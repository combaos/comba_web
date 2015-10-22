__author__ = 'michel'

from django.contrib.auth.models import User, check_password, Group, Permission, ContentType
from comba_lib.security.user import CombaUser
import simplejson
class RedisBackend(object):
    """
    Authenticate against the settings ADMIN_LOGIN and ADMIN_PASSWORD.

    Use the login name, and a hash of the password. For example:

    ADMIN_LOGIN = 'admin'
    ADMIN_PASSWORD = 'sha1$4e987$afbcf42e21bd417fb71db8c66b321e9fc33051de'
    """


    def check_auth(self, username, password):
        userdb = CombaUser()
        if userdb.hasPassword(username, password):
            return userdb.getUser(username)
        else:
            return False

    def authenticate(self, username=None, password=None):
        valid_user = self.check_auth(username, password)

        if valid_user:
            group = None
            groupcreated = None
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:

                user = User(username=valid_user['username'], password=valid_user['password'])

                if valid_user['role'] == 'admin':
                    user.is_superuser = True
                    user.is_staff = True
                elif valid_user['role'] == 'webuser':
                    (group, groupcreated) = Group.objects.get_or_create(name='webuser')
                    user.is_staff = True
                elif valid_user['role'] == 'serviceuser':
                    (group, groupcreated) = Group.objects.get_or_create(name='serviceuser')
                else:
                    return None
                user.save()
                if group:
                    if groupcreated:
                        group.save()
                    user = User.objects.get(username=valid_user['username'])
                    user.groups.add(group)
                    user.save()

            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None