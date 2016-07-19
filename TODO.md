### Cloud Foundry to do/problems

**Fix migration/launch**
The logic around migrations is wrong. The current approach is to use the `2: migrate occasionally` strategy from https://docs.cloudfoundry.org/devguide/services/migrate-db.html by
running, from the remote client, `make migrate` (which touches the `.migration_done` file), then `make run`

The `make migrate` task uses the `init_db.py` script to migrate and load_modules, but not to start the app. Since the script does not leave behind a long-running app, CF sees that as a failure, `cf push` exits with status 2, and `make` doesn't touch the _canary_ file `.migration_done`

For the long run we should use strategy 3 to continually migrate in an idempotent fashion. The example given at CFs webpage probably won't work because the command chain is, essentially:

1. If (Instance_ID=0) {run migrations}; exit 0
2. run application

which means instance 0 will be fine, but instances 1..N will immediately start the app, probably before the migrations are complete.

It may be necessary to change steps to:

1. If (Instance_ID=0) {run migrations} else {poll until migrations complete}; exit 0
2. run application

A few other potential fixes:
1. Don't worry about multi-instance; only ever run with a single instance (with autoscaling to reduce downtime when the main instance dies)
2. If multi-instance, use someother lock to prevent the app from running
3. If multi-instance, allow the app to start prior to migrations being complete and behaving in a sane fashion.

From the adage, "You don't have scale problem until you have a scale problem" we should go with 1, and just run one instance.  **Caveat**: We should be sure the code _can_ run across multiple instances (is stateless) so scaling is easier down the road.


[ ] memcached?
[ ]
``
