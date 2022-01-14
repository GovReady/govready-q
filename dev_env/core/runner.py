import json
import os
import re
import shutil
import time

from core.prompts import Prompt, Colors
from core.utils import Runner


class DockerCompose(Runner):
    REQUIRED_PORTS = [8000, 5432]
    compose_files = ['docker-compose.yml']

    def __init__(self, amd):
        super().__init__()
        self.amd = amd

    def build_docker_compose_command(self):
        command = f"docker-compose {' '.join([f'-f {x}' for x in self.compose_files])}"
        if self.amd:
            return f"DOCKER_DEFAULT_PLATFORM=linux/amd64 {command}"
        return command

    def generate_config(self):
        config = {
            "admins": [],
            "branding": "",
            "db": "postgres://postgres:PASSWORD@postgres_dev:5432/govready_q",
            "debug": True,
            "enable_toolbar": False,
            "email": {},
            "govready_cms_api_auth": "",
            "govready-url": "http://localhost:8000",
            "mailgun_api_key": "",
            "memcached": False,
            "okta": {},
            "secret-key": self.create_secret(),
            "gr-pdf-generator": "wkhtmltopdf",
            "gr-img-generator": "wkhtmltopdf",
            "session_security_expire_at_browser_close": True,
            "session_security_warn_after": 1200,
            "session_security_expire_after": 1800,
            "single-organization": "",
            "static": "static_root",
            "syslog": "",
            "test_browser": "chrome",
            "test_visible": False,
            "trust-user-authentication-headers": {}
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
        Prompt.title_banner(f"Service - Backend - Django Application", True)
        Prompt.warning(f"Access application via Browser: {Colors.CYAN}{self.config['govready-url']}")
        Prompt.warning(f"Access api docs via Browser: {Colors.CYAN}{self.config['govready-url']}/api/v2/docs/swagger/")
        Prompt.warning(f"View logs & debug by running: {Colors.CYAN}docker attach govready-q-dev")
        Prompt.warning(f"Connect to container: {Colors.CYAN}docker exec -it govready-q-dev /bin/bash")
        Prompt.warning(f"Testing: {Colors.CYAN}docker exec -it govready-q-dev ./manage.py test")

        creds_path = os.path.join(self.ROOT_DIR, 'local/admin.creds.json')
        if auto_admin:
            with open(creds_path, 'w') as f:
                json.dump({"username": auto_admin[0][0], "password": auto_admin[0][1].replace("govready-q-dev", "")}, f)
        else:
            if os.path.exists(creds_path):
                with open(creds_path, 'r') as f:
                    creds = json.load(f)
                auto_admin = [[creds['username'], creds['password']]]

        if auto_admin:
            Prompt.warning(f"Administrator Account - "
                           f"{Colors.CYAN}{auto_admin[0][0]} / {auto_admin[0][1].replace('govready-q-dev', '')} - {Colors.FAIL}"
                           f" This is stored in local/admin.creds.json")

        Prompt.title_banner(f"Service - Frontend - Webpack")
        Prompt.warning(f"View logs & debug by running: {Colors.CYAN}docker attach frontend")
        Prompt.warning(f"Connect to container: {Colors.CYAN}docker exec -it frontend /bin/sh")

        Prompt.title_banner(f"Service - Database - Postgres")
        Prompt.warning(f"View logs & debug by running: {Colors.CYAN}docker attach postgres_dev")
        Prompt.warning(f"Connect to container: {Colors.CYAN}docker exec -it postgres_dev /bin/bash")
        Prompt.warning(f"Connection String: {Colors.CYAN}{self.config['db'].replace('postgres_dev', 'localhost')}")

    def on_sig_kill(self):
        self.execute(cmd=f"{self.build_docker_compose_command()} down --remove-orphans  --rmi all")

    def remove(self):
        os.chdir(f"docker")
        self.execute(cmd=f"{self.build_docker_compose_command()} down --remove-orphans  --rmi all")

    def wipe_db(self):
        cwd = os.getcwd()
        os.chdir(f"docker")
        self.execute(cmd=f"{self.build_docker_compose_command()} down --remove-orphans  --rmi all -v")
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
        self.execute(cmd=f"{self.build_docker_compose_command()} down --remove-orphans  --rmi all")

        selenium_grid_map = {
            "grid": {"port": 4444, "file": "selenium/selenium-hub.yml"},
            "chrome": {"port": 6900, "file": "selenium/selenium-chrome.yml"},
            # "edge": {"port": 6901, "file": "selenium/selenium-edge.yml"},
            "firefox": {"port": 6902, "file": "selenium/selenium-firefox.yml"},
            "opera": {"port": 6903, "file": "selenium/selenium-opera.yml"},
        }

        if self.config['test_visible']:
            browser = self.config.get('test_browser')
            if not browser or browser not in selenium_grid_map:
                del selenium_grid_map['grid']
                Prompt.error(f"If Selenium isn't running as Headless, then you must declare a valid browser type: "
                             f"{selenium_grid_map.keys()}")
            self.REQUIRED_PORTS.append(8001)  # Live server for selenium tests
            self.REQUIRED_PORTS.append(selenium_grid_map['grid']['port'])
            self.compose_files.append(selenium_grid_map['grid']['file'])
            self.REQUIRED_PORTS.append(selenium_grid_map[browser]['port'])
            self.compose_files.append(selenium_grid_map[browser]['file'])

        self.check_ports()
        self.execute(cmd=f"{self.build_docker_compose_command()} build --parallel", show_env=True)
        self.execute(cmd=f"{self.build_docker_compose_command()} up -d", show_env=True)
        self.execute(cmd=f"docker-compose logs -f", show_env=True, threaded=True)

        Prompt.warning("Waiting for stack to come up...")
        while True:
            status = self.check_if_container_is_ready("govready-q-dev")
            if status == '"healthy"':
                break
            time.sleep(1)
