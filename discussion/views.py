from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone

from .models import Discussion, Comment
from guidedmodules.models import ModuleQuestion, Task, TaskAnswer
from siteapp.models import Project, ProjectMembership

@login_required
def start_a_discussion(request):
    # This view function creates a discussion, or returns an existing one.

    # Validate and retreive the Task and ModuleQuestion that the discussion
    # is to be attached to.
    task = get_object_or_404(Task, id=request.POST['task'])
    q = get_object_or_404(ModuleQuestion, id=request.POST['question'])

    # The user may not have permission to create - only to get.

    tq_filter = { "task": task, "question": q }
    tq = TaskAnswer.objects.filter(**tq_filter).first()
    if not tq:
        # Validate user can create discussion. Any user who can read the task can start
        # a discussion.
        if not task.has_read_priv(request.user):
            return JsonResponse({ "status": "error", "message": "You do not have permission!" })

        # Get the TaskAnswer for this task. It may not exist yet.
        tq, isnew = TaskAnswer.objects.get_or_create(**tq_filter)

    discussion = Discussion.get_for(request.organization, tq)
    if not discussion:
        # Validate user can create discussion.
        if not task.has_read_priv(request.user):
            return JsonResponse({ "status": "error", "message": "You do not have permission!" })

        # Get the Discussion.
        discussion = Discussion.get_for(request.organization, tq, create=True)

    # Build the event history.
    events = []
    events.extend([
        event
        for event in tq.get_history()
        if event["date_posix"] > float(request.POST.get("event_since", "0"))
    ])
    events.extend([
        comment.render_context_dict()
        for comment in discussion.comments.filter(
            id__gt=request.POST.get("comment_since", "0"),
            deleted=False)
    ])
    events.sort(key = lambda item : item["date_posix"])

    # Get the initial state of the discussion to populate the HTML.
    return JsonResponse({
        "status": "ok",
        "discussion": {
            "id": discussion.id,
            "title": discussion.title,
            "project": {
                "id": discussion.attached_to.project.id,
                "title": discussion.attached_to.project.title,
            },
            "can_invite": discussion.can_invite_guests(request.user),
        },
        "guests": [ user.render_context_dict(request.organization) for user in discussion.guests.all() ],
        "events": events,
        "autocomplete": discussion.get_autocompletes(request.user),
    })

@login_required
def submit_discussion_comment(request):
    discussion = get_object_or_404(Discussion, id=request.POST['discussion'], organization=request.organization)

    # Does user have write privs?
    if not discussion.is_participant(request.user):
        return JsonResponse({ "status": "error", "message": "No access."})

    # Validate.
    text = request.POST.get("text", "").strip()
    if text == "":
        return JsonResponse({ "status": "error", "message": "No comment entered."})

    # Save comment.
    comment = Comment.objects.create(
        discussion=discussion,
        user=request.user,
        text=text
        )

    # Issue a notification.
    from siteapp.views import issue_notification
    from django.utils.text import Truncator
    issue_notification(
        request.user,
        "commented on",
        discussion,
        description="“" + Truncator(text).words(15) + "”")

    # Return the comment for display.
    return JsonResponse(comment.render_context_dict())

@login_required
def edit_discussion_comment(request):
    # get object
    comment = get_object_or_404(Comment, id=request.POST['id'], discussion__organization=request.organization)

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

    # return new comment info
    return JsonResponse(comment.render_context_dict())

@login_required
def delete_discussion_comment(request):
    # get object
    comment = get_object_or_404(Comment, id=request.POST['id'], discussion__organization=request.organization)

    # can edit? must still be a participant of the discussion, to
    # prevent editing things that you are no longer able to see
    if not comment.can_edit(request.user):
        return HttpResponseForbidden()

    # mark deleted
    comment.deleted = True
    comment.save()

    # return new comment info
    return JsonResponse({ "status": "ok" })

@login_required
def save_reaction(request):
    # get comment that is being reacted *to*
    comment = get_object_or_404(Comment, id=request.POST['id'], discussion__organization=request.organization)

    # can see it?
    if not comment.can_see(request.user):
        return HttpResponseForbidden()

    # get the Comment that *reacts* to it
    comment, is_new = Comment.objects.get_or_create(
        discussion=comment.discussion,
        replies_to=comment,
        user=request.user,
    )

    # record edit history
    comment.push_history('emojis')

    # edit
    comment.emojis = request.POST['emojis']

    # save
    comment.save()

    # return new comment info
    return JsonResponse(comment.render_context_dict())
