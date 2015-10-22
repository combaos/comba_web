__author__ = 'michel'

from django.contrib.auth.models import User, check_password, Group, Permission, ContentType
from comba_lib.security.user import CombaUser


class RedisBackend(object):
    """
    Provides authentication via comba_lib
    """

    def check_auth(self, username, password):
        """
        check user and password in redis db
        :param username:
        :param password:
        :return:
        """
        userdb = CombaUser()

        if userdb.hasPassword(username, password):
            return userdb.getUser(username)
        else:
            return False

    #------------------------------------------------------------------------------------------#

    def authenticate(self, username=None, password=None):
        """
        Overwrite the parent authenticate method
        :param username:
        :param password:
        :return:
        """
        # check user and password
        valid_user = self.check_auth(username, password)

        if valid_user:
            group = None
            groupcreated = None

            try:
                # is the user already registered in django db?
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # create a user object
                user = User(username=valid_user['username'], password=valid_user['password'])
                # check the role
                if valid_user['role'] == 'admin':
                    # the superuser
                    user.is_superuser = True
                    user.is_staff = True
                elif valid_user['role'] == 'webuser':
                    # human user may login
                    # create a webuser group if not exists
                    (group, groupcreated) = Group.objects.get_or_create(name='webuser')
                    user.is_staff = True
                elif valid_user['role'] == 'serviceuser':
                    # uses the webservices only
                    # create a serviceuser group if not exists
                    (group, groupcreated) = Group.objects.get_or_create(name='serviceuser')
                else:
                    return None
                # save user
                user.save()

                if group:
                    # save group if a new group has been created
                    if groupcreated:
                        group.save()
                    # add user to group and save the user again
                    user = User.objects.get(username=valid_user['username'])
                    user.groups.add(group)
                    user.save()

            return user

        return None

    #------------------------------------------------------------------------------------------#

    def get_user(self, user_id):
        """
        Not really in use for now
        :param user_id:
        :return:
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None