from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, models
from django.conf import settings
from django.utils import timezone

import time, uuid

from exclusiveprocess import Lock

from notifications.models import Notification

class Command(BaseCommand):
    help = 'Sends emails for notifications.'

    def add_arguments(self, parser):
        parser.add_argument('forever', nargs='?', type=bool)

    def handle(self, *args, **options):
        # Ensure this process doesn't run multiple times concurrently.
        Lock(die=True).forever()

        if options["forever"]:
            # Loop forever.
            while True:
                self.send_new_emails()
                time.sleep(20)

        else:
            # Run on-off job.
            self.send_new_emails()

    def send_new_emails(self):
        # Find notifications that have not been emailed but should be emailed.
        #  * The user has notifications enabled as per notifemails_enabled value
        #    [(0, "As They Happen"), (1, "Don't Email")] in User model.
        #  * The notification is more recent than the last notification email sent
        #    via the "_notifemails_last_notif_id" field in User model.
        #  * The notification has target object so that we can generate a link back
        #    to the site.
        # And go in order because once we mark a notification as emailed, we imply
        # that all earlier notifications have been sent to the user too.
        notifs = Notification.objects\
            .filter(
                recipient__notifemails_enabled=0,
                id__gt=models.F('recipient__notifemails_last_notif_id'),
                emailed=False,
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

        # Let the actor render appropriately.
        notif.actor.preload_profile()

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
        from siteapp.templatetags.notification_helpers import get_notification_link
        url = get_notification_link(target, notif)
        if url is None:
            # Some notifications go stale and can't generate links,
            # and then we can't email notifications.
            return

        # Prevent multiple notifications emailed from multiple instances/containers of GovReady-Q
        # Make this transaction atomic
        # Re-check the database to make sure the individual notification is still unsent
        # Lock the notification record in the database while sending the email
        with transaction.atomic():
            notif_latest = (
                Notification.objects.select_for_update().get(id=notif.id)
            )

            if not notif_latest.emailed:
                send_mail(
                    "email/notification",
                    settings.DEFAULT_FROM_EMAIL,
                    [notif_latest.recipient.email],
                    {
                        "notification": notif,
                        "url": settings.SITE_ROOT_URL + url,
                        "whatreplydoes": what_reply_does,
                    },
                    headers={
                        "From": settings.NOTIFICATION_FROM_EMAIL_PATTERN % (str(notif.actor),),
                        "Reply-To": (settings.NOTIFICATION_REPLY_TO_EMAIL_PATTERN % (organization.name, notif.id, notif.data["secret_key"]))
                        if what_reply_does else "",
                        "Date": format_datetime(notif.timestamp),
                    }
                )

                # Mark notification as sent.
                notif_latest.emailed = True
                notif_latest.save(update_fields=['emailed'])
                # Update id of last notification sent to user
                notif.recipient.notifemails_last_notif_id = notif.id
                notif.recipient.notifemails_last_at = timezone.now()
                notif.recipient.save(update_fields=['notifemails_last_notif_id', 'notifemails_last_at'])
            else:
                # Save record with nothing changed to close transaction
                notif_latest.save()

        # Release row level database lock on notification
