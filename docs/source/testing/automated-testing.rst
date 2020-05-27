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

_NOTE: Depending on your Python3 configuration, you may need to run:_

.. code-block:: bash
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
