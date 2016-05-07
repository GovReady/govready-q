from django.db import models, transaction, IntegrityError
from django.utils import timezone
from django.contrib.auth import authenticate
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.backends import ModelBackend
from django.conf import settings

import enum, re

from email_validator import validate_email, EmailNotValidError

# Custom user model and login backends

class LoginException(Exception):
	"""Abstract base class for the reasons a login fails."""
	pass
class InactiveAccount(LoginException):
	# is_active==False
	def __str__(self):
		return "The account is disabled."
class InvalidCredentials(LoginException):
	def __init__(self, *args):
		if len(args) == 0:
			self.msg = "The email address is not valid. Please check for typos."
		else:
			self.msg = args[0]
	def __str__(self):
		return self.msg
class IncorrectCredentials(LoginException):
	def __str__(self):
		return "The email address and password did not match an account here."

class UserManagerBase(models.Manager):
	def _get_user_class(self):
		return User

	# used by django.contrib.auth.backends.ModelBackend
	def get_by_natural_key(self, key):
		return self._get_user_class().objects.get(email=key)

	# support the createsuperuser management command.
	def create_superuser(self, email, password, **extra_fields):
		user = self._get_user_class()(email=email)
		user.is_staff = True
		user.is_superuser = True
		user.set_password(password)
		user.save()
		return user

class UserBase(AbstractBaseUser, PermissionsMixin):
	"""Our user model, where the primary identifier is an email address."""
	# https://github.com/django/django/blob/master/django/contrib/auth/models.py#L395
	email = models.EmailField(unique=True)
	is_staff = models.BooleanField(default=False, help_text='Whether the user can log into this admin.')
	is_active = models.BooleanField(default=True, help_text='Unselect this instead of deleting accounts.')
	date_joined = models.DateTimeField(default=timezone.now)

	# custom user model requirements
	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = []
	def get_full_name(self): return self.email
	def get_short_name(self): return self.email
	class Meta:
		abstract = True
		verbose_name = 'user'
		verbose_name_plural = 'users'
	# Normally the object field would be defined here but the subclass
	# must set it to a Manager that knows what class this is for.

	@classmethod # first argument is the concrete User class
	def get_or_create(User, email):
		# Normalize the email address prior to checking if it is in the database.
		# See the email validation library's README for why that's important,
		# particularly for internationalized addresses.
		#
		# If the email address is not valid, raise an EmailNotValidError.
		email = validate_email(email, check_deliverability=False)["email"]

		# Fetch an existing User for this email address, if present.
		try:
			# Does the user exist?
			return User.objects.get(email=email)
		except User.DoesNotExist:
			# Create a new user.

			# We've already validated the email address's syntax and normalized it.
			# If we're configured to also check deliverability, do that now. We skip
			# that during login. This raises an EmailNotValidError (in particlar a
			# EmailUndeliverableError) on failure.
			if settings.VALIDATE_EMAIL_DELIVERABILITY:
				validate_email(email, check_deliverability=True)

			try:
				# In order to recover from an IntegrityError
				# we must wrap the error-prone part in a
				# transaction. Otherwise we can't execute
				# further queries from the except block.
				# Not sure why. Occurs w/ Sqlite.
				with transaction.atomic():
					# Try to create it.
					user = User(email=email)
					user.set_unusable_password()
					user.save()
					return user
			except IntegrityError:
				# Creation failed (unique key violation on username),
				# so try to get it again. If this fails, something
				# weird happened --- just raise an exception then.
				return User.objects.get(email=email)

	@classmethod # first argument is the concrete User class
	def authenticate(User, email, password):
		# Returns an authenticated User object for the email and password,
		# or raises a LoginException on failure.

		# Normalize the email address prior to checking if it is in the database.
		# See the email validation library's README for why that's important,
		# particularly for internationalized addresses.
		try:
			email = validate_email(email, check_deliverability=False)["email"]
		except EmailNotValidError as e:
			raise InvalidCredentials(str(e))

		# Run Django's usual authenticate function.
		user = authenticate(email=email, password=password)
		
		if user is None:
			# Email/password pair not found in database.
			raise IncorrectCredentials()
	
		if not user.is_active:
			# Account is disabled.
			raise InactiveAccount()

		return user


class DirectLoginBackend(ModelBackend):
	# Register in settings.py!
	# Django can't log a user in without their password. Before they create
	# a password, we use this to log them in. Registered in settings.py.
	supports_object_permissions = False
	supports_anonymous_user = False
	def authenticate(self, user_object=None):
		return user_object

