.. Copyright (C) 2020 GovReady PBC

.. _govready-q_server_docker_cloud:

Docker Cloud
=============

These instruction are for running a GovReady-Q on a remote host in the cloud.

This configuration assumes a complex network configuration where you will be
viewing GovReady-Q from a different machine from the host that is hosting the docker instance.

In this scenario it is necessary to correctly set a variety of networking-related parameters.


1. Installing Docker
--------------------

Make sure you first install Docker.

* https://docs.docker.com/engine/installation/
* https://docs.docker.com/engine/install/centos/
* https://docs.docker.com/engine/install/ubuntu/

If appropriate, grant non-root users access to run Docker containers

* https://docs.docker.com/engine/installation/linux/linux-postinstall/#manage-docker-as-a-non-root-user


2. Running GovReady-Q server container
--------------------------------------

We recommend you launch GovReady-Q container in the detached mode.

The following commands will launch GovReady-Q using the default SQLITE database.

.. code-block:: bash

    # Set relevant network Host Name / Domain / IP Address of server hosting GovReady-Q Docker container
    HOSTNAME=<HOSTNAME_OR_IP_ADDRESS>
    export HOSTNAME

    # Run the docker command to launch GovReady-Q's container
    sudo docker container run --detach --name govready-q  -p 80:8000 -e HOST="$HOSTNAME" -e PORT=80 \
    -e HTTPS=false -e DBURL= -e DEBUG=false  -e FIRST_RUN=1 -e DEBUG=true govready/govready-q

    # View the Docker log to get the automatically generated Superuser account information if you are initializing the database
    sudo docker container logs govready-q

Visit your GovReady-Q site in your web browser at:

    http://HOSTNAME

Your GovReady-Q site will not load immediately, as GovReady-Q
initializes your database for the first time. Wait for the site to
become available.

Alternatively, you can use GovReady-Q's ``docker_container_run.sh`` script.

.. code-block:: bash
    wget https://raw.githubusercontent.com/GovReady/govready-q/master/deployment/docker/docker_container_run.sh
    chmod +x docker_container_run.sh

.. code-block:: bash

    # Set relevant network Host Name / Domain / IP Address of server hosting GovReady-Q Docker container
    HOSTNAME=<HOSTNAME_OR_IP_ADDRESS>
    export HOSTNAME

    # Run the docker container using the docker_container-run.sh script in non-interactive mode
    sudo ./docker_container_run.sh --address $HOSTNAME:80 --bind $HOSTNAME:80 -- -e FIRST_RUN=1 \
    -e HOST=$HOSTNAME -e PORT=80 -e DEBUG=true

    # View the Docker log to get the automatically generated Superuser account information if you are initializing the database
    sudo docker container logs govready-q


The default Govready-Q instance is configured to non-debug mode (Django
``DEBUG=false``), which is the recommended setting for a public website.
The instance can be set to debug mode at runtime.

