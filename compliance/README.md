# CloudFoundry compliance

This profile assumes you have already authenticated to an api endpoint, e.g.:

```bash
$ cf api https://api.run.pivotal.io
$ cf auth $PWS_USER $PWS_PASS
$ cf target -o GovReady -s prod
```
## Verify a profile

InSpec ships with built-in features to verify a profile structure.

```bash
$ inspec check compliance
```

## Execute a profile

To run all **supported** controls on a local machine use `inspec exec /path/to/profile`.

```bash

$ inspec exec compliance
..

Finished in 0.0025 seconds (files took 0.12449 seconds to load)
8 examples, 0 failures
```
