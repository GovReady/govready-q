from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.urls import reverse
from mozilla_django_oidc.auth import OIDCAuthenticationBackend, LOGGER
from mozilla_django_oidc.utils import absolutify

from siteapp.models import Portfolio


class OIDCAuth(OIDCAuthenticationBackend):

    def is_admin(self, groups):
        if settings.OIDC_ROLES_MAP["admin"] in groups:
            return True
        return False

    def create_user(self, claims):
        data = {'email': claims[settings.OIDC_CLAIMS_MAP['email']],
                'first_name': claims[settings.OIDC_CLAIMS_MAP['first_name']],
                'last_name': claims[settings.OIDC_CLAIMS_MAP['last_name']],
                'username': claims[settings.OIDC_CLAIMS_MAP['username']],
                'is_staff': self.is_admin(claims[settings.OIDC_CLAIMS_MAP['groups']])}

        user = self.UserModel.objects.create_user(**data)
        portfolio = Portfolio.objects.create(title=user.email.split('@')[0], description="Personal Portfolio")
        portfolio.assign_owner_permissions(user)
        return user

    def update_user(self, user, claims):
        original_values = [getattr(user, x.name) for x in user._meta.get_fields() if hasattr(user, x.name)]

        user.email = claims[settings.OIDC_CLAIMS_MAP['email']]
        user.first_name = claims[settings.OIDC_CLAIMS_MAP['first_name']]
        user.last_name = claims[settings.OIDC_CLAIMS_MAP['last_name']]
        user.username = claims[settings.OIDC_CLAIMS_MAP['username']]
        groups = claims[settings.OIDC_CLAIMS_MAP['groups']]
        user.is_staff = self.is_admin(groups)
        user.is_superuser = user.is_staff

        new_values = [getattr(user, x.name) for x in user._meta.get_fields() if hasattr(user, x.name)]
        if new_values != original_values:
            user.save()
        return user

    def authenticate(self, request, **kwargs):
        """Authenticates a user based on the OIDC code flow."""

        self.request = request
        if not self.request:
            return None

        state = self.request.GET.get('state')
        code = self.request.GET.get('code')
        nonce = kwargs.pop('nonce', None)

        if not code or not state:
            return None

        reverse_url = self.get_settings('OIDC_AUTHENTICATION_CALLBACK_URL',
                                        'oidc_authentication_callback')

        redirect_uri = absolutify(
                self.request,
                reverse(reverse_url))
        if 'https' in settings.BASE_URL:
            redirect_uri = redirect_uri.replace('http', 'https')
        token_payload = {
            'client_id': self.OIDC_RP_CLIENT_ID,
            'client_secret': self.OIDC_RP_CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri
        }

        # Get the token
        token_info = self.get_token(token_payload)
        id_token = token_info.get('id_token')
        access_token = token_info.get('access_token')

        # Validate the token
        payload = self.verify_token(id_token, nonce=nonce)

        if payload:
            self.store_tokens(access_token, id_token)
            try:
                return self.get_or_create_user(access_token, id_token, payload)
            except SuspiciousOperation as exc:
                LOGGER.warning('failed to get or create user: %s', exc)
                return None
        return None