.. note::
    Example log output

    .. code:: bash

        root@ubuntu-s-2vcpu-4gb-nyc1-01:~# ./docker_container_run.sh --address 174.138.37.213:80 --bind 174.138.37.213:80 -- -e FIRST_RUN=1 -e HOST=174.138.37.213 -e PORT=80 -e DEBUG=true
        Using default tag: latest
        latest: Pulling from govready/govready-q
        Digest: sha256:de7f9752f95e885afa8966197dd59dbdb037b31630fbb5c0e0764531f1ef3ac0
        Status: Image is up to date for govready/govready-q:latest
        docker.io/govready/govready-q:latest
        GovReady-Q is starting...
        Container Name: govready-q
        Container ID: 6448d84ce6c7270e4f25cc830ddaf7839b5839e813a3632143a5362651cf193e
        Version: v0.9.1.12 
        Waiting for GovReady-Q to come online...
        Waiting for GovReady-Q to come online...
        
        ...

        GovReady-Q has been started!
        Listening on: 174.138.37.213:80
        URL: http://174.138.37.213
        For additional information run: docker container logs govready-q
        root@ubuntu-s-2vcpu-4gb-nyc1-01:~# docker container logs govready-q 
        This is GovReady-Q.
        v0.9.1.12

        Filesystem information:
        overlay / overlay rw,relatime,lowerdir=/var/lib/docker/overlay2/l/N3AVVYQ5DSUEE2OM3BS5LDPJ2R:/var/lib/docker/overlay2/l/XC2GAGKXOHT5AXBS63S3ILRNPK:/var/lib/docker/overlay2/l/5RW2V34N7DVPSXROQZM5IRQFDL:/var/lib/docker/overlay2/l/KFM5X32GDYXNZQJI64VKVUQ22N:/var/lib/docker/overlay2/l/YJJU2VGWOTBAF6WJW6GQA36J4G:/var/lib/docker/overlay2/l/L6FDR5GPPKMFIKKJZGSIQ6C7LV:/var/lib/docker/overlay2/l/GQUETMFMWPDZUKIQEGEEU4SFMV:/var/lib/docker/overlay2/l/7TLM7LC4VF2RYKPF4EBUW4UZBD:/var/lib/docker/overlay2/l/7SVNYISM5PYCUPIWU5FMUDL6BS:/var/lib/docker/overlay2/l/VBJDT6HYRDN4QLAWKMTZHASYYC:/var/lib/docker/overlay2/l/YRFVSGB4L7G5NS3UHKB2CQOK6Y:/var/lib/docker/overlay2/l/OTTSHASF6NO6R3DRNZD5YQXRXZ:/var/lib/docker/overlay2/l/PVUCE5DWRHDLRSUQVNZOVEZECC:/var/lib/docker/overlay2/l/ZX42GWAQU6UAEH656AH5UX5S3D:/var/lib/docker/overlay2/l/EA6MQBCVQMTCJG6M2ADW7F7TYI:/var/lib/docker/overlay2/l/ONDI3JJS7FGJD5FYG47JMCUPNU:/var/lib/docker/overlay2/l/MBDLEHR6CLDKBYI4UHBDJP2CXY:/var/lib/docker/overlay2/l/4JJ4B7CSKLHIOKCRKDPE5IFTXD:/var/lib/docker/overlay2/l/3WGMUK5JMSHRMZTNFBR6XZFNQC:/var/lib/docker/overlay2/l/FJNWSAZ6BZNWEGTW6QNUO4ONWR:/var/lib/docker/overlay2/l/TEVY5K4QZM67JCZGEDNM6W2E6E:/var/lib/docker/overlay2/l/RB6MOAUY5ARXKNZB4X2WY33MPF:/var/lib/docker/overlay2/l/2W6CXPXCS5OVAA6QGUB72SKIMA:/var/lib/docker/overlay2/l/Y3K3HW2S5MRGR5LJSLBXQCE4QA:/var/lib/docker/overlay2/l/AFLMN7W3XXR753PWGAYX7T2LP4:/var/lib/docker/overlay2/l/VULWA46JEROWKKQ3JJZUY4JCJJ:/var/lib/docker/overlay2/l/RHXI25QU7QBHZ4ML6QI6Y4Z2A4:/var/lib/docker/overlay2/l/5GEEYLAHQZQW3KM4RF5UPLXMW7:/var/lib/docker/overlay2/l/2WBKETVVEL3IJXHFEJVUBCW73A:/var/lib/docker/overlay2/l/AFC2ATE4JPYOXWWJRDIC5ZHMAX:/var/lib/docker/overlay2/l/EZTNQYVVYILNKHROAEJZWRSYL5:/var/lib/docker/overlay2/l/6UOID7MMZZEIC2GA7S6EZIQKS3:/var/lib/docker/overlay2/l/DSV35YXZXRB4ASPPNC3PSMJFSK:/var/lib/docker/overlay2/l/ARRDNFKBNXHFPSA3EQD533VPFY:/var/lib/docker/overlay2/l/3A3DOPZTJF6IYPVZZ5X7ZDXA56:/var/lib/docker/overlay2/l/RC5PUXCSJQ5TWKQT7ZTJJSJUJB:/var/lib/docker/overlay2/l/NG27PZR7QND6WTMVJ5HEITLHRJ:/var/lib/docker/overlay2/l/SKQ7VADV4CE5OQEUOCOUJOUWF3:/var/lib/docker/overlay2/l/RW2QA4G2LNI67BUOR355Q7MPLR:/var/lib/docker/overlay2/l/GTDTKJ7CIXGFM76OWVOYVJ74RV:/var/lib/docker/overlay2/l/7KI5FV5W267ZE3BFVE5QPTHXK4:/var/lib/docker/overlay2/l/NKK3XZKKJHAHLYRANW2YN2ZM7Y:/var/lib/docker/overlay2/l/WDA7UC26LZEVUSP7GK2CBMIKSI:/var/lib/docker/overlay2/l/ZXSHMF67XBVQ53UWLQQRAGMNDG,upperdir=/var/lib/docker/overlay2/acae340ecfa3950b57a8b3c433f781625934fa65953fed447730cf638822f7eb/diff,workdir=/var/lib/docker/overlay2/acae340ecfa3950b57a8b3c433f781625934fa65953fed447730cf638822f7eb/work 0 0
        /dev/vda1 /etc/resolv.conf ext4 rw,relatime,data=ordered 0 0
        ...

        Starting at 174.138.37.213 with HTTPS false.
        WARNING: Specified PDF generator is not supported. Setting generator to 'off'.
        WARNING: Specified IMG generator is not supported. Setting generator to 'off'.
        System check identified some issues:

        WARNINGS:
        ?: (security.W018) You should not have DEBUG set to True in deployment.

        System check identified 1 issue (4 silenced).
        dockerfile_exec.sh: line 104: [: too many arguments
        Confirmed that database is not initialized or has been migrated, and OK for version 0.9.0 migrations.
        WARNING: Specified PDF generator is not supported. Setting generator to 'off'.
        WARNING: Specified IMG generator is not supported. Setting generator to 'off'.
        Operations to perform:
        Apply all migrations: account, admin, auth, contenttypes, controls, dbstorage, discussion, guardian, guidedmodules, notifications, sessions, siteapp, sites, socialaccount, system_settings
        Running migrations:
        Applying contenttypes.0001_initial... OK
        Applying contenttypes.0002_remove_content_type_name... OK
        Applying auth.0001_initial... OK
        Applying auth.0002_alter_permission_name_max_length... OK
        Applying auth.0003_alter_user_email_max_length... OK
        ...
        Applying socialaccount.0003_extra_data_default_dict... OK
        Applying system_settings.0001_initial... OK
        Applying system_settings.0002_auto_20190808_1947... OK
        WARNING: Specified PDF generator is not supported. Setting generator to 'off'.
        WARNING: Specified IMG generator is not supported. Setting generator to 'off'.
        Running FIRST_RUN actions...
        WARNING: Specified PDF generator is not supported. Setting generator to 'off'.
        WARNING: Specified IMG generator is not supported. Setting generator to 'off'.
        Adding appname 'System-Description-Demo' from AppSource 'govready-q-files-startpack' to catalog.
        Adding appname 'PTA-Demo' from AppSource 'govready-q-files-startpack' to catalog.
        Adding appname 'rules-of-behavior' from AppSource 'govready-q-files-startpack' to catalog.
        Adding AppSource for authoring.
        Created administrator account (username: admin) with password: Y985S7NubSd5gyV2Rp5TfPk2
        Created administrator portfolio admin
        You can now login into GovReady-Q...
        GovReady-Q is starting.

.. warning::
    The GovReady-Q default SQLite database created within a Docker container
    exists only for the duration of the container’s lifetime. The database
    will persist between
    ``docker container stop``/``docker container start`` commands, but when
    the container is removed from Docker (i.e. using
    ``docker container rm``) the database will be destroyed.


3. Stopping, starting GovReady-Q server container
-------------------------------------------------

.. code-block:: bash

    # Stop, start container (when needed)
    docker container stop govready-q
    docker container start govready-q


4. Destroying the GovReady-Q server container
---------------------------------------------

.. code-block:: bash

    # Destroy the container and all user data entered into local database
    docker container rm -f govready-q

5. Viewing the GovReady-Q server logs in the container
--------------------------------------------------------

.. code-block:: bash

    # View logs - useful if site does not appear
    docker container logs govready-q


Advanced configuration options
------------------------------

The GovReady-Q server container supports many advanced configuration options
for production deployments.

See the next section `Advanced container configuration <advanced-container-config.html>`__  for further details.

.. topic:: Next

    .. toctree::
        :maxdepth: 1

        advanced-container-config-example
        advanced-container-config