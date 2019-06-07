import os
from random import sample

from django.utils.crypto import get_random_string
from siteapp.models import User, Organization

def get_file_dir():
    return os.path.dirname(os.path.realpath(__file__))

wordlist = None 
def get_wordlist(path="eff_short_wordlist_1.txt"):
    global wordlist
    if wordlist == None:
        with open(get_file_dir() + "/" + path, 'r') as file:
            wordlist = [line.split("\t")[-1].rstrip() for line in file.readlines() if line[0] != '#']
    return wordlist
        

def _getpath(model):
    return get_file_dir() + ("/TMP_%s.idlist" % model._meta.db_table)

def get_name(count, separator=' '):
    wordlist = get_wordlist()
    return separator.join([name.title() for name in sample(wordlist, count)])

def create_user(username=None, password=None):
    if username == None:
        username = get_name(2, '_').lower()
    if password == None:
        password = get_random_string(16)

    with open(_getpath(User), 'a+') as file:
        u = User.objects.create(
            username=username,
            email=("testuser_%s@govready.com" % username),
        )
        u.clear_password = password
        u.set_password(u.clear_password)
        u.save()
        file.write(str(u.id))
        file.write("\n")
    return u 

def create_organization(name=None, admin=None, help_squad=[], reviewers=[]):
    if name == None:
        name = get_name(1).upper()
    subdomain = name.lower()

    with open(_getpath(Organization), 'a+') as file:
        org = Organization.create(
            name=name,
            subdomain=subdomain,
            admin_user=admin,
        )
        file.write(str(org.id))
        file.write("\n")

    for user in help_squad:
        org.help_squad.add(user)
    for user in reviewers:
        org.reviewers.add(user)
    return org 


def delete_objects(model):
    with open(_getpath(model), 'r') as file:
        id_list = [int(x) for x in file.readlines()]
        model.objects.filter(id__in=id_list).delete()
        print("cleared " + str(model) + " IDs: " + str(id_list))
    # truncate the file
    with open(_getpath(model), 'w') as file:
        file.write('');
