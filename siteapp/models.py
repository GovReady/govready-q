from .betteruser import UserBase, UserManagerBase

class UserManager(UserManagerBase):
    def _get_user_class(self):
        return User

class User(UserBase):
    objects = UserManager()

    def __str__(self):
        from guidedmodules.models import TaskAnswer
        name = TaskAnswer.objects.filter(
            question__task=self.get_settings_task(),
            question__question_id="name").first()
        if name:
            return name.value #+ " <" + self.email + ">"
        else:
            return self.email

    def get_settings_task(self):
        from guidedmodules.models import Task
        return Task.objects.filter(
            editor=self,
            project=None,
            module_id="account_settings").first()

    def render_context_dict(self):
        return {
            "id": self.id,
            "name": str(self),
        }
        