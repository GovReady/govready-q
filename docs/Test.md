Testing
=======

1. [Running tests](#testing)
1. [Dependency management](#dependencies)

## <a name="testing"></a> Running tests

To run the integration tests, you'll also need to install chromedriver:

	sudo apt-get install chromium-chromedriver   (on Ubuntu)
	brew install chromedriver                    (on Mac)

Then run the test suite with:

	./manage.py test

## <a name="dependencies"></a> Dependency Management

Our `requirements.txt` file is designed to work with `pip install --require-hashes`, which ensures that every installed dependency matches a hash stored in this repository. The option requires that every dependency (including dependencies of dependencies) be listed, pinned to a version number, and paired with a hash. We therefore don't manually edit `requirements.txt`. Instead, we place our immediate dependencies in `requirements.in` and run `requirements_txt_updater.sh` (which calls pip-tools's pip-compile command) to update the `requirements.txt` file for production.

Continuous integration is set up with CircleCI at https://circleci.com/gh/GovReady/govready-q and performs unit tests, integration tests, and security checks on our dependencies. 

1. CI runs `requirements_txt_checker.sh` which ensures `requirements.txt` is in sync with `requirements.in`.
1. CI checks that there are no known vulnerabilities in the dependencies using [pyup.io](https://pyup.io/).
1. CI checks that all packages are up to date with upstream sources (unless the package and its latest upstream version are listed in `requirements_txt_checker_ignoreupdates.txt`).