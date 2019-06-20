import os
from random import sample

from django.utils.crypto import get_random_string
from siteapp.models import User, Organization
from guidedmodules.models import Task, TaskAnswer

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

def create_user(username=None, password=None, pw_hash=None):
    if username == None:
        username = get_name(3, '_').lower()
    if password == None:
        password = get_random_string(16)

    with open(_getpath(User), 'a+') as file:
        u = User.objects.create(
            username=username,
            email=("testuser_%s@govready.com" % username),
        )
        if pw_hash:
            u.password = pw_hash
        else:
            u.clear_password = password
            u.set_password(u.clear_password)
        u.save()
        file.write(str(u.id))
        file.write("\n")
    return u 

def create_organization(name=None, admin=None, help_squad=[], reviewers=[]):
    if name == None:
        name = get_name(2).upper()
    subdomain = name.replace(' ', '-').lower()

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

def answer_randomly(task, overwrite=False, halt_impute=True, skip_impute=False):
    current_answers = [x for x in task.get_current_answer_records()]
    for question in task.module.questions.order_by('definition_order'):
        if (halt_impute or skip_impute) and 'impute' in question.spec:
            print("'impute' handling not yet implemented, skipping " + question.key)
            if halt_impute:
                break
            continue

        if not overwrite:
            has_answer = len([x for x in current_answers if x[1] and x[0].key == question.key]) > 0
            if has_answer:
                print("Already answered " + question.key)
                continue

        type = question.spec['type']
        answer = None
        if type == 'yesno':
            answer = sample(['yes', 'no'],1)[0]
        if type == 'text':
            answer = get_random_string(20)
        if type == 'choice' or type == 'multiple-choice':
            answer = sample(question.spec['choices'], 1)[0]['key']
        if type == 'multiple-choice':
            # TODO make this handle a random number of choices, rather than just 1 choice each time
            answer = [x['key'] for x in sample(question.spec['choices'], 1)]
        
        if not answer and type != 'interstitial':
            print("Cannot answer question of type '" + type + "'")
            continue
        
        print(str((question.key, type, answer)))
        taskans, isnew = TaskAnswer.objects.get_or_create(task=task, question=question)

        from guidedmodules.answer_validation import validator
        try:
            value = validator.validate(question, answer)
        except ValueError as e:
            print("Answering {}: {}...".format(question.key, e))
            #return False
            break

        # Save the value.
        dummy_user = User.objects.all()[0]
        if taskans.save_answer(value, [], None, dummy_user, "api"):
            print("Answered {} with {}...".format(question.key, answer))
        else:
            print("No change?")
            break


import requests
import parsel
def login(username, password, domain):
    session = requests.Session()
    response = session.get(domain)
    return parsel.Selector(text=response.text)
