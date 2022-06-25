import time
from urllib.parse import urlencode
import json

from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.contrib.auth.models import Permission
from mozilla_django_oidc.auth import OIDCAuthenticationBackend, LOGGER
from mozilla_django_oidc.middleware import SessionRefresh
from mozilla_django_oidc.utils import absolutify, add_state_and_nonce_to_session
from base64 import urlsafe_b64decode

from siteapp.models import Portfolio, User


class OIDCAuth(OIDCAuthenticationBackend):

    # override get_user method to debug token
    def get_userinfo(self, access_token, id_token, payload):
        """Return user details dictionary. The id_token and payload are not used in
        the default implementation, but may be used when overriding this method"""
        import requests
        user_response = requests.get(
            self.OIDC_OP_USER_ENDPOINT,
            headers={
                'Authorization': 'Bearer {0}'.format(access_token)
            },
            verify=self.get_settings('OIDC_VERIFY_SSL', True),
            timeout=self.get_settings('OIDC_TIMEOUT', None),
            proxies=self.get_settings('OIDC_PROXY', None))
        user_response.raise_for_status()
        # LOGGER.warning(f"DEBUG (5) user_response, {type(user_response.text)}, {user_response.text}")
        # split on ".": Header.Payload.Signature
        header, payload, signature = [self.parse_b64url(content) for content in user_response.text.split(".")]
        header = json.loads(header.decode('UTF-8'))
        # LOGGER.warning(f"DEBUG (6) header: {header}, \npayload: {payload}, \nsignature: {signature}")
        payload = payload[:-1] if b'\x1b' in payload else payload
        payload = json.loads(payload.decode('UTF-8)').strip('\x06'))
        # return user_response.json()
        return payload

    def parse_b64url(self, content):
        """Return decoded base64url content"""

        try:
            decoded = urlsafe_b64decode(content+str(b'======='))
        except:
            decoded = urlsafe_b64decode(content)
        return decoded

    def is_admin(self, groups):
        if settings.OIDC_ROLES_MAP["admin"] in groups:
            return True
        return False

    # override verify_claims
    def verify_claims(self, claims):
        """Verify the provided claims to decide if authentication should be allowed."""

        # Verify claims required by default configuration
        # Check if user has role to access service
        GROUP_SPLIT_CHAR = '^'
        user_groups = claims.get(settings.OIDC_CLAIMS_MAP['groups']).split(GROUP_SPLIT_CHAR)
        if settings.OIDC_ROLES_MAP['admin'] in user_groups:
            return True
        if settings.OIDC_ROLES_MAP['normal'] in user_groups:
            return True
        return False

    # override get_or_create_user method
    def get_or_create_user(self, access_token, id_token, payload):
        """Returns a User instance if 1 user is found. Creates a user if not found
        and configured to do so. Returns nothing if multiple users are matched."""

        user_info = self.get_userinfo(access_token, id_token, payload)

        claims_verified = self.verify_claims(user_info)
        if not claims_verified:
            msg = 'Claims verification failed'
            HttpResponseForbidden()
            raise SuspiciousOperation(msg)

        # use email as username
        users = User.objects.filter(username=user_info.get('mail', None))

        if len(users) == 1:
            return self.update_user(users[0], user_info)
        elif len(users) > 1:
            # In the rare case that two user accounts have the same email address,
            # bail. Randomly selecting one seems really wrong.
            msg = 'Multiple users returned'
            raise SuspiciousOperation(msg)
        elif self.get_settings('OIDC_CREATE_USER', True):
            user = self.create_user(user_info)
            return user
        else:
            LOGGER.debug('Login failed: No user with %s found, and '
                         'OIDC_CREATE_USER is False',
                         self.describe_user_by_claims(user_info))
            return None

    def create_user(self, claims):

        # TODO: Better handling if no 'username' set. Current approach could cause duplicate record error
        # TODO: Is the below sufficiently generic for different customizations for a customer?
        data = {'email': claims.get(settings.OIDC_CLAIMS_MAP['email'], "email@example.com"),
                'first_name': claims.get(settings.OIDC_CLAIMS_MAP['first_name'], "first_name"),
                'last_name': claims.get(settings.OIDC_CLAIMS_MAP['last_name'], "last_name"),
                'username': claims.get(settings.OIDC_CLAIMS_MAP['username'], "username01"),
                'is_staff': False}

        user = self.UserModel.objects.create_user(**data)
        # Set permissions
        user.user_permissions.add(Permission.objects.get(codename='view_appsource'))
        user.save()
        GROUP_SPLIT_CHAR = '^'
        user_groups = claims.get(settings.OIDC_CLAIMS_MAP['groups']).split(GROUP_SPLIT_CHAR)
        if settings.OIDC_ROLES_MAP['admin'] in user_groups:
            user.is_superuser = True
            user.is_staff = True
            user.save()
        if user.default_portfolio is None:
            portfolio = user.create_default_portfolio_if_missing()
        return user

    def update_user(self, user, claims):

        original_values = [getattr(user, x.name) for x in user._meta.get_fields() if hasattr(user, x.name)]

        user.email = claims.get(settings.OIDC_CLAIMS_MAP['email'], "missing@example.com")
        user.first_name = claims.get(settings.OIDC_CLAIMS_MAP['first_name'], "missing first_name")
        user.last_name = claims.get(settings.OIDC_CLAIMS_MAP['last_name'], "missing last_name")
        user.username = claims.get(settings.OIDC_CLAIMS_MAP['username'], "missing username")
        groups = claims.get(settings.OIDC_CLAIMS_MAP['groups'], "missing groups")

        # Update permissions based on claim groups
        GROUP_SPLIT_CHAR = '^'
        user_groups = claims.get(settings.OIDC_CLAIMS_MAP['groups']).split(GROUP_SPLIT_CHAR)
        if settings.OIDC_ROLES_MAP['admin'] in user_groups:
            user.is_superuser = True
            user.is_staff = True
        else:
            user.is_superuser = False
            user.is_staff = False

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

        token_payload = {
            'client_id': self.OIDC_RP_CLIENT_ID,
            'client_secret': self.OIDC_RP_CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': absolutify(
                self.request,
                reverse(reverse_url))
        }
        token_payload.update(self.get_settings('OIDC_AUTH_REQUEST_EXTRA_PARAMS', {}))

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


