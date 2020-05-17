.. Copyright (C) 2020 GovReady PBC

.. _govready-q_server_installation:

Installing GovReady-Q server
============================

The GovReady-Q server can be installed on any Unix-like operating system. It is most commonly installed on Linux.

The primary differences between OS installations are package names and the OS's install package command.

Once the required OS packages have been installed, installing GovReady-Q server is identical.

Consult the table below and choose how to proceed:

+-------------------------------+-------------------------------------------------------------------------+
| Install                       | Guide                                                                   |
+===============================+=========================================================================+
| CentOS / RHEL                 | :ref:`CentOS/RHEL 7 or greater <govready-q_server_sources_centos_rhel>` |
+-------------------------------+-------------------------------------------------------------------------+
| Ubuntu                        | :ref:`Ubuntu 16.04 or greater <govready-q_server_sources_ubuntu>`       |
+-------------------------------+-------------------------------------------------------------------------+
| macOS                         | :ref:`macOS 10.10 or greater <govready-q_server_sources_macos>`         |
+-------------------------------+-------------------------------------------------------------------------+
| Docker (Unix)                 | :ref:`Docker 17 or greater <govready-q_server_docker>`                  |
+-------------------------------+-------------------------------------------------------------------------+
| Docker GovReady+Wazuh (Unix)  | :ref:`Docker GovReady+Wazuh <govready-q_server_wazuh_docker>`           |
+-------------------------------+-------------------------------------------------------------------------+


.. topic:: Contents

    .. toctree::
        :maxdepth: 1

        linux/centos/index
        linux/ubuntu/index
        unix/macos/index
        containers/docker/index
        containers/docker-govready-wazuh/index
