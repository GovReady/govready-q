from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils import timezone
from jsonfield import JSONField
from siteapp.models import User
from .validators import validate_file_extension


class Discussion(models.Model):
    organization = models.ForeignKey('siteapp.Organization', related_name="discussions", on_delete=models.CASCADE, help_text="The Organization that this Discussion belongs to.")

    attached_to_content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    attached_to_object_id = models.PositiveIntegerField()
    attached_to = GenericForeignKey('attached_to_content_type', 'attached_to_object_id')

    guests = models.ManyToManyField(User, related_name="guest_in_discussions", blank=True, help_text="Additional Users who are participating in this chat, besides those that are implicit discussion members via the Discussion's attached_to object.")

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    extra = JSONField(blank=True, help_text="Additional information stored with this object.")

    class Meta:
      unique_together = ('attached_to_content_type', 'attached_to_object_id')

    @staticmethod
    def get_for(org, object, create=False, must_exist=False):
        content_type = ContentType.objects.get_for_model(object)
        if create:
            return Discussion.objects.get_or_create(organization=org, attached_to_content_type=content_type, attached_to_object_id=object.id)[0]
        elif not must_exist:
            return Discussion.objects.filter(attached_to_content_type=content_type, attached_to_object_id=object.id).first()
        else:
            return Discussion.objects.get(attached_to_content_type=content_type, attached_to_object_id=object.id)

    @staticmethod
    def get_for_all(objects):
        if objects.count() == 0:
            return Discussion.objects.none() # empty QuerySet
        content_type = ContentType.objects.get_for_model(objects.first())
        return Discussion.objects.filter(attached_to_content_type=content_type, attached_to_object_id__in=objects)

    def __str__(self):
        # for the admin, notification strings
        return self.title

    @property
    def attached_to_obj(self):
        # Cache .attached_to.
        if not hasattr(self, '_attached_to'):
            self._attached_to = self.attached_to
        return self._attached_to

    def get_absolute_url(self):
        if self.attached_to_obj is None:
            # Dangling!
            return ""
        return self.attached_to_obj.get_absolute_url() + "#discussion"

    @property
    def title(self):
        if self.attached_to_obj is not None:
            return self.attached_to_obj.title
        else:
            # Dangling - because it's a generic relation, there is no
            # delete protection and attached_to can get reset to None.
            return "<Deleted Discussion>"

    def is_participant(self, user):
        # No one is a participant of a discussion attached to (a question of) a deleted Task.
        if self.attached_to_obj is not None and self.attached_to_obj.is_discussion_deleted():
            return False
        return user in self.get_all_participants()

    def get_all_participants(self):
        # Because get_discussion_participants uses distinct, self.guests must too
        participants = self.guests.all().distinct()
        if self.attached_to_obj is not None:
            participants = (participants | self.attached_to_obj.get_discussion_participants()).distinct()
        return participants

    ##

    def render_context_dict(self, user, comments_since=0, parent_events_since=0):
        # Build the event history...
        events = []

        # From the object that this discussion is attached to...
        if self.attached_to_obj is not None:
            events.extend(self.attached_to_obj.get_discussion_interleaved_events(parent_events_since))

        # And from the comments.
        comments = list(self.comments
            .select_related('user')
            .filter(
                id__gt=comments_since,
                deleted=False,
                draft=False))

        # Speed up rendering by allowing Discussion-level data to be cached on the
        # Discussion instance.
        for c in comments: c.discussion = self

        # Batch load user information. For the user's own draft, load the requesting user's info too.
        # Don't use a set to uniquify Users since the comments may have different User instances and
        # we want to fill in info for all of them.
        User.preload_profiles([ c.user for c in comments ] + [ user ])

        # Add.
        events.extend([
            comment.render_context_dict(user)
            for comment in comments
        ])

        # Sort by date, since we are interleaving two sources of events.
        events.sort(key = lambda item : item["date_posix"])

        # Is there a draft in progress?
        draft = None
        if user:
            draft = self.comments.filter(user=user, draft=True).first()
            if draft:
                draft.user = user # reuse instance for caching via User.preload_profiles
                draft.discussion = self # reuse instance for caching
                draft = draft.render_context_dict(user)

        # Get the initial state of the discussion to populate the HTML.
        return {
            "status": "ok",
            "discussion": {
                "id": self.id,
                "title": self.title,
                "project": self.attached_to_obj.get_project_context_dict() if self.attached_to_obj is not None else None,
                "can_invite": self.can_invite_guests(user),
                "can_comment": self.can_comment(user),
            },
            "guests": [ user.render_context_dict() for user in self.guests.all() ],
            "events": events,
            "autocomplete": self.get_autocompletes(user),
            "draft": draft,
        }

    ##

    def post_comment(self, user, text, post_method, is_draft=False):
        # Does user have write privs?
        if not self.is_participant(user):
            raise ValueError("No access.")

        # Validate. Allow empty drafts so attachments can attach to them.
        if not is_draft:
            text = text.rstrip() # don't lstrip because markdown is sensitive to initial whitespace
            if text.strip() == "":
                raise ValueError("No comment entered.")

        # Save comment.
        comment = Comment.objects.create(
            discussion=self,
            user=user,
            draft=is_draft,
            text=text,
            extra={
                "post_method": post_method,
            }
            )

        # If not a draft...
        if not is_draft:
            comment._on_published()

        return comment

    ##

    def is_public(self):
        return getattr(self.attached_to_obj, 'is_discussion_public', lambda : False)

    def can_comment(self, user):
        return user is not None and self.is_participant(user)

    def can_invite_guests(self, user):
        if self.attached_to_obj is None: return False
        return self.attached_to_obj.can_invite_guests(user)

    def get_invitation_verb_inf(self, invitation):
        return "to join the discussion"

    def get_invitation_verb_past(self, invitation):
        return "joined the discussion"

    def is_invitation_valid(self, invitation):
        # Invitation remains valid only if the user that sent it is still
        # able to invite guests.
        return self.can_invite_guests(invitation.from_user)

    def accept_invitation(self, invitation, add_message):
        if self.is_participant(invitation.accepted_user):
            # user is already a participant --- possibly because they were just invited
            # and now added into the project, which gives them access to the discussion
            # --- so just redirect to it.
            return
        else:
            # add the user to the guests list for the discussion. 
            self.guests.add(invitation.accepted_user)
            add_message('You are now a participant in the discussion on %s.' % self.title)

    def get_invitation_redirect_url(self, invitation):
        if self.attached_to_obj is None: return None
        return self.attached_to_obj.get_absolute_url()

    @property
    def supress_link_from_notifications(self):
        # Dangling - because it's a generic relation, there is no
        # delete protection and attached_to can get reset to None.
        return self.attached_to_obj is None

    def get_notification_watchers(self):
        if self.attached_to_obj is None or self.attached_to_obj.is_discussion_deleted():
            return set()
        return set(self.attached_to_obj.get_notification_watchers()) \
            | set(self.guests.all())

    def get_notification_link(self, notification):
        if notification.data and notification.data.get("comment_id"):
            return self.attached_to_obj.get_absolute_url() + "#discussion-comment-" + str(notification.data.get("comment_id"))
        return None # fall back to default behavior

    def post_notification_reply(self, notification, user, message):
        # This is called via incoming mail routing when a user replies to a notification
        # email about this discussion. Ignore any problems because we don't have a way
        # to alert the sender of the problem.
        self.post_comment(user, message, "email")

    ##

    def get_autocompletes(self, user):
        # When typing in a comment, what autocompletes are available to this user?
        # Ensure the user is a participant of the discussion. Cache this on the
        # instance since when we render the Discussion event history we fetch this
        # once for each comment we render.
        if hasattr(self, '_get_autocompletes'): return self._get_autocompletes
        if self.attached_to_obj is None or not self.is_participant(user):
            self._get_autocompletes = []
        else:
            self._get_autocompletes = self.attached_to_obj.get_discussion_autocompletes(self)
        return self._get_autocompletes

