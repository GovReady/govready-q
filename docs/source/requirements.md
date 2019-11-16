## System Requirements

GovReady-Q is a Python 3.6 and higher, Django 2.x application with a relational database back-end. 

### Software Requirements

| Required Software Packages (partial list) |
| --- |
| (GovReady-Q application) |
| Python 3.6 |
| Django 2.2 |
| Jinja 2.x |
| uwsgi 2.x |
| unzip |
| graphviz |
| libmagic |
| pandoc |
| Wkhtmltopdf |
| Git 2.x |
| supervisor |

| Supported Databases |
| --- |
| Postgres 9.4 (psycopg2 2.7.5 adapter) |
| Mysql 7.6 and higher (mysqlclient 1.3.12 adapter) |
| SQLite 3.x |

| Recommended Database |
| --- |
| Postgres 9.4 (psycopg2 2.7.5 adapter) |

| SMTP Mail Server (for sending email notifications and receiving comments via email) |
| --- |
| Any SMTP mail server (MTA) supporting STARTTLS connections. |

For a more detailed list of software dependencies and requirements see:
* https://github.com/GovReady/govready-q/blob/master/requirements.in
* https://github.com/GovReady/govready-q/blob/master/requirements.txt
* https://github.com/GovReady/govready-q/blob/master/requirements_mysql.in
* https://github.com/GovReady/govready-q/blob/master/requirements_mysql.txt
* https://github.com/GovReady/govready-q/blob/master/Vagrantfile

### Hardware Requirements

| Minimum Hardware |
| --- |
| Single server to host both multi-tenant GovReady-Q application and Database |
| Linux-compatible hardware |
| 2GB RAM |
| 10 GB storage (for database) |

| Recommended Hardware |
| --- |
| 2 servers: 1 for multi-tenant GovReady-Q application; 1 for Database Server |
| Linux-compatible hardware (64 bit architecture; FIPS-140-2 validated cryptographic module) |
| 8GB RAM for each server |
| 100 GB storage (for database server) |
