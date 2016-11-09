from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, models
from django.conf import settings
from django.utils import timezone

import time, uuid

from notifications.models import Notification

class Command(BaseCommand):
    help = 'Sends emails for notifications.'
    args = '[forever]'

    def handle(self, *args, **options):
        # Ensure this process doesn't run multiple times concurrently.
        exclusive_process("q_send_notification_emails")

        if len(args) == 1 and args[0] == "forever":
            # Loop forever.
            while True:
                self.send_new_emails()
                time.sleep(20)

        else:
            # Run on-off job.
            self.send_new_emails()


    def send_new_emails(self):
        # Find notifications that have not been emailed but should be emailed.
        #  * The user has notifications enabled.
        #  * The notification is more recent than the last notification email sent.
        #  * The notification has target object so that we can generate a link back
        #    to the site.
        # And go in order because once we mark a notification as emailed, we imply
        # that all earlier notifications have been sent to the user too.
        notifs = Notification.objects\
            .filter(
                recipient__notifemails_enabled=0,
                id__gt=models.F('recipient__notifemails_last_notif_id')
            )\
            .exclude(target_object_id=None)\
            .order_by('id')

        for notif in notifs:
            self.send_it_out(notif)

    def send_it_out(self, notif):
        # If the Notification's target does not have an 'organization' attribute
        # and a 'get_absolute_url' attribute, then we can't generate a link back
        # to the site, so skip it.
        target = notif.target
        if not hasattr(target, 'get_absolute_url'): return
        organization = getattr(notif.target, 'organization', None)
        if not organization: return

        # Let the actor render appropriate for the org.
        notif.actor.localize_to_org(organization)

        # If the target supports receiving email replies (like replying to an email
        # about a discussion), then store a secret in the notif.data dictionary so
        # that we can tell that a user has replied to something we sent them (and
        # can't reply to something we didn't notify them about).
        what_reply_does = None
        if hasattr(target, "post_notification_reply"):
            notif.data = notif.data or { }
            notif.data["secret_key"] = uuid.uuid4()
            notif.save(update_fields=['data'])
            what_reply_does = "You can reply to this email to post a comment to the discussion. Do not forward this email to others."

        # Send the email.
        from htmlemailer import send_mail
        from email.utils import format_datetime
        from siteapp.templatetags import q as q_template_tags
        send_mail(
            "email/notification",
            settings.DEFAULT_FROM_EMAIL,
            [notif.recipient.email],
            {
                "notification": notif,
                "url": organization.get_url(q_template_tags.get_notification_link(target, notif)),
                "whatreplydoes": what_reply_does,
            },
            headers={
                "From": settings.NOTIFICATION_FROM_EMAIL_PATTERN % (str(notif.actor),),
                "Reply-To": (settings.NOTIFICATION_REPLY_TO_EMAIL_PATTERN % (organization.name, notif.id, notif.data["secret_key"]))
                if what_reply_does else "",
                "Date": format_datetime(notif.timestamp),
            }
        )

        # Mark it as sent.
        notif.recipient.notifemails_last_notif_id = notif.id
        notif.recipient.notifemails_last_at = timezone.now()
        notif.recipient.save(update_fields=['notifemails_last_notif_id', 'notifemails_last_at'])

def exclusive_process(name):
    # Based on https://github.com/mail-in-a-box/mailinabox/blob/master/management/utils.py
    ######################################################################################

    # Ensure that this process, named `name`, does not execute multiple
    # times concurrently by writing our process ID to a global file.

    import os, sys, atexit

    pidfile = '/tmp/%s.pid' % name
    mypid = os.getpid()

    # This function will be used with atexit to clear the pid file when
    # the program terminates.
    def clear_my_pid():
        os.unlink(pidfile)

    def is_pid_valid(pid):
        """Checks whether a pid is a valid process ID of a currently running process."""
        # adapted from http://stackoverflow.com/questions/568271/how-to-check-if-there-exists-a-process-with-a-given-pid
        import os, errno
        if pid <= 0: raise ValueError('Invalid PID.')
        try:
            os.kill(pid, 0)
        except OSError as err:
            if err.errno == errno.ESRCH: # No such process
                return False
            elif err.errno == errno.EPERM: # Not permitted to send signal
                return True
            else: # EINVAL
                raise
        else:
            return True

    # Attempt to get a lock on ourself so that the concurrency check
    # itself is not executed in parallel.
    with open(__file__, 'r+') as flock:
        # Try to get a lock. This blocks until a lock is acquired. The
        # lock is held until the flock file is closed at the end of the
        # with block.
        os.lockf(flock.fileno(), os.F_LOCK, 0)

        # While we have a lock, look at the pid file. First attempt
        # to write our pid to a pidfile if no file already exists there.
        try:
            with open(pidfile, 'x') as f:
                # Successfully opened a new file. Since the file is new
                # there is no concurrent process. Write our pid.
                f.write(str(mypid))
                atexit.register(clear_my_pid)

        except FileExistsError:
            # The pid file already exixts, but it may contain a stale
            # pid of a terminated process.
            with open(pidfile, 'r+') as f:
                # Read the pid in the file.
                try:
                    existing_pid = int(f.read().strip())
                except ValueError:
                    pass
                else:
                    # Check if the pid in it is valid, and if so print a
                    # message and exit.
                    if is_pid_valid(existing_pid):
                        print("Another %s is already running (pid %d)." % (name, existing_pid), file=sys.stderr)
                        sys.exit(1)

                # The file didn't have a valid pid, so overwrite the file
                # with our pid.
                f.seek(0)
                f.write(str(mypid))
                f.truncate()
                atexit.register(clear_my_pid)
 
