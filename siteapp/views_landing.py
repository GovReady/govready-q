# Views for q.govready.com, the special domain that just
# is a landing page and a way to create new organization
# subdomains.

from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse, HttpResponseNotAllowed
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
from django.db import transaction

def homepage(request):
    # Main landing page.
    return render(request, "landing.html")

def aboutpage(request):
    # About page
    return render(request, "about.html")

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
