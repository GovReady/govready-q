import requests
from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from django.conf import settings
from requests.auth import HTTPBasicAuth

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

    def get_token(self, payload):
        """Return token object as a dictionary."""

        auth = None
        if self.get_settings('OIDC_TOKEN_USE_BASIC_AUTH', False):
            # When Basic auth is defined, create the Auth Header and remove secret from payload.
            user = payload.get('client_id')
            pw = payload.get('client_secret')

            auth = HTTPBasicAuth(user, pw)
            del payload['client_secret']

        response = requests.post(
            self.OIDC_OP_TOKEN_ENDPOINT,
            data=payload,
            auth=auth,
            verify=self.get_settings('OIDC_VERIFY_SSL', True),
            timeout=self.get_settings('OIDC_TIMEOUT', None),
            proxies=self.get_settings('OIDC_PROXY', None))
        import ipdb; ipdb.set_trace()
        response.raise_for_status()
        return response.json()
