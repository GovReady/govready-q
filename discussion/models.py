from django.db import models, transaction
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.conf import settings

import re

from jsonfield import JSONField

from siteapp.models import User

class Discussion(models.Model):
    organization = models.ForeignKey('siteapp.Organization', related_name="discussions", help_text="The Organization that this Discussion belongs to.")

    attached_to_content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    attached_to_object_id = models.PositiveIntegerField()
    attached_to = GenericForeignKey('attached_to_content_type', 'attached_to_object_id')

    guests = models.ManyToManyField(User, blank=True, help_text="Additional Users who are participating in this chat, besides those that are implicit discussion members via the Discussion's attached_to object.")

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    extra = JSONField(blank=True, help_text="Additional information stored with this object.")

    class Meta:
      unique_together = (('attached_to_content_type', 'attached_to_object_id'))

    @staticmethod
    def get_for(org, object, create=False, must_exist=False):
        content_type = ContentType.objects.get_for_model(object)
        if create:
            return Discussion.objects.get_or_create(organization=org, attached_to_content_type=content_type, attached_to_object_id=object.id)[0]
        elif not must_exist:
            return Discussion.objects.filter(organization=org, attached_to_content_type=content_type, attached_to_object_id=object.id).first()
        else:
            return Discussion.objects.get(organization=org, attached_to_content_type=content_type, attached_to_object_id=object.id)

    def __str__(self):
        # for the admin, notification strings
        return self.title

    def get_absolute_url(self):
        return self.attached_to.get_absolute_url() + "#discussion"

    @property
    def title(self):
        if self.attached_to is not None:
            return self.attached_to.title
        else:
            # Dangling - because it's a generic relation, there is no
            # delete protection and attached_to can get reset to None.
            return "<Deleted Discussion>"

    def is_participant(self, user):
        # No one is a participant of a dicussion attached to (a question
        # of) a deleted Task.
        if self.attached_to.is_discussion_deleted():
            return False
        return user in self.get_all_participants()

    def get_all_participants(self):
        return (
            self.attached_to.get_discussion_participants()
            | self.guests.all().distinct() # because get_discussion_participants uses distinct, this one must too
            ).distinct()

    ##

    def render_context_dict(self, user, comments_since=0, parent_events_since=0):
        # Build the event history.
        events = []
        events.extend(self.attached_to.get_discussion_interleaved_events(parent_events_since))
        events.extend([
            comment.render_context_dict(user)
            for comment in self.comments.filter(
                id__gt=comments_since,
                deleted=False)
        ])
        events.sort(key = lambda item : item["date_posix"])

        # Get the initial state of the discussion to populate the HTML.
        return {
            "status": "ok",
            "discussion": {
                "id": self.id,
                "title": self.title,
                "project": self.attached_to.get_project_context_dict(),
                "can_invite": self.can_invite_guests(user),
            },
            "guests": [ user.render_context_dict(self.organization) for user in self.guests.all() ],
            "events": events,
            "autocomplete": self.get_autocompletes(user),
        }

    ##

    def post_comment(self, user, text, post_method):
        # Does user have write privs?
        if not self.is_participant(user):
            raise ValueError("No access.")

        # Validate.
        text = text.strip()
        if text == "":
            raise ValueError("No comment entered.")

        # Save comment.
        comment = Comment.objects.create(
            discussion=self,
            user=user,
            text=text,
            extra={
                "post_method": post_method,
            }
            )

        # Finish attachments. Since attachments are created before comments
        # are saved, they must be associated with the Comment once it is saved.
        for attachment_id in re.findall("\(attachment:(\d+)\)", text):
            attachment = Attachment.objects.filter(id=attachment_id, user=user).first()
            if attachment:
                # Silently ignore any invalid attachment IDs.
                attachment.comment = comment
                attachment.save()

        # Issue a notification to anyone watching the discussion
        # via discussion.get_notification_watchers() except to
        # anyone @-mentioned because they'll get a different
        # notification.
        from siteapp.views import issue_notification
        _, mentioned_users = match_autocompletes(text, self.get_autocompletes(user))
        issue_notification(
            user,
            "commented on",
            self,
            recipients=self.get_notification_watchers() - mentioned_users,
            description=text,
            comment_id=comment.id)

        # Issue a notification to anyone @-mentioned in the comment.
        # Compile a big regex for all usernames.
        issue_notification(
            user,
            "mentioned you in a comment on",
            self,
            recipients=mentioned_users,
            description=text,
            comment_id=comment.id)

        return comment

    ##

    def can_invite_guests(self, user):
        return self.attached_to.can_invite_guests(user)

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
        return self.attached_to.get_absolute_url()

    @property
    def supress_link_from_notifications(self):
        # Dangling - because it's a generic relation, there is no
        # delete protection and attached_to can get reset to None.
        return self.attached_to is None

    def get_notification_watchers(self):
        if self.attached_to.is_discussion_deleted():
            return set()
        return set(self.attached_to.get_notification_watchers()) \
            | set(self.guests.all())

    def get_notification_link(self, notification):
        if notification.data and notification.data.get("comment_id"):
            return self.attached_to.get_absolute_url() + "#discussion-comment-" + str(notification.data.get("comment_id"))
        return None # fall back to default behavior

    def post_notification_reply(self, notification, user, message):
        # This is called via incoming mail routing when a user replies to a notification
        # email about this discussion. Ignore any problems because we don't have a way
        # to alert the sender of the problem.
        self.post_comment(user, message, "email")

    ##

    def get_autocompletes(self, user):
        # When typing in a comment, what autocompletes are available to this user?
        # Ensure the user is a participant of the discussion.
        if not self.is_participant(user):
            return []
        return self.attached_to.get_discussion_autocompletes(self.organization)

