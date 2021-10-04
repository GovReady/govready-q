from django.db.models import Q
from rest_framework import authentication
from rest_framework import exceptions

from siteapp.enums.access_level import AccessLevelEnum
from siteapp.models import User


class APITokenBackend(authentication.BaseAuthentication):

    def get_user_from_browser_session(self, request):
        from django.contrib.sessions.models import Session
        session = Session.objects.get(session_key=request.session.session_key)
        session_data = session.get_decoded()
        uid = session_data.get('_auth_user_id')
        user = User.objects.get(id=uid)
        user.access_level = AccessLevelEnum.READ_WRITE
        return user, None

    def authenticate(self, request):
        if not request.session.exists(request.session.session_key):
            header = request.META.get("HTTP_AUTHORIZATION", "").split()
            if not header:
                return
            api_key = header[-1]
            try:
                user = User.objects.get(Q(api_key_rw=api_key) | Q(api_key_ro=api_key) | Q(api_key_wo=api_key))
                if user.api_key_ro == api_key:
                    user.access_level = AccessLevelEnum.READ_ONLY
                elif user.api_key_wo == api_key:
                    user.access_level = AccessLevelEnum.WRITE_ONLY
                else:
                    user.access_level = AccessLevelEnum.READ_WRITE
                return user, None
            except User.DoesNotExist:
                raise exceptions.AuthenticationFailed('No Users matching provided API key')
        return self.get_user_from_browser_session(request)

