Deveoper Guide
================================

Documentation for developers of GovReady-Q Compliance Server.

# Overview

GovReady-Q Compliance Server is a GRC platform for creating automated compliance processes ranging from gathering information from persons and computers to generating compliance artifacts.

Unlike other GRC software, GovReady-Q was designed for modern software practices such as Agile, DevOps, and Infrastructure-as-Code.

The GovReady Compliance ecosystem consists of the following:

1. GovReady-Q Compliance Server - an open source server and collaboration platform gathering information and generating artifacts
1. GovReady Compliance Apps - customizable "images" of modules, questions, tasks, and artifact templates
1. GovReady Automation API - GovReady-Q Server's RESTful API for adding evidence and results
1. OpenControl - an emerging standard for expressing control implementation information in machine readable format
1. ComplianceLib - a Python library for modeling controls and control catalogs

# GovReady-Q Django Apps

The GovReady-Q Compliance Server is a Django Project consisting of three interacting Django Apps:

1. `siteapp` - handles Users, Organizations, Projects and Folders, Invitations
1. `guidedmodules` - handles Compliance Apps, Modules and Questions, (Tasks,) Answers, Instrumentation
1. `discussion` - handles Discussions, Comments, Invitations

Both `siteapp` and `discussion` are fairly intuitive in what they do and how they work. The `guidedmodules` app is the most sophisticated and least intuitive of the three and provides the core functionality the GovReady Compliance Server.

## Siteapp

The diagram below provides summary representation of GovReady-Q's Django siteapp data model that handles users, organizations, project and folders and invitations.

![Siteapp data model (not all tables represented)](assets/govready-q-siteapp-erd.png)

## Guidedmodules

The diagram below provides summary representation of GovReady-Q's Django guidedmodules data model that handles Compliance Apps, modules and 1uestions, (tasks,) answers, and instrumentation. 

![Guildedmodules data model (not all tables represented)](assets/govready-q-guidedmodules-erd.png)

## Discussion

The diagram below provides summary representation of GovReady-Q's Django discussion data model that handles discussions, comments, and invitations.

![Discussion data model (not all tables represented)](assets/govready-q-discussion-erd.png)

## Generate Detailed Data Models

Below are instructions to use `django-extensions` to generate detailed data models.

```
# Install django-extensions
# http://django-extensions.readthedocs.io/en/latest/installation_instructions.html
pip3 install django-extensions

# Add django-extensions INSTALLED_APPS in siteapp > settings.py
# INSTALLED_APPS = (
#    ...
#    'django_extensions',
# )

# You may need to install pyparsing
pip3 install pyparsing

# examples:
python3 manage.py graph_models -a -g -o my_project_visualized.png
python3 manage.py graph_models -a -o my_project.png
python3 manage.py graph_models -a > my_project.dot
# for a single django app:
python3 manage.py graph_models app1 -o my_project_app1.png
```