class Comment(models.Model):
    discussion = models.ForeignKey(Discussion, related_name="comments", on_delete=models.CASCADE, help_text="The Discussion that this comment is attached to.")
    replies_to = models.ForeignKey('self', blank=True, null=True, related_name="replies", on_delete=models.CASCADE, help_text="If this is a reply to a Comment, the Comment that this is in reply to.")
    user = models.ForeignKey(User, on_delete=models.PROTECT, help_text="The user making a comment.")

    emojis = models.CharField(max_length=256, blank=True, null=True, help_text="A comma-separated list of emoji names that the user is reacting with.")
    text = models.TextField(blank=True, help_text="The text of the user's comment.")
    proposed_answer = JSONField(blank=True, null=True, help_text="A proposed answer to the question that this discussion is about.")
    draft = models.BooleanField(default=False, help_text="Set to true if the comment is a draft.")
    deleted = models.BooleanField(default=False, help_text="Set to true if the comment has been 'deleted'.")

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    extra = JSONField(blank=True, help_text="Additional information stored with this object.")

    class Meta:
        index_together = [
            ('discussion', 'user'),
        ]

    def __str__(self):
        # To see the comment text
        return self.text

    # auth
    def can_see(self, user):
        if self.deleted or self.draft:
            return False
        return self.discussion.is_public() or self.discussion.is_participant(user)

    def can_edit(self, user):
        # If the comment has been deleted, it becomes locked for editing. This
        # shouldn't have a user-visible effect, since no one can see it anyway.
        if self.deleted:
            return False

        # Is the user permitted to edit this comment? If a user is no longer
        # a participant in a discussion, they can't edit their comments in that
        # discussion.
        return self.user == user and self.discussion.is_participant(user)

    def can_delete(self, user):
        return self.can_edit(user)

    # draft / publish / update

    def publish(self):
        if not self.draft: raise Exception("I'm not a draft.")
        self._on_published()

    def _on_published(self):
        # Mark as not a draft.
        self.draft = False

        # Reset the creation date to the moment it's published.
        self.created = timezone.now()
        # Save.
        self.save()

        # Kick the attached object.
        if hasattr(self.discussion.attached_to_obj, 'on_discussion_comment'):
            self.discussion.attached_to_obj.on_discussion_comment(self)

        # Issue a notification to anyone watching the discussion
        # via discussion.get_notification_watchers() except to
        # anyone @-mentioned because they'll get a different
        # notification.
        if self.draft: raise Exception("I'm still a draft.")
        from siteapp.views import issue_notification
        _, mentioned_users = match_autocompletes(self.text, self.discussion.get_autocompletes(self.user))
        issue_notification(
            self.user,
            "commented on",
            self.discussion,
            recipients=self.discussion.get_notification_watchers() - mentioned_users,
            description=self.text,
            comment_id=self.id)

        # Issue a notification to anyone @-mentioned in the comment
        # that is already a discussion participant.
        discussion_participants = set(self.discussion.get_all_participants())
        issue_notification(
            self.user,
            "mentioned you in a comment on",
            self.discussion,
            recipients=mentioned_users & discussion_participants,
            description=self.text,
            comment_id=self.id)

        # Send invitations to anyone @-mentioned who is not yet a participant
        # in the discussion.
        from siteapp.models import Invitation

        for user in mentioned_users - discussion_participants:
            inv = Invitation.objects.create(
                from_user=self.user,
                from_project=self.discussion.attached_to_obj.task.project, # TODO: Breaks abstraction, assumes attached_to => TaskAnswer.
                target=self.discussion,
                target_info={ "what": "invite-guest" },
                to_user=user,
                text="{} mentioned you in a discussion:\n\n{}".format(self.user, self.text),
            )
            inv.send()

        # Let the owner object of the discussion know that a comment was left.
        if hasattr(self.discussion.attached_to_obj, 'on_discussion_comment'):
            self.discussion.attached_to_obj.on_discussion_comment(self)

    def push_history(self, field):
        if not isinstance(self.extra, dict):
            self.extra = { }
        self.extra.setdefault("history", []).append({
            "when": timezone.now().isoformat(), # make JSON-serializable
            "previous-" + field: getattr(self, field),
        })

    def get_emoji_list(self):
        if self.emojis in (None, ""): return set()
        return set(self.emojis.split(","))

    # render

    def render_context_dict(self, whose_asking):
        if self.deleted:
            raise ValueError()
        if self.draft and whose_asking != self.user:
            raise ValueError()

        # Render for a notification.
        def notification_text():
            if self.text:
                return str(self.user) + ": " + self.text
            elif self.emojis:
                return str(self.user) + " reacted with " + self.emojis + "."
            else:
                return None

        def get_user_role():
            ret = self.discussion.attached_to_obj.get_user_role(self.user)
            if ret is not None:
                return ret
            if self.user in self.discussion.guests.all():
                return "guest"
            return "former participant"

        return {
            "type": "comment",
            "id": self.id,
            "can_edit": self.can_edit(whose_asking),
            "can_delete": self.can_delete(whose_asking),
            "replies_to": self.replies_to_id,
            "user": self.user.render_context_dict(),
            "user_role": get_user_role(),
            "date_relative": reldate(self.created, timezone.now()) + " ago",
            "date_posix": self.created.timestamp(), # POSIX time, seconds since the epoch, in UTC
            "text": self.text,
            "text_rendered": render_text(self.text, autocompletes=self.discussion.get_autocompletes(whose_asking), comment=self),
            "notification_text": notification_text(),
            "emojis": self.emojis.split(",") if self.emojis else None,
        }

