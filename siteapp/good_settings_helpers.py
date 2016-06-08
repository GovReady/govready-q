from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter

class AllauthAccountAdapter(DefaultAccountAdapter):
    def send_mail(self, template_prefix, email, context):
        from htmlemailer import send_mail
        send_mail(
            template_prefix,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            context
        )

if settings.ALLAUTH_FORM_RENDERER:
    # Monkey-patch allauth to return forms that render with django-bootstrap-form.
    import allauth.account.views
    allauth_get_form_class_original = allauth.account.views.get_form_class
    def allauth_get_form_class_patch(*args, **kwargs):
        form = allauth_get_form_class_original(*args, **kwargs)
        class F(form):
            def as_p(self):
                return settings.ALLAUTH_FORM_RENDERER(self)
        return F
    allauth.account.views.get_form_class = allauth_get_form_class_patch
