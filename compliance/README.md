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

Profile: Cloud Foundry Compliance Profile (cloudfoundry)
Version: 1.0.0
Target:  local://

  ✔  cf-1.0: tbd

Summary: 3 successful, 0 failures, 0 skipped
```
