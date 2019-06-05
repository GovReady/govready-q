import os

from django.utils.crypto import get_random_string
from siteapp.models import User, Organization

def _getpath(model):
    return os.path.dirname(os.path.realpath(__file__)) + ("/TMP_%s.idlist" % model._meta.db_table)

def create_user(username=None):
    if username == None:
        username = get_random_string(16)

    with open(_getpath(User), 'a+') as file:
        u = User.objects.create(
            username=username,
            email=("testuser_%s@govready.com" % username),
        )
        file.write(str(u.id))
        file.write("\n")

def delete_users():
    with open(_getpath(User), 'r') as file:
        id_list = [int(x) for x in file.readlines()]
        User.objects.filter(id__in=id_list).delete()
        print("cleared user IDs: " + str(id_list))
    # truncate the file
    with open(_getpath(User), 'w') as file:
        file.write('');