class OIDCSessionRefresh(SessionRefresh):
    def process_request(self, request):
        if not self.is_refreshable_url(request):
            # LOGGER.debug('request is not refreshable')
            return

        expiration = request.session.get('oidc_id_token_expiration', 0)
        now = time.time()
        if expiration > now:
            # The id_token is still valid, so we don't have to do anything.
            # LOGGER.debug('id token is still valid (%s > %s)', expiration, now)
            return

        # LOGGER.debug('id token has expired')
        # The id_token has expired, so we have to re-authenticate silently.
        auth_url = self.get_settings('OIDC_OP_AUTHORIZATION_ENDPOINT')
        client_id = self.get_settings('OIDC_RP_CLIENT_ID')
        state = get_random_string(self.get_settings('OIDC_STATE_SIZE', 32))

        # Build the parameters as if we were doing a real auth handoff, except
        # we also include prompt=none.
        params = {
            'response_type': 'code',
            'client_id': client_id,
            'redirect_uri': absolutify(
                request,
                reverse(self.get_settings('OIDC_AUTHENTICATION_CALLBACK_URL',
                                          'oidc_authentication_callback'))
            ),
            'state': state,
            'scope': self.get_settings('OIDC_RP_SCOPES', 'openid email'),
            'prompt': 'none',
        }

        if self.get_settings('OIDC_USE_NONCE', True):
            nonce = get_random_string(self.get_settings('OIDC_NONCE_SIZE', 32))
            params.update({
                'nonce': nonce
            })
        params.update(self.get_settings('OIDC_AUTH_REQUEST_EXTRA_PARAMS', {}))

        add_state_and_nonce_to_session(request, state, params)

        request.session['oidc_login_next'] = request.get_full_path()

        query = urlencode(params)
        redirect_url = '{url}?{query}'.format(url=auth_url, query=query)
        if request.is_ajax():
            # Almost all XHR request handling in client-side code struggles
            # with redirects since redirecting to a page where the user
            # is supposed to do something is extremely unlikely to work
            # in an XHR request. Make a special response for these kinds
            # of requests.
            # The use of 403 Forbidden is to match the fact that this
            # middleware doesn't really want the user in if they don't
            # refresh their session.
            response = JsonResponse({'refresh_url': redirect_url}, status=403)
            response['refresh_url'] = redirect_url
            return response
        return HttpResponseRedirect(redirect_url)
