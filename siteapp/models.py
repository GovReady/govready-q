from django.db import models, transaction
from django.utils import timezone
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from jsonfield import JSONField

from .betteruser import UserBase, UserManagerBase
from questions import Module


class UserManager(UserManagerBase):
    def _get_user_class(self):
        return User

class User(UserBase):
    objects = UserManager()

    def __str__(self):
        from guidedmodules.models import TaskAnswer
        name = TaskAnswer.objects.filter(
            question__task=self.get_settings_task(),
            question__question_id="name").first()
        if name:
            return name.value #+ " <" + self.email + ">"
        else:
            return self.email

    def get_settings_task(self):
        from guidedmodules.models import Task
        return Task.objects.filter(
            editor=self,
            project=None,
            module_id="account_settings").first()

    def render_context_dict(self):
        return {
            "id": self.id,
            "name": str(self),
        }

class Project(models.Model):
    title = models.CharField(max_length=256, help_text="The title of this Project.")
    notes = models.TextField(blank=True, help_text="Notes about this Project for Project members.")

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    extra = JSONField(blank=True, help_text="Additional information stored with this object.")

    def __str__(self):
        # For the admin.
        return self.title + " [" + self.get_owner_domains() + "]"

    def __repr__(self):
        # For debugging.
        return "<Project %d %s>" % (self.id, self.title[0:30])

    def get_absolute_url(self):
        from django.utils.text import slugify
        return "/projects/%d/%s" % (self.id, slugify(self.title))

    def get_admins(self):
        return User.objects.filter(projectmembership__project=self, projectmembership__is_admin=True)

    def get_owner_domains(self):
        # Utility function for the admin/debugging to quickly see the domain
        # names in the email addresses of the admins of this project.
        return ", ".join(sorted(m.user.email.split("@", 1)[1] for m in ProjectMembership.objects.filter(project=self, is_admin=True)))

    def has_read_priv(self, user):
        # Who can see this project? Team members + anyone editing a task within
        # this project + anyone that's a guest in dicussion within this project.
        from guidedmodules.models import Task
        if ProjectMembership.objects.filter(project=self, user=user).exists():
            return True
        if Task.objects.filter(editor=user, project=self).exists():
            return True
        for d in self.get_discussions_in_project_as_guest(user):
            return True
        return False

    def get_discussions_in_project_as_guest(self, user):
        from discussion.models import Discussion
        for d in Discussion.objects.filter(external_participants=user):
            if d.attached_to.task.project == self:
                if not d.attached_to.task.deleted_at:
                    yield d
    
    def get_invitation_purpose(self, invitation):
        into_new_task_module_id = invitation.target_info.get('into_new_task_module_id')
        if into_new_task_module_id:
            return ("to edit a new module <%s>" % Module.load(into_new_task_module_id).title) \
                + (" and to join the project team" if invitation.into_project else "")
        elif invitation.target_info.get('what') == 'join-team':
            return "to join this project team"
        raise ValueError()

    def is_invitation_valid(self, invitation):
        # Invitations to create a new Task remain valid so long as the
        # inviting user is a member of the project.
        return ProjectMembership.objects.filter(project=self, user=invitation.from_user).exists()

    def accept_invitation(self, invitation, add_message):
        # Create a new Task for the user to begin a module.
        into_new_task_module_id = invitation.target_info.get('into_new_task_module_id')
        if into_new_task_module_id:
            from questions import Module
            from guidedmodules.models import Task
            m = Module.load(into_new_task_module_id)
            task = Task.objects.create(
                project=self,
                editor=invitation.accepted_user,
                module_id=into_new_task_module_id,
                title=m.title,
            )

            # update the target to point to the created Task so that
            # we don't lose track of it - it will be saved into inv
            # by the caller
            invitation.target = task

            task.invitation_history.add(invitation)
        
        else:
            raise ValueError()

    def get_invitation_redirect_url(self, invitation):
        # Just for joining a project. For accepting a task, the target
        # has been updated to that task.
        return "/"

