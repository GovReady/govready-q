from rest_framework import permissions

from siteapp.enums.access_level import AccessLevelEnum


class APITokenPermission(permissions.BasePermission):
    READ_ONLY_METHODS = ['GET']
    WRITE_ONLY_METHODS = ['POST', "PUT", "DELETE"]

    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):
        if hasattr(view, request.method.lower()):  # Supported endpoint for ViewSet
            if request.user.access_level == AccessLevelEnum.READ_ONLY and request.method not in self.READ_ONLY_METHODS:
                self.message = f"User logged in with {AccessLevelEnum.READ_ONLY}.  Endpoint requires " \
                               f"{AccessLevelEnum.WRITE_ONLY} or {AccessLevelEnum.READ_WRITE}."
                return False
            elif request.user.access_level == AccessLevelEnum.WRITE_ONLY and request.method not in self.WRITE_ONLY_METHODS:
                self.message = f"User logged in with {AccessLevelEnum.WRITE_ONLY}.  Endpoint requires " \
                    f"{AccessLevelEnum.READ_ONLY} or {AccessLevelEnum.READ_WRITE}."
                return False
        return True
