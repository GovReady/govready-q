import os, json, sys
import dj_database_url

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_NAME = "siteapp"

def env_dict():
    '''
    return a dict with the mappings from environment variable
    to the key names for local/environment.json, and expected types
    '''
    return {
        'SECRET_KEY': ('secret-key', str),
        'DEBUG': ('debug', bool),
        'HOST': ('host',  str),
        'HTTPS': ('https',  bool),
        'ADMINS': ('admins',  list),
        'MEMCACHED': ('memcached', bool),
        'STATIC': ('static',  str),
        'MODULES_PATH': ('modules', str),
        'GOVREADY_CMS_API_AUTH': ('govready_cms_api_auth', str)
    }

def populate_env(input_dict):
    '''
    Return an environment dict based on environment vars
    '''
    environment = {}
    for key in input_dict.keys():
        if os.getenv(key):
            if (input_dict[key][1] == list):
                # split lists at the : character
                environment[input_dict[key][0]] = os.environ[key].split(':')
            else:
                # convert to str or bool, as needed
                environment[input_dict[key][0]] = input_dict[key][1](os.environ[key])
    return (environment)

def populate_email():
    '''
    Return a dictionary with EMAIL settings
    by parsing a url like: 'email://eric:allman@mailhost:465'
    '''
    if not os.getenv('EMAIL'):
        return {}
    from urllib.parse import urlparse
    url = urlparse(os.environ.get('EMAIL'))
    return {
        'host': url.hostname,
        'port': url.port,
        'user': url.username,
        'pw': url.password
    }

def populate_db():
    '''
    Return a dictionary with DATABASE_URL settings
    '''
    if not os.getenv('DATABASE_URL'):
        return {}
    db = dj_database_url.config()
    return db

def all():
    '''
    Gather all the environment settings from other functions,
    so we can test for empty environment
    '''
    environment = populate_env(env_dict())
    em = populate_email()
    if em.keys(): environment['email'] = em
    db = populate_db()
    if db.keys(): environment['db'] = db
    return environment

def write_local(e):
    '''
    Hardcoded to write to ./siteapp/local/environment.json
    '''
    local_dir = os.path.join(BASE_DIR, APP_NAME, 'local')
    json_path = os.path.join(local_dir, 'environment.json')
    if e != {}:
        if not os.path.exists(local_dir):
            os.mkdir(local_dir)
        with open(json_path, 'w') as f:
            json.dump(e, f, indent=2, sort_keys=True)
            f.close()
    else:
        print("Empty environ, not writing any file", file=sys.stderr)

def main():
    environment = all()
    write_local(environment)

if __name__ == "__main__":
    # execute only if run as a script
    main()
