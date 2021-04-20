import json
import os
import re
import shutil
import time

from core.prompts import Prompt, Colors
from core.utils import Runner


class DockerCompose(Runner):
    REQUIRED_PORTS = [8000]

    def generate_config(self):
        config = {
            "admins": [],
            "branding": "",
            "db": "postgres://postgres:PASSWORD@postgres_dev:5432/govready_q",
            "debug": True,
            "email": {},
            "govready_cms_api_auth": "",
            "govready-url": "http://localhost:8000",
            "mailgun_api_key": "",
            "memcached": "",
            "secret-key": self.create_secret(),
            "gr-pdf-generator": "wkhtmltopdf",
            "gr-img-generator": "wkhtmltopdf",
            "single-organization": "",
            "static": "static_root",
            "syslog": "",
            "trust-user-authentication-headers": ""
        }
        with open("docker/environment.json", 'w') as f:
            json.dump(config, f, indent=4, sort_keys=True)
        return config

    def on_fail(self):
        self.execute(cmd=f"docker-compose logs")
        self.on_sig_kill()

    def on_complete(self):
        logs = self.execute(cmd=f"docker-compose logs", display_stdout=False, show_notice=False)
        auto_admin = re.findall(
            'Created administrator account \(username: (admin)\) with password: ([a-zA-Z0-9#?!@$%^&*-]+)', logs)
        print()

        Prompt.warning(f"Access application via Browser: {Colors.CYAN}{self.config['govready-url']}")
        Prompt.warning(f"View logs & debug by running: {Colors.CYAN}docker attach govready_q_dev")
        Prompt.warning(f"Connect to container: {Colors.CYAN}docker exec -it govready_q_dev /bin/bash")
        Prompt.warning(f"Testing: {Colors.CYAN}docker exec -it govready_q_dev ./manage.py test")

        creds_path = os.path.join(self.ROOT_DIR, 'local/admin.creds.json')
        if auto_admin:
            with open(creds_path, 'w') as f:
                json.dump({"username": auto_admin[0][0], "password": auto_admin[0][1]}, f)
        else:
            if os.path.exists(creds_path):
                with open(creds_path, 'r') as f:
                    creds = json.load(f)
                auto_admin = [[creds['username'], creds['password']]]

        if auto_admin:
            Prompt.warning(f"Administrator Account - "
                           f"{Colors.CYAN}{auto_admin[0][0]} / {auto_admin[0][1]} - {Colors.FAIL}"
                           f" This is stored in local/admin.creds.json")

    def on_sig_kill(self):
        self.execute(cmd="docker-compose down --remove-orphans  --rmi all")

    def remove(self):
        os.chdir(f"docker")
        self.execute(cmd=f"docker-compose down --remove-orphans  --rmi all")

    def wipe_db(self):
        cwd = os.getcwd()
        os.chdir(f"docker")
        self.execute(cmd=f"docker-compose down --remove-orphans  --rmi all -v")
        file_path = os.path.abspath(os.path.join(self.ROOT_DIR, "local"))
        if os.path.exists(file_path):
            shutil.rmtree(file_path)
        os.chdir(cwd)

    def run(self):
        Prompt.warning(f"Attempting to start developer environment via docker-compose")
        if not os.path.exists("docker/environment.json"):
            self.config = self.generate_config()
        else:
            with open("docker/environment.json", 'r') as f:
                self.config = json.load(f)

        os.chdir(f"docker")
        self.execute(cmd=f"docker-compose down --remove-orphans  --rmi all")
        self.check_ports()
        self.execute(cmd=f"docker-compose build --parallel", show_env=True)
        self.execute(cmd=f"docker-compose up -d", show_env=True)
        self.execute(cmd=f"docker-compose logs -f", show_env=True, threaded=True)

        Prompt.warning("Waiting for stack to come up...")
        while True:
            status = self.check_if_container_is_ready("govready_q_dev")
            if status == '"healthy"':
                break
            time.sleep(1)
