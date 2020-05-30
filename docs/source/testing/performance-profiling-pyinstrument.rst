.. Copyright (C) 2020 GovReady PBC

.. _performance_profiling_pyinstrument:

Performance Profiling with Pyinstrument
=======================================

The Python package `Pyinstrument <https://github.com/joerick/pyinstrument#profile-a-web-request-in-django>`_ can be added to GovReady-Q to profile performance issues within the code.

Pyinstrument includes a Django middleware that when added to GovReady-Q's ``siteapp/settings_application.py`` file enables displaying of profile results directly in the browser.

Use Pip to install Pyinstrument Python package.

.. code:: bash

    pip install pyinstrument

Add ``pyinstrument.middleware.ProfilerMiddleware`` to ``siteapp/settings_application.py``.

.. code:: python

    MIDDLEWARE += [
        #'debug_toolbar.middleware.DebugToolbarMiddleware',
        'siteapp.middleware.ContentSecurityPolicyMiddleware',
        'guidedmodules.middleware.InstrumentQuestionPageLoadTimes',
        'pyinstrument.middleware.ProfilerMiddleware'
    ]

Restart GovReady-Q server.

Once installed, add ``?profile`` to the end of a request URL to activate the profiler (or ``&profile`` if URL already includes GET params).

See `Pyinstrument Profile a web request in Django <https://github.com/joerick/pyinstrument#profile-a-web-request-in-django>`_ for more details.
