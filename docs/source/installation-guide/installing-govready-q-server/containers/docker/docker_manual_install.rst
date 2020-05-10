Manual installation on a Docker container
==========================================

If you have experience with Docker and want to try this manual
installation without affecting your own computer, you can run a CentOS 7
container with these commands.

.. code:: bash

   # start a container, forward port 8000 for GovReady
   docker run -it --name govready-q -p8000:8000 centos:7.8.2003 bash

You will start in a root shell. Create a non-root user:

.. code:: bash

   # create user and set password
   adduser testuser
   passwd testuser

   # give test user sudo privileges
   usermod -aG wheel testuser

   # add 'sudo' command
   yum install sudo

   # switch to the testuser account
   su - testuser

Then you can proceed with the installation of GovReady-Q as the non-root user ``testuser``.
