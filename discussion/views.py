import logging
import structlog
from structlog import get_logger

from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
import sys

from siteapp.settings import DATA_UPLOAD_MAX_MEMORY_SIZE
from .models import Discussion, Comment, Attachment
from .validators import validate_file_extension

logging.basicConfig()
logger = get_logger()

@login_required
@transaction.atomic
def update_discussion_comment_draft(request):
    # Get the discussion object.
    discussion = get_object_or_404(Discussion, id=request.POST['discussion'])

    # Get the text.
    text = request.POST.get("text", "").rstrip()

    comment = None
    if request.POST.get('draft', '') != '':
        # Update existing draft. It's possible the client-side draft
        # ID migth become stale if another browser submits the same
        # draft.
        try:
            comment = discussion.comments.get(id=request.POST['draft'], user=request.user, draft=True)
        except:
            logger.error(
                event="update_discussion_comment_draft",
                object={"object": "comment", "id": request.POST['draft']},
                user={"id": request.user.id, "username": request.user.username}
            )
        else:
            comment.text = text
            comment.save()

    if comment is None:
        # Create a new draft.
        comment = discussion.post_comment(
            request.user, text, "web",
            is_draft=True)

    # Return the comment's id and rendered text for displaying a preview.
    return JsonResponse(comment.render_context_dict(request.user))

@login_required
@transaction.atomic
def submit_discussion_comment(request):
    # Get the discussion object.
    discussion = get_object_or_404(Discussion, id=request.POST['discussion'])
    if not discussion.can_comment(request.user):
        return HttpResponseForbidden("You do not have permission to post to this discussion.")

    # Get the Comment draft.
    try:
        comment = discussion.comments.get(id=request.POST['draft'], user=request.user)
    except:
        return JsonResponse({ "status": "error", "message": "No draft." })

    if not comment.draft:
        return JsonResponse({ "status": "error", "message": "It looks like the comment was already submitted from another browser session." })
    # Publish it.
    comment.publish()

    # Return the comment for display.
    return JsonResponse(comment.render_context_dict(request.user))

@login_required
def edit_discussion_comment(request):
    # get object
    comment = get_object_or_404(Comment, id=request.POST['id'])

    # can edit? must still be a participant of the discussion, to
    # prevent editing things that you are no longer able to see
    if not comment.can_edit(request.user):
        return HttpResponseForbidden()

    # record edit history
    comment.push_history('text')

    # edit
    comment.text = request.POST['text']

    # save
    comment.save()

    # Kick the attached object.
    if hasattr(comment.discussion.attached_to, 'on_discussion_comment_edited'):
        comment.discussion.attached_to.on_discussion_comment_edited(comment)

    # return new comment info
    return JsonResponse(comment.render_context_dict(request.user))

@login_required
def delete_discussion_comment(request):
    # get object
    comment = get_object_or_404(Comment, id=request.POST['id'])

    # can delete? must still be a participant of the discussion, to
    # prevent editing things that you are no longer able to see
    if not comment.can_delete(request.user):
        return HttpResponseForbidden()

    # mark deleted
    comment.deleted = True
    comment.save()

    # return new comment info
    return JsonResponse({ "status": "ok" })

@login_required
def save_reaction(request):
    # get comment that is being reacted *to*
    comment = get_object_or_404(Comment, id=request.POST['id'])

    # can see it?
    if not comment.can_see(request.user):
        return HttpResponseForbidden()

    # get the Comment that holds the reaction to it
    comment, is_new = Comment.objects.get_or_create(
        discussion=comment.discussion,
        replies_to=comment,
        user=request.user,
    )

    # get previous value
    old_value = comment.get_emoji_list()

    # record edit history
    comment.push_history('emojis')

    # edit
    comment.emojis = request.POST['emojis']

    # if there are changes...
    new_value = comment.get_emoji_list()
    if old_value != new_value:
        # save
        comment.save()

        # issue notification to the parent comment's author, unless it's
        # the user making the reaction
        if new_value - old_value:
            # There are new reactions.
            msg = "reacted " + ", ".join(sorted(new_value-old_value)) + " to"

            # There were also emojis un-reacted.
            if old_value - new_value:
                msg += " and removed their reaction " + ", ".join(sorted(old_value-new_value))
        elif old_value - new_value:
            # Emojis were removed (and nothing else).
            msg = "removed their reaction " + ", ".join(sorted(old_value-new_value)) + " to"
        from siteapp.views import issue_notification
        issue_notification(
            comment.user,
            msg,
            comment.discussion,
            recipients=[comment.replies_to.user],
            comment_id=comment.id)

    # return new comment info
    return JsonResponse(comment.render_context_dict(request.user))

@login_required
def poll_for_events(request):
    discussion = get_object_or_404(Discussion, id=request.POST['id'])
    if not discussion.is_participant(request.user):
        raise Http404()
    return JsonResponse(discussion.render_context_dict(
        request.user,
        request.POST.get("comment_since", "0"),
        request.POST.get("event_since", "0")
    ))

@login_required
@transaction.atomic
def create_attachments(request):
    # Get the Discussion.
    discussion = get_object_or_404(Discussion, id=request.POST['discussion'])
    if not discussion.is_participant(request.user):
        return HttpResponseForbidden()

    # Get the Comment draft.
    try:
        comment = discussion.comments.get(id=request.POST['draft'], user=request.user, draft=True)
    except:
        return JsonResponse({ "status": "error", "message": "No draft." })

    # The user is uploading one or more files.
    ret = { }
    for fn in request.FILES:
        # Validate before attachment object creation
        uploaded_file = request.FILES[fn]

        # 2.5MB
        if sys.getsizeof(uploaded_file) >= DATA_UPLOAD_MAX_MEMORY_SIZE:
            return JsonResponse(status=413, data={'status':'error','message': "413 Payload Too Large"})

        validation_result = validate_file_extension(uploaded_file)
        if validation_result != None:
            return validation_result

        attachment = Attachment.objects.create(
            comment=comment,
            user=request.user,
            file=request.FILES[fn]
        )

        # Get the dbstorage.models.StoredFile instance which holds
        # an auto-detected mime type. Use that to return whether
        # the attachment is an image or not.
        from dbstorage.models import StoredFile
        sf = StoredFile.objects.get(path=attachment.file.name)
        is_image = sf.mime_type and sf.mime_type.startswith("image/")

        ret[fn] = {
            "id": attachment.id,
            "url": settings.SITE_ROOT_URL + attachment.get_absolute_url(),
            "original_fn": request.FILES[fn].name,
            "is_image": is_image,
        }

    # Return a mapping from file field names in the upload to Attachment infos.
    return JsonResponse(ret)

def download_attachment(request, attachment_id):
    try:
        attachment = get_object_or_404(Attachment, id=attachment_id)
    except ValueError:
        raise Http404()
    if not attachment.comment.discussion.is_public() and not attachment.comment.discussion.is_participant(request.user):
        return HttpResponseForbidden()

    from dbstorage.views import get_file_content_view
    return get_file_content_view(request, attachment.file.name)
    