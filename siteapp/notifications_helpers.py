from django.http import HttpResponseNotAllowed, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

def issue_notification(acting_user, verb, target, recipients='WATCHERS', **notification_kwargs):
    # Create a notification *from* acting_user *to*
    # all users who are watching target.
    from notifications.signals import notify
    if recipients == 'WATCHERS':
        recipients = target.get_notification_watchers()
    for user in recipients:
        # Don't notify the acting user about an
        # action they took.
        if user == acting_user:
            continue

        # Create the notification.
        # TODO: Associate this notification with an organization?
        notify.send(
            acting_user, verb=verb, target=target,
            recipient=user,
            **notification_kwargs)

@login_required
def mark_notifications_as_read(request):
	# Mark one or all of the user's notifications as read.

    # TODO: Filter for notifications relevant to the organization site the user is on.
	notifs = request.user.notifications

	if "upto_id" in request.POST:
		# Mark up to the one with id upto_id. This ensures that if a 
		# notification was generated after the client-side UI
		# displayed the last batch of notifications, that we
		# won't clear out something the user hasn't seen.
		notifs = notifs.filter(id__lte=request.POST['upto_id'])
	
	elif "id" in request.POST:
		# Mark a single notification as read.
		notifs = notifs.filter(id=request.POST['id'])

	notifs.mark_all_as_read()

	return JsonResponse({ "status": "ok" })


@csrf_exempt
def notification_reply_email_hook(request):
    # This URL is called by Mailgun to submit an incoming email from notifications.

    def error(msg):
        # Use a 406 status code to signal to Mailgun to not try again.
        return JsonResponse({ "status": "error", "message": msg}, status=406)

    # Validate the Mailgun signature to ensure this request is from Mailgun.
    try:
        import hashlib, hmac
        if request.POST.get("signature") != hmac.new(
          key=settings.MAILGUN_API_KEY.encode("ascii"),
          msg=(request.POST.get("timestamp", "") + request.POST.get("token", "")).encode("ascii"),
          digestmod=hashlib.sha256).hexdigest():
            raise Exception("Invalid signature.")
    except Exception as e:
       return error(str(e))

    # What is this email for? Validate it.
    from notifications.models import Notification
    import re
    recip = request.POST.get("recipient", "")
    m = re.match(settings.NOTIFICATION_REPLY_TO_EMAIL_REGEX, recip)
    if not m:
       return error("Invalid recipient.")
    notification_id, notification_key = m.groups()
    try:
        notification = Notification.objects.get(id=notification_id)
    except Notification.DoesNotExist:
       return error("Invalid recipient - invalid notification id.")
    if (notification.data or {}).get("secret_key") != notification_key:
       return error("Invalid recipient - invalid notification key.")

    # Ok now what to do with it?
    if not hasattr(notification.target, "post_notification_reply"):
       return error("Invalid recipient - invalid notification target.")

    # Execute.
    try:
        notification.target.post_notification_reply(notification, notification.recipient, request.POST.get("stripped-text", ""))
    except Exception as e:
        # Swallow errors.
       return error(str(e))

    # Signal OK with a 200 response.
    return JsonResponse({ "status": "ok" })

