Automated testing
=================

GovReady-Q's unit tests and integration tests are currently combined. Our integration tests uses Selenium to simulate user interactions with the interface.

To run the integration tests, you'll also need to install chromedriver:

.. code-block:: bash

   sudo apt-get install chromium-chromedriver   (on Ubuntu)
   brew cask install chromedriver               (on Mac)

Navigate within your terminal to GovReady-Q top level directory.

Then run the test suite with:

.. code-block:: bash

    python manage.py test

.. note::
   Depending on your Python3 configuration, you may need to run

   .. code:: bash

      python3 manage.py test

To selectively run tests from individual modules:

.. code-block:: bash

    # test rendering of guided modules
    python manage.py test guidedmodules
    
    # test general siteapp logic
    python manage.py test siteapp
    
    # test discussion functionality
    python manage.py test discussion

Or to selectively run tests from individual classes or methods:

.. code-block:: bash

    # run tests from individual test class
    python manage.py test siteapp.tests.GeneralTests
    
    # run tests from individual test method
    python manage.py test siteapp.tests.GeneralTests.test_login

    # run tests from different apps in sequence
    python manage.py test siteapp.tests.GeneralTests.test_create_portfolios discussion.tests.DiscussionTests

To produce a code coverage report, run the tests with `coverage`:

.. code-block:: bash

    coverage run --source='.' --branch manage.py test
    coverage report

Selenium Troubleshooting
~~~~~~~~~~~~~~~~~~~~~~~~

**500 Internal Server Error**

Receiving an **500 Internal Server Error** in Selenium's Chromium web browser during
testing indicates an error serving the page.

If error is received only on some tests, the testing framework has located a legitimate problem
rendering that page that needs to be corrected.

If the error occurs rendering every page, the probable cause is missing static files. Correct this problem
by re-fetch vendor resources, check your ``static`` setting in the ``local/environment.json`` file
and re-run Django ``collectstatic`` admin command.

.. code-block:: bash

    ./fetch-vendor-resources.sh
    python manage.py collectstatic

To debug further, set the verbosity of the tests to level 3 for increased log output and
look for ``Missing staticfiles manifest entry for`` or other error messages detailing problems
with serving the page.

.. code-block:: bash

    python manage.py test -v 3
