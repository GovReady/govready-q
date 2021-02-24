# pylint: disable=C0116
# Missing function docstrings
import os
import secrets

from django.utils.crypto import get_random_string
from siteapp.models import User, Portfolio
from guidedmodules.models import TaskAnswer

TMP_BASE_PATH = "/tmp/govready-q/datagen"
rand = secrets.SystemRandom()  # Initialize secure random generator

os.makedirs(TMP_BASE_PATH, exist_ok=True)


# Returns a list of length count of randomly placed items in choices
def generate_sample(choices, count):
    return list(secrets.choice(choices) for _num in range(count))


def get_file_dir():
    return os.path.dirname(os.path.realpath(__file__))


wordlists = {}


def get_wordlist(path="eff_short_wordlist_1.txt"):
    global wordlists
    if path not in wordlists:
        with open(get_file_dir() + "/" + path, 'r') as file:
            wordlists[path] = [line.split("\t")[-1].rstrip()
                               for line in file.readlines()
                               if line[0] != '#']
    return wordlists[path]


def _getpath(model):
    return TMP_BASE_PATH + ("/%s.idlist" % model._meta.db_table)


def get_name(count, separator=' ', path='eff_short_wordlist_1.txt', filter=[]):
    wordlist = get_wordlist(path=path)
    if len(filter) >= len(wordlist) ** count:
        raise Exception("Cannot get a unique name for this entity")
    name = None
    while name is None:
        name = separator.join([name.title() for name in generate_sample(wordlist, count)])
        if name in filter:
            name = None
    return name


def get_random_sentence():
    # Potential future improvement: generate some lorem ipsum instead
    count = rand.randint(5, 10)
    wordlist = get_wordlist()
    words = ' '.join(generate_sample(wordlist, count))
    return words


def get_random_paragraph():
    count = rand.randint(2, 5)
    sents = [get_random_sentence() + '.' for x in range(0, count)]
    return '\n\n'.join(sents)


def get_random_email():
    wordlist = get_wordlist()
    word = generate_sample(wordlist, 1)[0]
    return "{}@example.com".format(word)


def get_random_url():
    wordlist = get_wordlist()
    word = generate_sample(wordlist, 1)[0]
    return "http://example.com/some_path/{}".format(word)


def create_user(username=None, password=None, pw_hash=None):
    if username is None:
        username = get_name(1, '_', path='names.txt', filter=[u.username for u in User.objects.all()])
    if password is None:
        password = get_random_string(16)

    with open(_getpath(User), 'a+') as file:
        u = User.objects.create(
            username=username,
            first_name=username,
            last_name='Smith', # decent enough generic last name for a US professional context
            email=("%s@govready.com" % username),
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


def create_portfolio(user):
    portfolio = Portfolio.objects.create(title=user.username)
    portfolio.assign_owner_permissions(user)


def delete_objects(model):
    with open(_getpath(model), 'r') as file:
        id_list = [int(x) for x in file.readlines()]
        model.objects.filter(id__in=id_list).delete()
        print("cleared " + str(model) + " IDs: " + str(id_list))
    # truncate the file
    with open(_getpath(model), 'w') as file:
        file.write('')


def answer_randomly(task, dummy_user, overwrite=False, halt_impute=True, skip_impute=False, quiet=False):
    def log(item):
        if not quiet:
            print(item)

    current_answers = [x for x in task.get_current_answer_records()]

    # we want to communicate back to the caller whether this was fully skipped or not
    did_anything = False

    for question in task.module.questions.order_by('definition_order'):
        type_t = question.spec['type']

        if type_t == 'raw':
            print("'raw' question type is out-of-scope, skipping")
            continue

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

        answer = None
        if type_t == 'yesno':
            answer = generate_sample(['yes', 'no'],1)[0]
        elif type_t == 'text':
            answer = get_random_sentence()
        elif type_t == 'longtext':
            answer = get_random_paragraph()
        elif type_t == 'choice':
            answer = generate_sample(question.spec['choices'], 1)[0]['key']
        elif type_t == 'multiple-choice':
            choices = question.spec['choices']
            amount = rand.randint(question.spec['min'], len(choices))
            answer = [x['key'] for x in generate_sample(choices, amount)]
        elif type_t == 'datagrid':
            choices = question.spec['fields']
            amount = rand.randint(question.spec['min'], len(choices))
            answer = [x['key'] for x in generate_sample(choices, amount)]
        elif type_t == 'module' and 'module-id' in question.spec:
            subtask = task.get_or_create_subtask(dummy_user, question, create=True)
            log("doing subtask")
            did_anything = True
            continue

        if not answer and type_t not in ('interstitial', 'raw'):
            print("Cannot answer question of type '" + type_t + "'")
            continue

        did_anything = True
        
        log(str((question.key, type_t, answer)))
        taskans, isnew = TaskAnswer.objects.get_or_create(task=task, question=question)

        from guidedmodules.answer_validation import validator
        try:
            value = validator.validate(question, answer)
        except ValueError as err:
            print("Answering {}: {}...".format(question.key, err))
            #return False
            break
        except Error as err:
            print("------\nUnknown error occurred, debug info follows.\n")
            print("Next line is: 'str((question.key, type_t, answer, question.spec))'")
            print(str((question.key, type_t, answer, question.spec)))
            print("------")
            raise err

        # Save the value.
        if taskans.save_answer(value, [], None, dummy_user, "api"):
            log("Answered {} with {}...".format(question.key, answer))
        else:
            log("No change?")
            break

        return did_anything
