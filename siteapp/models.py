from .betteruser import UserBase, UserManagerBase

class UserManager(UserManagerBase):
    def _get_user_class(self):
        return User

class User(UserBase):
    objects = UserManager()

    def __str__(self):
        from guidedmodules.models import TaskAnswer
        name = TaskAnswer.objects.filter(
            question__task__editor=self,
            question__task__project=None,
            question__task__module_id="account_settings",
            question__question_id="name").first()
        if name:
            return name.value + " <" + self.email + ">"
        else:
            return self.email

    def render_context_dict(self):
        return {
            "id": self.id,
            "name": str(self),
        }
        