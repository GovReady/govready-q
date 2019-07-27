Testing
=======

## Running Tests

GovReady-Q's unit tests and integration tests are currently combined. Our integration tests uses Selenium to simulate user interactions with the interface.

To run the integration tests, you'll also need to install chromedriver:

	sudo apt-get install chromium-chromedriver   (on Ubuntu)
	brew install chromedriver                    (on Mac)

Navigate within your terminal to GovReady-Q top level directory.

Then run the test suite with:

	./manage.py test

_NOTE: Depending on your Python3 configuration, you may need to run:_

	python3 manage.py test


To selectively run tests from individual modules:

	# test rendering of guided modules
	./manage.py test guidedmodules
	
	# test general siteapp logic
	./manage.py test siteapp
	
	# test discussion functionality
	./manage.py test discussion

Or to selectively run tests from individual classes or methods:

	# run tests from individual test class
	./manage.py test siteapp.tests.GeneralTests
	
	# run tests from individual test method
	./manage.py test siteapp.tests.GeneralTests.test_login


## Test Coverage Report

To produce a code coverage report, run the tests with `coverage`:

	coverage run --source='.' --branch manage.py test
	coverage report

## Code Scanning and Analysis

GovReady-Q is a Python web application written on top of the Django framework and uses a variety of industry standard Javascript libraries. See [Software Requirements](requirements.html#software-requirements) for high level view and the `requirement*.txt` files for detailed view.

GovReady-Q's Python application code is found in the `*.py` files in the following directories and their subdirectories:
* discussion/
* guidedmodules/
* siteapp/

The small `manage.py` script in the root directory is part of the Django framework. We use bash utilities scripts (`*.sh`) to automate installation and maintenance tasks of the code base. Python scripts in `.circleci` directory are used within our Continuous Implementation pipeline.

### Simple Static Code Analysis

To run a static code analysis with our typical settings:

	bandit -s B101,B110,B603 -r discussion/ guidedmodules/ siteapp/

We use `-s` on the command-line and `nosec` in limited places in the source code to disable some checks that are determined after review to be false positives.

### Detailed Static and Dynamic Code Analysis

We periodically scan GovReady-Q's code base with more traditional/powerful tools and remediate critical and high vulnerabilities.

To scan GovReady-Q's codebase, you will need to configure your tools to scan Python code. You are looking for the `*.py` files across the code base.

To scan or do other penetration tests on the code base, we recommend [deploying GovReady-Q with Docker](deploy_docker.html).

## Dependency Management and Vulnerability Testing

Our `requirements.txt` file is designed to work with `pip install --require-hashes`, which ensures that every installed dependency matches a hash stored in this repository. The option requires that every dependency (including dependencies of dependencies) be listed, pinned to a version number, and paired with a hash. We therefore don't manually edit `requirements.txt`. Instead, we place our immediate dependencies in `requirements.in` and run `requirements_txt_updater.sh` (which calls pip-tools's pip-compile command) to update the `requirements.txt` file for production.

Continuous integration is set up with CircleCI at https://circleci.com/gh/GovReady/govready-q and performs unit tests, integration tests, and security checks on our dependencies. 

1. CI runs `requirements_txt_checker.sh` which ensures `requirements.txt` is in sync with `requirements.in`. This script is set up to run against any similar files as well, such as MySQL-specific `requirements_mysql.*` files.
1. CI checks that there are no known vulnerabilities in the dependencies using [pyup.io](https://pyup.io/).
1. CI checks that all packages are up to date with upstream sources (unless the package and its latest upstream version are listed in `requirements_txt_checker_ignoreupdates.txt`).

## Populating sample data for manual testing and verification

In some cases, you may wish to perform manual testing on an instance of GovReady-Q which has been populated with data. Several Django commands have been added to facilitate this, in the `testmocking` module. Generated data is intended to be structurally similar to what might be found in a real GovReady-Q instance, but the actual content of the data will often appear machine-generated.

If you wish to get up and running quickly, the following command is recommended:

```
python3 manage.py populate --full --password TEST_PASSWORD_HERE
```

The `populate --full` command will generate a set of users and organizations inside of GovReady-Q, and then add assessments to those organizations. User count and organization count can be controlled using the `--user-count` and `--org-count` arguments. `--password` can take any value, and is a recommended (but not required) argument, for easier login to the test accounts.

Note that `populate` will use the same password for all created users, as generating unique credentials for each user would be slow (due to best practice security measures used by GovReady-Q's authentication process).
