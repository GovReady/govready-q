import argparse

from core.prompts import Prompt
from core.runner import DockerCompose

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='GovReadyQ Local Development')
    parser.add_argument('action', help='The action to take', default=None, nargs='?')
    parser.add_argument('--clean', help='Will wipe the database and other artifacts for a clean run', action='store_true')

    args = vars(parser.parse_args())
    valid_actions = ['init', 'remove', 'wipedb', None]
    if args['action'] not in valid_actions:
        valid_actions = [x for x in valid_actions if x]
        Prompt.error(f"{args['action']} is not a valid choice.  Choices: {valid_actions}.  "
                     f"Leave blank to run stack.", close=True)

    compose = DockerCompose()
    if args['clean']:
        compose.wipe_db()
    if args['action'] == 'init':
        compose.generate_config()
    elif args['action'] == 'remove':
        compose.remove()
    elif args['action'] == 'wipedb':
        compose.wipe_db()
    else:
        compose = DockerCompose()
        compose.run()
        compose.on_complete()
        compose.cleanup()
