from rest_framework import permissions
from .models import *


class IsUser(permissions.BasePermission):

    def has_permission(self, request, view):
        user=User.objects.filter(user=self.request.user)
        if user and user.is_active==False:
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