from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """
    Разрешает автору объекта совершать операции изменения/удаления,
    остальным пользователям - только безопасные методы.
    """
    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.author == request.user


class IsAdminOrReadOnly(BasePermission):
    """
    Разрешает администратору совершать любые операции над объектом,
    остальным пользователям - только безопасные методы.
    """
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_staff
