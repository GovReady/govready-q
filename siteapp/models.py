from .betteruser import UserBase, UserManagerBase

class UserManager(UserManagerBase):
    def _get_user_class(self):
        return User

class User(UserBase):
    objects = UserManager()

    def __str__(self):
        from guidedmodules.models import Answer
        name = Answer.objects.filter(
            task__editor=self,
            task__project=None,
            task__module_id="account_settings",
            question_id="name").first()
        if name:
            return name.value + " <" + self.email + ">"
        else:
            return self.email

    def render_context_dict(self):
        return {
            "id": self.id,
            "name": str(self),
        }
        