class Attachment(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, help_text="The user uploading this attachment.")
    comment = models.ForeignKey(Comment, blank=True, null=True, related_name="attachments", on_delete=models.CASCADE, help_text="The Comment that this Attachment is attached to. Null when the file has been uploaded before the Comment has been saved.")
    file = models.FileField(upload_to='discussion/attachments', validators=[validate_file_extension], help_text="The attached file.")

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    extra = JSONField(blank=True, help_text="Additional information stored with this object.")

    def get_absolute_url(self):
        return reverse("discussion-attachment", args=[self.id])

def reldate(date, ref=None):
    import dateutil.relativedelta
    rd = dateutil.relativedelta.relativedelta(ref or timezone.now(), date)
    def r(n, unit):
        return str(n) + " " + unit + ("s" if n != 1 else "")
    def c(*rs):
        return ", ".join(r(*s) for s in rs)
    if rd.months >= 1: return c((rd.months, "month"), (rd.days, "day"))
    if rd.days >= 7: return c((rd.days, "day"),)
    if rd.days >= 1: return c((rd.days, "day"), (rd.hours, "hour"))
    if rd.hours >= 1: return c((rd.hours, "hour"), (rd.minutes, "minute"))
    if rd.minutes >= 1: return c((rd.minutes, "minute"),)
    return c((rd.seconds, "second"),)

