# Installing GovReady-Q

## System Requirements

* A Windows 10, Mac, or Linux computer with [Python 3](https://www.python.org/downloads/) and Git installed.
* Python 3.6 or higher will be required.
  * On Macs, you should already have Python 3 and Git installed.
  * On Windows, you may need to install a [Windows version of Python](https://www.python.org/downloads/windows/), and [Git for Windows](https://gitforwindows.org/) or a [Windows version of Git](https://git-scm.com/download/win).  Or, you can use [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/install-win10).
* Access to a command line, to run Python and Git commands.
* 300-500 MB of free disk space to install GovReady-Q. The installed files will be in the GovReady-Q directory, and you may delete that directory after the test.
* Internet access or alternative resources:
  * Access to repositories with appropriate operating systems packages for OS dependencies.
  * Access to https://github.com/GovReady/govready-q, https://govready.com/govready-q/download, or another repository with GovReady-Q source code
  * Access to https://pypi.org/simple or local mirror of Pypi to install Python dependencies. 
* On macOS, installation of some additional dependencies.

## Before You Install

For Mac, Linux, or Windows Subsystem for Linux, please find the `install.md` file and follow the instructions there.

## Before You Install - Windows

(This section is under construction.)

## Install Instructions

Start your command line shell.

Go to a directory that you can download GovReady-Q into.  If you wish, you can create a new directory, and change directory into it.

### 1. Clone GovReady-Q

Do these shell commands.

```shell
git clone https://github.com/GovReady/govready-q.git
cd govready-q
```

### 2. Create and Activate Python Virtual Environment

Do these shell commands.

```shell
py -m venv venv
venv/scripts/activate.bat
```

You should see "(venv)".

Your prompt may or may not change to include "venv".

### 3. Run Installer

Do this shell command for to see all install options.

```shell
python3 install.py -h
```

The script will print command options.

```shell
>>>>>>>>>> Welcome to the GovReady-Q Installer <<<<<<<<<

usage: install.py [-h] [--non-interactive] [--timeout TIMEOUT] [--user]
                  [--verbose]

Quickly set up a new GovReady-Q instance from a freshly-cloned repository.

optional arguments:
  -h, --help            show this help message and exit
  --non-interactive, -n
                        run without terminal interaction
  --timeout TIMEOUT, -t TIMEOUT
                        seconds to allow external programs to run
                        (default=120)
  --user, -u            do pip install with --user
```


Do this shell command for default install.

```shell
python3 install.py
```

The script will print progress messages. Some of the steps may take a minute or several minutes.

If you are asked a yes/no question, answer as appropriate.

You can hit Control-C at any point to stop the install.

The output will begin something like this:

```
>>>>>>>>>> Welcome to the GovReady-Q Installer <<<<<<<<<

Testing environment...

Platform is Darwin version 20.3.0 running on x86_64.

====

Python version is 3.8.2.
+ Python version is >= 3.8.
```

If the install and configuration completes properly, you should see something like this:

```
***********************************
* GovReady-Q Server configured... *
***********************************

To start GovReady-Q, run:
    ./manage.py runserver

Log in with the administrator credentials below.

WRITE THIS DOWN:

Created administrator account (username: admin) with password: xxxxxxxxxxxx

When GovReady-Q is running, visit http://localhost:8000/ with your web browser.
```

Congratulations, you have installed GovReady-Q!