class ProjectMembership(models.Model):
    project = models.ForeignKey(Project, related_name="members", help_text="The Project this is defining membership for.")
    user = models.ForeignKey(User, help_text="The user that is a member of the Project.")
    is_admin = models.BooleanField(default=False, help_text="Is the user an administrator of the Project?")
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        unique_together = [('project', 'user')]


class Invitation(models.Model):
    # who is sending the invitation
    from_user = models.ForeignKey(User, related_name="invitations_sent", help_text="The User who sent the invitation.")
    from_project = models.ForeignKey(Project, related_name="invitations_sent", help_text="The Project within which the invitation exists.")
    
    # what is the recipient being invited to?
    into_project = models.BooleanField(default=False, help_text="Whether the user being invited is being invited to join from_project.")
    target_content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    target_object_id = models.PositiveIntegerField()
    target = GenericForeignKey('target_content_type', 'target_object_id')
    target_info = JSONField(blank=True, help_text="Additional information about the target of the invitation.")

    # who is the recipient of the invitation?
    to_user = models.ForeignKey(User, related_name="invitations_received", blank=True, null=True, help_text="The user who the invitation was sent to, if to an existing user.")
    to_email = models.CharField(max_length=256, blank=True, null=True, help_text="The email address the invitation was sent to, if to a non-existing user.")

    # personalization
    text = models.TextField(blank=True, help_text="The personalized text of the invitation.")

    # what state is this invitation in?
    sent_at = models.DateTimeField(blank=True, null=True, help_text="If the invitation has been sent by email, when it was sent.")
    accepted_at = models.DateTimeField(blank=True, null=True, help_text="If the invitation has been accepted, when it was accepted.")
    revoked_at = models.DateTimeField(blank=True, null=True, help_text="If the invitation has been revoked, when it was revoked.")

    # what resulted from this invitation?
    accepted_user = models.ForeignKey(User, related_name="invitations_accepted", blank=True, null=True, help_text="The user that accepted the invitation (i.e. if the invitation was by email address and an account was created).")

    # random string to generate unique code for recipient
    email_invitation_code = models.CharField(max_length=64, blank=True, help_text="For emails, a unique verification code.")

    # bookkeeping
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    extra = JSONField(blank=True, help_text="Additional information stored with this object.")

    def __str__(self):
        # for the admin
        return "invitation from %s to %s %s on %s" % (
            self.from_user,
            self.to_display(),
            self.purpose(),
            self.created)

    @staticmethod
    def generate_email_invitation_code():
        import random, string
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(24))

    @staticmethod
    def form_context_dict(user, project):
        from guidedmodules.models import ProjectMembership
        return {
            "project_id": project.id,
            "project_title": project.title,
            "users": [{ "id": pm.user.id, "name": str(pm.user) } for pm in ProjectMembership.objects.filter(project=project).exclude(user=user)],
        }

    def to_display(self):
        return str(self.to_user) if self.to_user else self.to_email

    def purpose(self):
        return self.target.get_invitation_purpose(self)

    def get_acceptance_url(self):
        from django.core.urlresolvers import reverse
        return settings.SITE_ROOT_URL \
            + reverse('accept_invitation', kwargs={'code': self.email_invitation_code})

    def send(self):
        # Send and mark as sent.
        from htmlemailer import send_mail
        send_mail(
            "email/invitation",
            "GovReady Q <q@mg.govready.com>",
            [self.to_user.email if self.to_user else self.to_email],
            {
                'invitation': self,
            }
        )
        Invitation.objects.filter(id=self.id).update(sent_at=timezone.now())

    def is_expired(self):
        # Return true if there is any reason why this invitation cannot be
        # accepted.

        if self.revoked_at:
            return True

        from datetime import timedelta
        if self.sent_at and timezone.now() > (self.sent_at + timedelta(days=10)):
            return True

        if not self.target.is_invitation_valid(self):
            return True

        return False
    is_expired.boolean = True

    def get_redirect_url(self):
        return self.target.get_invitation_redirect_url(self)