class Comment(models.Model):
    discussion = models.ForeignKey(Discussion, related_name="comments", help_text="The Discussion that this comment is attached to.")
    replies_to = models.ForeignKey('self', blank=True, null=True, related_name="replies", help_text="If this is a reply to a Comment, the Comment that this is in reply to.")
    user = models.ForeignKey(User, help_text="The user making a comment.")

    emojis = models.CharField(max_length=256, blank=True, null=True, help_text="A comma-separated list of emoji names that the user is reacting with.")
    text = models.TextField(blank=True, help_text="The text of the user's comment.")
    proposed_answer = JSONField(blank=True, null=True, help_text="A proposed answer to the question that this discussion is about.")
    deleted = models.BooleanField(default=False, help_text="Set to true if the comment has been 'deleted'.")

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    extra = JSONField(blank=True, help_text="Additional information stored with this object.")

    class Meta:
        index_together = [
            ('discussion', 'user'),
        ]

    def can_see(self, user):
        if self.deleted:
            return False
        return self.discussion.is_participant(user)

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
        return self.can_edit(user) and (not isinstance(self.extra, dict) or self.extra.get("deletable", True))

    def push_history(self, field):
        if not isinstance(self.extra, dict):
            self.extra = { }
        self.extra.setdefault("history", []).append({
            "when": timezone.now().isoformat(), # make JSON-serializable
            "previous-" + field: getattr(self, field),
        })

    def render_context_dict(self, whose_asking):
        if self.deleted:
            raise ValueError()

        # Render for a notification.
        if self.text:
            notification_text = str(self.user) + ": " + self.text
        elif self.emojis:
            notification_text = str(self.user) + " reacted with " + self.emojis + "."
        else:
            notification_text = None

        def get_user_role():
            ret = self.discussion.attached_to.get_user_role(self.user)
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
            "user": self.user.render_context_dict(self.discussion.organization),
            "user_role": get_user_role(),
            "date_relative": reldate(self.created, timezone.now()) + " ago",
            "date_posix": self.created.timestamp(), # POSIX time, seconds since the epoch, in UTC
            "text": self.text,
            "text_rendered": render_text(self.text, autocompletes=self.discussion.get_autocompletes(whose_asking), comment=self),
            "notification_text": notification_text,
            "emojis": self.emojis.split(",") if self.emojis else None,
        }

class Attachment(models.Model):
    discussion = models.ForeignKey(Discussion, related_name="attachments", help_text="The Discussion that this Attachment is attached to.")
    user = models.ForeignKey(User, help_text="The user uploading this attachment.")
    comment = models.ForeignKey(Comment, blank=True, null=True, related_name="attachments", help_text="The Comment that this Attachment is attached to. Null when the file has been uploaded before the Comment has been saved.")
    file = models.FileField(upload_to='discussion/attachments', help_text="The attached file.")

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    extra = JSONField(blank=True, help_text="Additional information stored with this object.")

    def get_absolute_url(self):
        return self.file.url

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
    def get_attachment_url(attachment_id):
        try:
            attachment = Attachment.objects.filter(id=int(attachment_id.group(1)), comment=comment).first()
            if attachment:
                return attachment.get_absolute_url()
        except ValueError:
            pass
        return attachment_id.group(0)
    text = re.sub("(?<=\()attachment:(\d+)(?=\))", get_attachment_url, text)

    # Render to HTML as if CommonMark.
    import CommonMark
    parsed = CommonMark.Parser().parse(text)
    text = CommonMark.HtmlRenderer({ "safe": True }).render(parsed)

    if unwrap_p:
        # If it's a single paragraph, unwrap it.
        text = re.sub(r"^<p>(.*)</p>$", r"\1", text)

    return text


def match_autocompletes(text, autocompletes, replace_mentions=None):
    import re
    from siteapp.models import User

    # Make a big regex for all mentions of all autocompletable things.
    pattern = "|".join(
        "(" + char + ")(" + "|".join(
            re.escape(item["tag"])
            for item in items
        ) + ")"
        for char, items in autocompletes.items()
    )

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
        item = reverse_mapping[(char, tag)]
        if item.get("user_id"):
            user = User.objects.get(id=item["user_id"])
            mentioned_users.add(user)
            if replace_mentions:
                return replace_mentions(char+tag)
        return m.group(0)
    text = re.sub(pattern, replace_func, text)

    return (text, mentioned_users)
