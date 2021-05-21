from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from django.conf import settings

from siteapp.models import Portfolio


class OIDCAuth(OIDCAuthenticationBackend):

    def is_admin(self, groups):
        if settings.OIDC_ROLES_MAP["admin"] in groups:
            return True
        return False

    def create_user(self, claims):
        data = {'email': claims.get(settings.OIDC_EMAIL_CLAIM_KEY, 'email'),
                'first_name': claims.get(settings.OIDC_FIRSTNAME_CLAIM_KEY, 'email'),
                'last_name': claims.get(settings.OIDC_LASTNAME_CLAIM_KEY, 'family_name'),
                'username': claims.get(settings.OIDC_USERNAME_CLAIM_KEY, 'preferred_username'),
                'is_staff': self.is_admin(claims.get(settings.OIDC_GROUPS_CLAIM_KEY, 'groups'))}

        user = self.UserModel.objects.create_user(**data)
        portfolio = Portfolio.objects.create(title=user.email.split('@')[0], description="Personal Portfolio")
        portfolio.assign_owner_permissions(user)
        return user

    def update_user(self, user, claims):
        original_values = [getattr(user, x.name) for x in user._meta.get_fields() if hasattr(user, x.name)]

        user.email = claims.get(settings.OIDC_EMAIL_CLAIM_KEY, 'email')
        user.first_name = claims.get(settings.OIDC_FIRSTNAME_CLAIM_KEY, 'given_name')
        user.last_name = claims.get(settings.OIDC_LASTNAME_CLAIM_KEY, 'family_name')
        user.username = claims.get(settings.OIDC_USERNAME_CLAIM_KEY, 'preferred_username')
        groups = claims.get(settings.OIDC_GROUPS_CLAIM_KEY, 'groups')
        user.is_staff = self.is_admin(groups)
        user.is_superuser = user.is_staff

        new_values = [getattr(user, x.name) for x in user._meta.get_fields() if hasattr(user, x.name)]
        if new_values != original_values:
            user.save()
        return user
