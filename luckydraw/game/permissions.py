from rest_framework import permissions
from .models import *


class IsUser(permissions.BasePermission):
    """
    checks and permits if user is active or not.
    """

    def has_permission(self, request, view):
        user=User.objects.filter(user=self.request.user)
        if user and user.is_active==False:
            return True
        else:
            return False


class IsAdmin(permissions.BasePermission):
    """
    checks if user is superadmin or not.
    """

    def has_permission(self, request, view):
        user = request.user
        if user and user.is_superuser:
            return True
        else:
            return False


class IsNotActive(permissions.BasePermission):
    """
    checking if user is already active or not.
    """
    def has_permission(self, request, view):
        if request.user.is_active == True:
             return False
        return True


SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']

class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    The request is authenticated as a user, or is a read-only request.
    """

    def has_permission(self, request, view):
        if (request.method in SAFE_METHODS or
            request.user and
            request.user.is_authenticated()):
            return True
        return False