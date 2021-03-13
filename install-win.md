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

For Windows Subsystem for Linux, please find the `install.md` file and follow the instructions there.  If you are using Windows 10 directly, please continue.

These instructions assume you will be using Git Bash as your shell, and that you  will run it as administrator.  If you cannot run Git Bash as administrator, please contact your system adminstrator, or contact GovReady for more information.

### Install Python for Windows

Go to [Python Releases for Windows](https://www.python.org/downloads/windows/).

Choose an appropriate download file.

A good choice may be the "Windows installer (64-bit)" within the most recent release under "Stable Releases".

After download, run the install.  Usually you can "Install Now", which is described with "Includes IDLE, pip and documentation".  Choose "Customize installation" you need to make changes.

### Install Git for Windows

Go to [Git for Windows](https://gitforwindows.org/).

After the redirect to GitHub, scroll down to "Assets" and click the appropriate file to download.

A good choice may be "Git-x.xx.x-64-bit.exe".

After download, run the install.

During the Git install, take care to choose your desired editor on the "Choosing the default editor used by Git".  If none of the choices is familiar to you, you may wish to choose the simplest (and least powerful) editor, "Notepad".

After Git is installed, find the "Git" folder in your Start menu, and then "Git Bash". Select "Run as administrator".

### Install Visual Studio Build Tools 2019

Go to [Visual Studio Build Tools 2019](https://visualstudio.microsoft.com/visual-cpp-build-tools/).

Click "Download Build Tools".

After download, run the install.

In "Workloads", select "C++ build tools".

Click "Install".

After the install, you do not need to click "Launch". Just close the installer.

## GovReady-Q Install Instructions

Make sure you are running Git Bash as administrator.

Go to a directory that you can download GovReady-Q into.  If you wish, you can create a new directory, and change directory into it.

### 1. Clone GovReady-Q

Do these shell commands.

```shell
git clone https://github.com/GovReady/govready-q.git
cd govready-q
```

[Next step needed until `installer.py` is on the main branch.]

Do this shell command.

```shell
git checkout install-test-001-windows
```

You should see:

```
Branch 'install-test-001-windows' set up to track remote branch 'install-test-001-windows' from 'origin'.
Switched to a new branch 'install-test-001-windows'
```

### 2. Create and Activate Python Virtual Environment

Do these shell commands.

```shell
py -m venv venv
source venv/scripts/activate
```

You should see "(venv)".

### 3. Upgrade pip

You should check to see if `pip` should be upgraded.

Try this shell command.

```shell
pip install --upgrade pip
```

You may see an error, even if you ran Git Bash as administrator:

```
ERROR: Could not install packages due to an OSError: [WinError 5] Access is denied
```

This error can occur even if the `pip` upgrade was successful.

To check, run the same command again.

```shell
pip install --upgrade pip
```

If you see "Requirement already satisfied", you can proceed.

### 4. Install Additional Modules

On Windows, you need to install these additional modules.

```shell
pip install colorama python-magic-bin
```

When successful, `pip` will print:

```
Successfully installed colorama-0.x.x python-magic-bin-0.x.x
```

### 5. Run Installer

Do this shell command for to see all install options.

```shell
py install.py -h
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
py install.py
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
