from rest_framework.permissions import BasePermission


class IsAdminPanelUser(BasePermission):

    message = "شما اجازه دسترسی به پنل مدیریت را ندارید."

    def has_permission(self, request, view):

        return (
            request.user
            and request.user.is_authenticated
            and (
                request.user.is_superuser
                or request.user.is_staff
            )
        )