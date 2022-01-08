import argparse

from core.prompts import Prompt
from core.runner import DockerCompose

if __name__ == '__main__':
    valid_actions = ['init', 'dev', 'remove', 'wipedb']

    parser = argparse.ArgumentParser(description='GovReadyQ Local Development')
    parser.add_argument('action', help=f'The action to take.  Options: {valid_actions}')
    parser.add_argument('--clean', help='Will wipe the database and other artifacts for a clean run', action='store_true')
    parser.add_argument('--amd64', help='Will add DOCKER_DEFAULT_PLATFORM=linux/amd64 to docker commands',
                        action='store_true')

    args = vars(parser.parse_args())
    valid_actions = ['init', 'dev', 'remove', 'wipedb']
    if args['action'] not in valid_actions:
        Prompt.error(f"{args['action']} is not a valid choice.  Choices: {valid_actions}.", close=True)

    compose = DockerCompose(amd=args['amd64'])
    if args['clean']:
        compose.wipe_db()
    if args['action'] == 'init':
        compose.generate_config()
    elif args['action'] == 'remove':
        compose.remove()
    elif args['action'] == 'wipedb':
        compose.wipe_db()
    else:
        compose.run()
        compose.on_complete()
        compose.cleanup()
