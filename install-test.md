# Testing GovReady-Q Install Script

Thank you for testing the GovReady-Q Install Script!

This document version: 2021-03-07-002

## System Requirements

* A Windows, Mac, or Linux computer with [Python 3](https://www.python.org/downloads/) and Git installed.
* Python 3.6 or higher will be required, but we are interested in seeing how the script responds to versions < 3.6, so please don't upgrade Python right away if you have a lower version.
  * On Macs, you should already have Python 3 and Git installed.
  * On Macs, you should already have Python 3 and Git installed.
  * On Windows, you may need to install a [Windows version of Python](https://www.python.org/downloads/windows/), and [Git for Windows](https://gitforwindows.org/) or a [Windows version of Git](https://git-scm.com/download/win).  Or, you can use [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/install-win10).
* Access to a command line, to run Python and Git commands.
* 300-500 MB of free disk space to install GovReady-Q. The installed files will be in the GovReady-Q directory, and you may delete that directory after the test.
* Internet access or alternative resources:
  * Access to repositories with appropriate operating systems packages for OS dependencies.
  * Access to https://github.com/GovReady/govready-q, https://govready.com/govready-q/download, or another repository with GovReady-Q source code
  * Access to https://pypi.org/simple or local mirror of Pypi to install Python dependencies. 
* On macOS, installation of some additional dependencies.
* A way to report results back -- either with screenshots or by copy/pasting text from your command shell.
  * Email feedback to [Dayton Williams](mailto:dayton.williams@govready.com) ([dayton.williams@govready.com](dayton.williams@govready.com)).
  * There are instructions to [take a screenshot on your Mac](https://support.apple.com/en-us/HT201361).
  * There are instructions to [use Snipping Tool to capture screenshots on Windows](https://support.microsoft.com/en-us/windows/use-snipping-tool-to-capture-screenshots-00246869-1843-655f-f220-97299b865f6b).

## Goals

You will download a copy of the GovReady-Q source code using Git.

You will run the GovReady-Q Install Script.

The GovReady-Q Install Script will do additional configuration and download additional libraries and assets.

The configuration may run to completion, and you'll be able to start GovReady-Q, or it may run into expected or unexpected issues, and the configuration will stop.

If it worked, you'll run GovReady-Q and see its start page.

If it didn't work, you'll mostly likely get error messages.  Please report (screenshot or copy/paste) any error information you see, and any other relevant information: kind of computer, which OS version, which Python version, anything you did or didn't do that might have caused problems for the Installer, etc.

Please also give us any comments, questions, or concerns you have about the install process.

At the end of your testing, you may delete the GovReady-Q directory to reclaim the disk space.

## Before You Install - Windows

(This section has not been completed yet.)

## Before You Install - Ubuntu

Some additional dependencies are required for Linux Ubuntu.

Do these shell commands to update package list.

```shell
# Update package list
apt-get update
apt-get upgrade
```

Do these shell commands to install the OS dependencies for GovReady-Q.

```shell
# Install dependencies
DEBIAN_FRONTEND=noninteractive \
apt-get install -y \
unzip git curl jq \
python3 python3-pip \
python3-yaml \
graphviz pandoc \
language-pack-en-base language-pack-en
```

## Before You Install - CentOS 8, RHEL 8, Fedora 8

Some additional dependencies are required for Linux CentOS, RHEL, Fedora.

Do these shell commands to update package list.

```shell
# Update package list
dnf update
```

Do these shell commands to install the OS dependencies for GovReady-Q.

```shell
# Install dependencies
dnf install \
python3 python3-devel gcc-c++.x86_64 \
unzip git jq \
graphviz

# for pandoc, enable PowerTools repository
dnf install dnf-plugins-core
dnf config-manager --set-enabled PowerTools
dnf install pandoc
```

## Before You Install - macOS

Some additional dependencies are required for macOS.

Temporary setup instructions (temporary because they may need to be cleaned up and/or fleshed out.)

Do this shell command.

```shell
xcode-select --install
```

(See [How to fix the xcrun invalid active developer path error in macOS](https://flaviocopes.com/fix-xcrun-error-invalid-active-developer-path/) for more complete instructions.)

If you get an error that command line tools are already installed, just proceed.

Next, install Homebrew, if it is not already installed.  This is one way to get started.

```shell
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

(For more details, see [Installation — Homebrew Documentation](https://brew.sh/).)

After Homebrew is installed, do this shell command.

```shell
brew install libmagic
```

If you get a warning that libmagic is already installed, just proceed.

After Homebrew is installed, do this shell command.

```shell
brew install postgresql
```

If you get a warning that postgresql is already installed, just proceed.

[Note, this is needed to resolve this dependency: "Error: pg_config executable not found. pg_config is required to build psycopg2 from source." We should just move this dependency out to a pg_requirements file.]

## Install Instructions

Start your command line shell.

Go to a directory that you can download GovReady-Q into.  If you wish, you can create a new directory, and change directory into it.

Do these shell commands.

```shell
git clone https://github.com/GovReady/govready-q.git
cd govready-q
git checkout install-test-001
```

You should see:

```
Branch 'install-test-001' set up to track remote branch 'install-test-001' from 'origin'.
Switched to a new branch 'install-test-001'
```

On Windows, do these shell commands.

```shell
py -m venv venv
venv\scripts\activate.bat
```

On Mac, do these shell commands.

```shell
python3 -m venv venv
source venv/bin/activate
```

You should not see any output.  Your prompt may or may not change to include "venv".

[may need `pip3 install --upgrade pip`]

## Test 1 - check for help message

Do these shell commands.

```shell
./install.py --help
python3 install.py --help
```

They should both print usage help and a list of command-line arguments.

If the output from both is the same, then in the instructions below, you can use either form of the command (without specifing `--help`).

If they have different output, please let us know, and only use the form that printed the usage help.

## Test 2 - try a default install

Do this shell command.

```shell
python3 install.py
```

The script will print progress messages.  Some of the steps may take a minute or several minutes.

If you are asked a yes/no question, answer with "n".

You can hit Control-C at any point to stop the install.

If the script stops with an error, please share the results with us.

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

If you see a similar message, go ahead and try to run GovReady-Q.

```shell
./manage.py runserver
```

You will see some INFO and WARNING messages printed, and then you should see the following:

```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

Using a web browser, visit http://localhost:8000/

Some more messages will print in the command shell.  GovReady-Q should load in your browser.

Sign in with the username `admin` and the password that printed in your command shell.

When you're ready, stopy GovReady-Q by hitting Control-C in your command shell.

Let us know you were successful!

## Test 3 - try a verbose install

Do this shell command.

```shell
python3 install.py --verbose
```

The script will print progress messages.  Some of the steps may take a minute or several minutes.

In the verbose output, some lines will have WARNING or ERROR messages. Typically, these are normal and expected.  But if the script stops without 

If you are asked a yes/no question, answer with "n".

You can hit Control-C at any point to stop the install.

If the script stops with an error, please share the results with us.

When you see this message:

```
***********************************
* GovReady-Q Server configured... *
***********************************

To start GovReady-Q, run:
    ./manage.py runserver

Administrator account(s) previously created.

When GovReady-Q is running, visit http://localhost:8000/ with your web browser.
```

Sign in as you did in Test 2, with the same credentials.

Let us know you were successful!

## Test 4 - try a verbose install after removing created config files

In this test, we will delete some configuration files that were generated.

(This section will describe how to remove `local/db.sqlite3` and `environment.json` in the various OSes, and will repeat Test 3.  Since we removed the database, the administrator credentials will be regenerated, as in Test 2.  Until this section is written, this test is optional; feel free to do it if you understand this summary and what to do, or feel free to skip this test.)

