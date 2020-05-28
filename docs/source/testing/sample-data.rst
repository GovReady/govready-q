Populating sample data for testing and verification
===================================================

In some cases, you may wish to perform manual testing on an instance of GovReady-Q which has been populated with data. Several Django commands have been added to facilitate this, in the ``testmocking`` module. Generated data is intended to be structurally similar to what might be found in a real GovReady-Q instance, but the actual content of the data will often appear machine-generated.

If you wish to get up and running quickly, the following command is recommended:

.. code-block:: bash

    python3 manage.py add_data --non-interactive


The ``add_data`` command will fill in a recommended set of sample data.
