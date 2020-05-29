Generating Detailed Data Models
===============================

Below are instructions to use ``django-extensions`` to generate detailed
data models.

::

   # Install django-extensions
   # http://django-extensions.readthedocs.io/en/latest/installation_instructions.html
   apt install graphviz-dev
   pip3 install django-extensions pygraphviz

   # Add django-extensions INSTALLED_APPS in siteapp > settings.py
   # INSTALLED_APPS = (
   #    ...
   #    'django_extensions',
   # )

   # examples:
   python3 manage.py graph_models -a -g -o my_project_visualized.png
   python3 manage.py graph_models -a -o my_project.png
   python3 manage.py graph_models -a > my_project.dot
   # for a single django app:
   python3 manage.py graph_models app1 -o my_project_app1.png
