# Build on Docker's official Python 3(.6) image.
FROM python:3

# Expose the port that `manage.py runserver` uses by default.
EXPOSE 8000

# Put the Python source code here.
WORKDIR /usr/src/app

# Install the U.S. locale, which we reference explicitly in Q for
# formatting and parsing numbers.
RUN apt-get update && apt-get install locales && apt-get clean && sed -i "s/^[# ]*en_US.UTF-8/en_US.UTF-8/" /etc/locale.gen && /usr/sbin/locale-gen

# Install required system packages.
# jq: we use it to assemble the local/environment.json file
RUN apt-get update && apt-get install -y graphviz unzip pandoc xvfb wkhtmltopdf jq && apt-get clean

# Copy in the Python module requirements and install them.
# Manually install database drivers which aren't in our requirements
# file because they're not commonly used in development.
# Run pyup.io's python package vulnerability check.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir psycopg2
RUN safety check

# Copy in the vendor resources and fetch them.
COPY fetch-vendor-resources.sh ./
RUN ./fetch-vendor-resources.sh

# Copy in remaining source code. (We put this last because these
# change most frequently, so there is less to rebuild if we put
# infrequently changed steps above.)
#
# NOTE: Do *not* include the "local" directory in this step, since
# that often has local development files.
COPY discussion ./discussion
COPY guidedmodules ./guidedmodules
COPY modules ./modules
COPY siteapp ./siteapp
COPY templates ./templates
COPY manage.py .
COPY deployment/docker/first_run.sh .
COPY deployment/docker/dockerfile_exec.sh .

# Set the startup script.
CMD [ "bash", "dockerfile_exec.sh" ]