def render_text(text, autocompletes=None, comment=None, unwrap_p=False):
    # Render comment text into HTML.

    import re

    # Put @-mentions in bold.
    if autocompletes:
        text, _ = match_autocompletes(text, autocompletes,
            lambda text : "**" + text + "**")

    # Rewrite attachment:### URLs.
    if comment is not None:
        def get_attachment_url(attachment_id):
            try:
                return Attachment.objects.get(id=attachment_id.group(1)).get_absolute_url()
            except:
                return "about:blank"
        text = re.sub("(?<=\()attachment:(\d+)(?=\))", get_attachment_url, text)

    # Render to HTML as if CommonMark.
    import commonmark
    parsed = commonmark.Parser().parse(text)
    text = commonmark.HtmlRenderer({ "safe": True }).render(parsed)

    if unwrap_p:
        # If it's a single paragraph, unwrap it.
        text = re.sub(r"^<p>(.*)</p>$", r"\1", text)

    return text

def match_autocompletes(text, autocompletes, replace_mentions=None):
    import re
    from siteapp.models import User

    # Make a big regex for all mentions of all autocompletable things.
    # Since we're matching against Markdown, allow the prefix character
    # (@ or #) to be preceded by a backslash, since punctuation can
    # be escaped. If this Markdown came from a rich text editor, we
    # might have escapes in funny places.
    pattern = "|".join(
        r"\\?" + char + "(" + "|".join(
            re.escape(item["tag"])
            for item in items
        ) + ")"
        for char, items in autocompletes.items()
        if len(items) > 0
    )
    if pattern == "":
        return (text, set())

    # Wrap in a lookbehind and a lookahead to not match if surrounded
    # by word-ish characters.
    pattern = r"(?<!\w)" + pattern + r"(?!\w)"

    # Create a reverse-mapping.
    reverse_mapping = { }
    for char, items in autocompletes.items():
        for item in items:
            reverse_mapping[(char, item['tag'])] = item

    # Find what was mentioned.
    mentioned_users = set()
    def replace_func(m):
        char, tag = (m.group(0)[:1], m.group(0)[1:])
        if char == "\\": # was escaped
            char, tag = (m.group(0)[1:2], m.group(0)[2:])
        item = reverse_mapping[(char, tag)]
        if item.get("user_id"):
            user = User.objects.get(id=item["user_id"])
            mentioned_users.add(user)
            if replace_mentions:
                return replace_mentions(m.group(0))
        return m.group(0)
    text = re.sub(pattern, replace_func, text)

    return (text, mentioned_users)
