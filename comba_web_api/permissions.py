__author__ = 'michel'
from rest_framework import permissions

class isServiceUser(permissions.BasePermission):
    """
    Global permission check for blacklisted IPs.
    """

    def has_permission(self, request, view):
        for group in request.user.groups.all():
            if group.name == "serviceuser":
                return True
        else:
            return False

