from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from django.conf import settings

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
