from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

from jsonfield import JSONField

class Project(models.Model):
    title = models.CharField(max_length=256, help_text="The title of this Project.")
    notes = models.TextField(blank=True, help_text="Notes about this Project for Project members.")

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    extra = JSONField(blank=True, help_text="Additional information stored with this object.")

    def get_absolute_url(self):
        from django.utils.text import slugify
        return "/tasks/projects/%d/%s" % (self.id, slugify(self.title))

class ProjectMembership(models.Model):
    project = models.ForeignKey(Project, related_name="members", help_text="The Project this is defining membership for.")
    user = models.ForeignKey(User, help_text="The user that is a member of the Project.")
    is_admin = models.BooleanField(default=False, help_text="Is the user an administrator of the Project?")
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
    	unique_together = [('project', 'user')]

class Task(models.Model):
    project = models.ForeignKey(Project, blank=True, null=True, help_text="The Project that this Task is a part of, or empty for Tasks that are just directly owned by the user.")
    user = models.ForeignKey(User, help_text="The user that is working on this task.")
    module_id = models.CharField(max_length=128, help_text="The ID of the module being completed.")

    title = models.CharField(max_length=256, help_text="The title of this Task. If the user is performing multiple tasks for the same module, this title would distiguish the tasks.")
    notes = models.TextField(blank=True, help_text="Notes set by the user about why they are completing this task.")

    requested_by = models.ForeignKey('guidedmodules.Task', blank=True, null=True, related_name='requests', help_text="The Task (and its user) which is requesting that this Task be completed, if applicable. Answers are inherited from this Task if there is no Answer for a particular question in this Task.")
    requestor_notes = models.TextField(blank=True, help_text="A message from the requesting user to the user of this Task.")

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    extra = JSONField(blank=True, help_text="Additional information stored with this object.")

    class Meta:
        index_together = [
            ('project', 'user', 'module_id'),
        ]

    @staticmethod
    def has_completed_task(user, module_id, project=None):
        task = Task.objects.filter(project=project, user=user, module_id="account_settings").first()
        if task is None:
            return False
        return task.is_finished()

    @staticmethod
    def get_task_for_module(user, module_id):
        # Gets a task given a module_id. Use only with system modules
        # where a user can only have one Task for the module.
        task, isnew = Task.objects.get_or_create(
            user=user,
            module_id=module_id)
        if isnew:
            task.title = task.load_module().title
            task.save()
        return task

    def get_absolute_url(self):
        from django.utils.text import slugify
        return "/tasks/%d/%s" % (self.id, slugify(self.title))

    def load_module(self):
        from questions import Module
        return Module.load(self.module_id)

    def get_answers_dict(self):
        answered = { }

        # If this Task was by invitation from another Task (of the same module),
        # use answers from the requesting Task as default answers for anything
        # not answered by this user.
        if self.requested_by:
            answered.update(self.requested_by.get_answers_dict())

        # Add in the answers this user actually answered.
        for q in self.answers.all():
            answered[q.question_id] = q.value

        return answered

    def is_finished(self):
        return self.load_module().next_question(self.get_answers_dict()) == None

    def get_status_display(self):
        if not self.is_finished():
            return "In Progress, last edit " + self.updated.strftime("%x %X")
        else:
            return "FInished on " + self.updated.strftime("%x %X")

    def get_output(self):
        return self.load_module().render_output(self.get_answers_dict())

class Answer(models.Model):
    task = models.ForeignKey(Task, related_name="answers", help_text="The Task that this Answer is for.")
    question_id = models.CharField(max_length=128, help_text="The ID of the question (with the Task's module) that this Answer answers.")

    value = JSONField(blank=True, help_text="The actual answer value for the Question, or None/null if the question is not really answered yet.")

    notes = models.TextField(blank=True, help_text="Notes entered by the user completing this Answer.")

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    extra = JSONField(blank=True, help_text="Additional information stored with this object.")

    class Meta:
        unique_together = [('task', 'question_id')]

class Comment(models.Model):
    user = models.ForeignKey(User, help_text="The user making a comment.")
    target = models.ForeignKey(Answer, help_text="The Answer that this comment is attached to.")

    emoji = models.CharField(max_length=64, blank=True, null=True, help_text="The name of an emoji that the user is reacting with.")
    text = models.TextField(blank=True, help_text="The text of the user's comment.")

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    extra = JSONField(blank=True, help_text="Additional information stored with this object.")

    class Meta:
        index_together = [
            ('user', 'target'),
        ]

