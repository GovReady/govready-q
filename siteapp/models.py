from .betteruser import UserBase, UserManagerBase

class UserManager(UserManagerBase):
    def _get_user_class(self):
        return User

class User(UserBase):
    objects = UserManager()

