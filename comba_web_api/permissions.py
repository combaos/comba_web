__author__ = 'michel'
from rest_framework import permissions

class isServiceUser(permissions.BasePermission):
    """
    Global permission check for blacklisted IPs.
    """

    def has_permission(self, request, view):

        if request.user.is_superuser:
            return True

        for group in request.user.groups.all():
            if group.name == "serviceuser":
                return True
            if group.name == "webuser":
                return True
        else:
            return False

