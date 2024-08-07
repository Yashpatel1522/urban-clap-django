from rest_framework.permissions import BasePermission

# Vishvas Panshiniya


def RoleReturn(request):
    if request.user.is_superuser:
        role = 'admin'
    elif not request.user.is_staff:
        role = 'customer'
    else:
        role = 'serviceprovider'
    return role


class IsAdminOrServiceProvider(BasePermission):
    def has_permission(self, request, view):
        role = RoleReturn(request)
        return request.user and (role == "admin" or role == "serviceprovider")


class IsAllRole(BasePermission):
    def has_permission(self, request, view):
        role = RoleReturn(request)
        return request.user


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        role = RoleReturn(request)
        return request.user and role == "admin"


class IsSeviceProvider(BasePermission):
    def has_permission(self, request, view):
        role = RoleReturn(request)
        return request.user and role == "serviceprovider"


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        role = RoleReturn(request)
        return request.user and role == "customer"
