import os
from random import sample, randint

from django.utils.crypto import get_random_string
from siteapp.models import User, Organization, ProjectMembership
from guidedmodules.models import Task, TaskAnswer, Module, Project

TMP_BASE_PATH="/tmp/govready-q/datagen"

os.makedirs(TMP_BASE_PATH, exist_ok=True)

def get_file_dir():
    return os.path.dirname(os.path.realpath(__file__))

wordlists = {} 
def get_wordlist(path="eff_short_wordlist_1.txt"):
    global wordlists
    if not path in wordlists:
        with open(get_file_dir() + "/" + path, 'r') as file:
            wordlists[path] = [line.split("\t")[-1].rstrip() for line in file.readlines() if line[0] != '#']
    return wordlists[path]
        

def _getpath(model):
    return TMP_BASE_PATH + ("/%s.idlist" % model._meta.db_table)

def get_name(count, separator=' ', path='eff_short_wordlist_1.txt'):
    wordlist = get_wordlist(path=path)
    return separator.join([name.title() for name in sample(wordlist, count)])


def get_random_sentence():
    # Potential future improvement: generate some lorem ipsum instead
    count = randint(5, 10)
    wordlist = get_wordlist()
    words = ' '.join(sample(wordlist, count))
    return words

def get_random_paragraph():
    count = randint(2, 5)
    sents = [get_random_sentence() + '.' for x in range(0, count)]
    return '\n\n'.join(sents)

def get_random_email():
    wordlist = get_wordlist()
    word = sample(wordlist, 1)[0]
    return "{}@example.com".format(word)

def get_random_url():
    wordlist = get_wordlist()
    word = sample(wordlist, 1)[0]
    return "http://example.com/some_path/{}".format(word)

def create_user(username=None, password=None, pw_hash=None):
    if username == None:
        username = get_name(1, '_', path='names.txt')
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
        name = get_name(2)
        name += " " + get_name(1, path='company_suffixes.txt')
    subdomain = name.replace(' ', '-').lower()

    superuser = User.objects.get(id=1)

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

    # also add the superuser as an admin, for convenience's sake
    pm, isnew = ProjectMembership.objects.get_or_create(user=superuser, project=org.get_organization_project())
    pm.is_admin = True
    pm.save()
    return org 


def delete_objects(model):
    with open(_getpath(model), 'r') as file:
        id_list = [int(x) for x in file.readlines()]
        model.objects.filter(id__in=id_list).delete()
        print("cleared " + str(model) + " IDs: " + str(id_list))
    # truncate the file
    with open(_getpath(model), 'w') as file:
        file.write('');

def answer_randomly(task, overwrite=False, halt_impute=True, skip_impute=False, quiet=False):
    
    def log(item):
        if not quiet:
            print(item)

    current_answers = [x for x in task.get_current_answer_records()]

    # sooo... sometimes we might have accidentally created a project with no admin. Use the org admin instead.
    dummy_user = task.project.organization.get_organization_project().get_admins()[0]

    for question in task.module.questions.order_by('definition_order'):
        if (halt_impute or skip_impute) and 'impute' in question.spec:
            log("'impute' handling not yet implemented, skipping " + question.key)
            if halt_impute:
                break
            continue

        if not overwrite:
            has_answer = len([x for x in current_answers if x[1] and x[0].key == question.key]) > 0
            if has_answer:
                log("Already answered " + question.key)
                continue

        type = question.spec['type']
        answer = None
        if type == 'yesno':
            answer = sample(['yes', 'no'],1)[0]
        elif type == 'text':
            answer = get_random_sentence()
        elif type == 'longtext':
            answer = get_random_paragraph()
        elif type == 'email-address':
            answer = get_random_email()
        elif type == 'url':
            answer = get_random_url()
        elif type == 'date':
            year = randint(2010, 2030)
            month = randint(1, 12)
            # stopping our day at 28 means we don't need to worry about varying month lengths
            day = randint(1, 28) 
            # internal answer format seems to be yyyy-mm-dd
            answer = "{}-{:02}-{:02}".format(year, month, day)
        elif type == 'choice':
            answer = sample(question.spec['choices'], 1)[0]['key']
        elif type == 'multiple-choice':
            choices = question.spec['choices']
            amount = randint(question.spec['min'], len(choices))
            answer = [x['key'] for x in sample(choices, amount)]
        elif type == 'module' and 'module-id' in question.spec:
            subtask = task.get_or_create_subtask(dummy_user, question, create=True)
            log("doing subtask")
            continue
        
        if not answer and type != 'interstitial':
            print("Cannot answer question of type '" + type + "'")
            continue
        
        log(str((question.key, type, answer)))
        taskans, isnew = TaskAnswer.objects.get_or_create(task=task, question=question)

        from guidedmodules.answer_validation import validator
        try:
            value = validator.validate(question, answer)
        except ValueError as e:
            print("Answering {}: {}...".format(question.key, e))
            #return False
            break

        # Save the value.
        if taskans.save_answer(value, [], None, dummy_user, "api"):
            log("Answered {} with {}...".format(question.key, answer))
        else:
            log("No change?")
            break


import requests
import parsel
def login(username, password, domain):
    session = requests.Session()
    response = session.get(domain)
    return parsel.Selector(text=response.text)
