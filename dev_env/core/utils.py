import json
import os
import signal
import subprocess
import sys
import multiprocessing
from abc import ABC
from contextlib import closing
from urllib.parse import urlparse

from .prompts import Prompt, Colors


class BackgroundSubprocess(multiprocessing.Process):
    def __init__(self, cmd, display_stdout=True, on_error_fn=None):
        self.stdout = None
        self.stderr = None
        self.cmd = cmd
        self.display_stdout = display_stdout
        self.on_error_fn = on_error_fn
        super().__init__()

    def run(self):
        env = os.environ.copy()
        with subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE,  stderr=subprocess.DEVNULL,
                              bufsize=0, env=env) as proc:
            try:
                for line in proc.stdout:
                    formatted = line.rstrip().decode('utf-8', 'ignore')
                    if self.display_stdout:
                        print(formatted)
            except:
                pass
        if proc.returncode != 0:
            if self.on_error_fn:
                self.on_error_fn()


class HelperMixin:

    BACKGROUND_PROCS = []

    def __init__(self):
        self.ROOT_DIR = os.path.abspath(os.path.join(os.getcwd(), '..'))
        signal.signal(signal.SIGINT, self.signal_handler)
        self.kill_captured = False
        self.check_if_docker_is_started()

    def check_if_docker_is_started(self):

        def offline():
            Prompt.error("Docker Engine is offline.  Please start before continuing.")
            sys.exit(1)

        self.execute("docker info", {}, display_stdout=False, show_notice=False, on_error_fn=offline,
                     display_stderr=False)

    def create_secret(self):
        import secrets
        alphabet = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        return ''.join(secrets.choice(alphabet) for i in range(50))

    def check_if_valid_uri(self, x):
        try:
            result = urlparse(x)
            return all([result.scheme, result.netloc])
        except:
            return False

    def cleanup(self):
        for proc in self.BACKGROUND_PROCS:
            proc.terminate()

    def execute(self, cmd, env_dict, display_stdout=True, on_error_fn=None, show_env=False, show_notice=True,
                exit_on_fail=True, threaded=False, display_stderr=True):
        env = os.environ.copy()
        normalized_dict = {}
        for key, value in env_dict.items():
            if isinstance(value, (list, dict)):
                value = json.dumps(value)
            if value is None:
                value = ""
            normalized_dict[key] = value
        env.update(normalized_dict)
        output = ""
        if show_notice:
            Prompt.notice(f"Executing command: {Colors.WARNING}{cmd}")
            if show_env:
                Prompt.notice(f"Environment Variables: {json.dumps(env_dict, indent=4, sort_keys=True)}")
        if threaded:
            proc = BackgroundSubprocess(cmd, display_stdout=display_stdout, on_error_fn=on_error_fn)
            proc.daemon = True
            proc.start()
            self.BACKGROUND_PROCS.append(proc)
        else:
            args = dict(stdout=subprocess.PIPE, bufsize=0, env=env, shell=True)
            if not display_stderr:
                args.update(dict(stderr=subprocess.DEVNULL))
            with subprocess.Popen(cmd, **args) as proc:
                for line in proc.stdout:
                    formatted = line.rstrip().decode('utf-8', 'ignore')
                    output += formatted
                    if display_stdout:
                        print(formatted)
            if proc.returncode != 0:
                if on_error_fn:
                    on_error_fn()
                Prompt.error(f"[{cmd}] Failed [code:{proc.returncode}]- {proc.stderr}", close=exit_on_fail)
            return output

    def signal_handler(self, sig, frame):
        Prompt.notice("\nCtrl-c captured.  Executing teardown function.")
        if not self.kill_captured:
            self.kill_captured = True
            self.on_sig_kill()
        sys.exit(0)

    def on_sig_kill(self):
        raise NotImplementedError()

    def on_complete(self):
        raise NotImplementedError()

    def on_fail(self):
        raise NotImplementedError()

    def check_if_container_is_ready(self, name):
        return self.execute(cmd="docker inspect --format=\"{{json .State.Health.Status}}\" " + name,
                            env_dict={}, exit_on_fail=True,
                            display_stdout=False, show_notice=False)


class Runner(HelperMixin, ABC):
    REQUIRED_PORTS = []  # Verifies to see if ports are available

    def execute(self, cmd, env_dict=None, display_stdout=True, on_error_fn=None, show_env=False, show_notice=True,
                exit_on_fail=True, threaded=False, display_stderr=True):
        if not env_dict:
            env_dict = {}
        return super().execute(cmd,
                               display_stdout=display_stdout,
                               env_dict=env_dict,
                               show_notice=show_notice,
                               threaded=threaded,
                               exit_on_fail=exit_on_fail,
                               display_stderr=display_stderr,
                               on_error_fn=on_error_fn if on_error_fn else self.on_fail, show_env=show_env)

    def check_ports(self, raise_exception=True):
        Prompt.notice(f"Checking if ports are available for deployment: {self.REQUIRED_PORTS}")
        import socket
        ports_in_use = []
        for port in self.REQUIRED_PORTS:
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                if sock.connect_ex(('127.0.0.1', port)) == 0:
                    ports_in_use.append(port)
        if ports_in_use and raise_exception:
            Prompt.error(f"Cannot deploy.  The following ports are in use: {ports_in_use}", close=True)
        return bool(ports_in_use)

    def run(self):
        raise NotImplementedError()
