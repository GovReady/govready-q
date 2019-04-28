# Deploying to a generic Unix-based OS

If you are using a Unix-based OS (or POSIX-compliant OS) which is not specifically listed, here are the generic steps to take when installing GovReady-Q.

## System Requirements

First, install sufficient [system requirements](requirements.html#software-requirements).

Typically, this will include:

- python3
- pip3
- unzip
- pandoc
- wkhtmltopdf and xvfb
- gcc
- git
- bash 4.0+ (note: macOS may have an older version)

## Download and Install GovReady-Q

Run the following commands to download the GovReady-Q source code, install necessary Python modules, and perform app-specific installation steps.

	# Clone this repository.
	git clone https://github.com/GovReady/govready-q
	cd govready-q

	# Install dependencies.
	pip3 install --user -r requirements.txt
	./fetch-vendor-resources.sh

	# if you intend to use optional configurations, such as the MySQL adapter, you
	# may need to run additional `pip3 install` commands, such as:
	# pip3 install --user -r requirements_mysql.txt

	# Set up the database (sqlite3 will be used until you configure another database).
	python3 manage.py migrate
	python3 manage.py load_modules


## Next steps (Production or Development configuration)

If you're deploying GovReady-Q to a production environment, see the [Production deployment steps](deploy_prod.html).

If you're deploying GovReady-Q for development or evaluation purposes, [Development deployment steps](deploy_local_dev.html) may be useful for you.