class Invitation(models.Model):
    from_user = models.ForeignKey(User, related_name="invitations_sent", help_text="The user who sent the invitation.")
    from_task = models.ForeignKey(Task, related_name="invitations_sent", help_text="The Task that prompted the invitation.")
    question_id = models.CharField(max_length=64, blank=True, null=True, help_text="The ID of the question that prompted the invitation.")

    to_user = models.ForeignKey(User, related_name="invitations_received", blank=True, null=True, help_text="The user who the invitation was sent to, if to an existing user.")
    to_email = models.CharField(max_length=256, blank=True, null=True, help_text="The email address the invitation was sent to, if to a non-existing user.")

    text = models.TextField(blank=True, help_text="The personalized text of the invitation.")
    invite_to_project = models.ForeignKey(Project, blank=True, null=True, related_name="invitations_sent", help_text="The Project that the user being invited is being invited to join, if any.")

    sent_at = models.DateTimeField(blank=True, null=True, help_text="If the invitation has been sent by email, when it was sent.")
    accepted_at = models.DateTimeField(blank=True, null=True, help_text="If the invitation has been accepted, when it was accepted.")

    accepted_user = models.ForeignKey(User, related_name="invitations_accepted", blank=True, null=True, help_text="The user that accepted the invitation (i.e. if the invitation was by email address).")
    accepted_task = models.ForeignKey(Task, related_name="invitations_received", blank=True, null=True, help_text="The Task generated by accepting the invitation.")

    email_invitation_code = models.CharField(max_length=64, blank=True, help_text="For emails, a unique verification code.")

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    extra = JSONField(blank=True, help_text="Additional information stored with this object.")

    @staticmethod
    def create(from_task, from_question_id, to_user, to_email, text, add_to_project):
        return Invitation.objects.create(
            from_user = from_task.user,
            from_task = from_task,
            question_id = from_question_id,
            to_user = to_user,
            to_email = to_email,
            text = text,
            invite_to_project = from_task.project if add_to_project else None,
            email_invitation_code = Invitation.generate_email_invitation_code(),
        )

    @staticmethod
    def generate_email_invitation_code():
        import random, string
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(24))

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
                'accept_url': self.get_acceptance_url(),
                'from_user': self.from_user,
                'task': self.from_task,
                'message': self.text,
            }
        )
        Invitation.objects.filter(id=self.id).update(sent_at=timezone.now())

    def is_expired(self):
        from datetime import timedelta
        return timezone.now() > (self.sent_at + timedelta(days=10))
    is_expired.boolean = True

    def accept(self, request):
        from django.contrib.auth import authenticate, login, logout
        import urllib.parse

        # If this is a repeat-click, just redirect the user to where
        # they went the first time.
        if self.accepted_at:
            return self.accepted_task.get_absolute_url()

        # Can't accept if this object has expired. Warn the user but
        # send them to the homepage.
        if self.is_expired():
            from django.contrib import messages
            messages.add_message(request, messages.ERROR, 'The invitation you wanted to accept has expired.')
            return "/"

        # Get the user logged into an account.
        
        matched_user = self.to_user \
            or User.objects.filter(email=self.to_email).exclude(id=self.from_user.id).first()
        
        if self.to_user and request.user == self.to_user:
            # If the invitation was to a user account, and the user is already logged
            # in to it, then we're all set.
            pass

        elif matched_user:
            # If the invitation was to a user account or to an email address that has
            # an account, the user on this request has just demonstrated ownership of
            # that user's email address, so we can log them in immediately.
            matched_user = authenticate(user_object=matched_user)
            if not matched_user.is_active:
                messages.add_message(request, messages.ERROR, 'Your account has been deactivated.')
                return "/"
            if request.user.is_authenticated():
                # The user was logged into a different account before. Log them out
                # of that account and then log them into the account in the invitation.
                logout(request) # setting a message after logout but before login should keep the message in the session
                messages.add_message(request, messages.INFO, 'You have been logged in as %s.' % matched_user)
            login(request, matched_user)

        elif request.user.is_authenticated() and request.user != self.from_user:
            # The invitation was sent to an email address that does not have a matching
            # User account, but the user is already logged into an account --- continue
            # with that account.
            pass

        else:
            # The invitation was sent to an email address that does not have a matching
            # User account. Ask the user to log in or sign up, using a redirect to the
            # login page, with a next URL set to take them back to this step. In the
            # event the user was logged in (and we didn't handle it above), log them
            # out and force them to log into a new account.
            from django.core.urlresolvers import reverse
            logout(request)
            return reverse('account_login') + "?next=" + urllib.parse.quote(self.get_acceptance_url())

        # The user is now logged in and able to accept the invitation.
        with transaction.atomic():
            # Create the new task.
            task = Task.objects.create(
                project=self.from_task.project,
                user=request.user,
                module_id=self.from_task.module_id,
                title=self.from_task.title,
                requested_by=self.from_task,
                requestor_notes=self.text,
            )

            # Add user to the project team.
            if self.invite_to_project:
                ProjectMembership.objects.create(
                    project=self.invite_to_project,
                    user=request.user,
                    )

            # Update this invitation.
            Invitation.objects.filter(id=self.id).update(
                accepted_at=timezone.now(),
                accepted_user=request.user,
                accepted_task=task,
            )

            # TODO: Notify self.from_user that the invitation was accepted.

            # Redirect the user to this task, and if it's a request for a particular
            # question then take them to that question.
            return task.get_absolute_url() + (("?q=" + urllib.parse.quote(self.question_id)) if self.question_id else "")
