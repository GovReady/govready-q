# CloudFoundry compliance proof-of-concept

This directory provides two Inspec profiles for testing compliance of a Q install on CloudFoundry.


## CloudFoundry user audit

This is run from the inaccurately named `cirle.sh`, which will make API calls against
your cloudfoundry install to audit the user roles. To use this you'd typically just need to run:

```
cd compliance     # this directory
bundle install    # install required Gems
./circle.sh       # do the teests
```

The audit controls are in the file `cf/controls/cf.rb`, if users change in your CloudFoundry
install then you'll need to change the audit controls.

## CloudFoundry application install audit

Since CloudFoundry provides SSH access to the application containers, we can run Inspec
locally to issue commands over SSH to test the remote install. There is **no need to install
anything on the remote system** (assuming basic Linux shell commands are in place like: `netstat`
  `env`, `echo`)

SSH to CloudFoundry is enabled via one-time passwords, fetched with `cf ssh-code`
so using the password in the command line is not a threat.

The audit controls are in the file `app/controls/app.rb`. Currently it tests for:
  * Is logging setup by checking the VCAP_SERVICES var json for `syslog_drain_url`
  * Are python and diego-sshd the only listening processes
  * Is nothing listening outside the expected port rante.

To run it, execute `./remote.sh`

## Development notes

Inspec is organized around `profiles`, and in this directory we have to profiles, `app` and `cf`
in their corresponding directories.

When changing the profiles you can syntax/sanity-check them with:

```bash
$ inspec check app
$ inspec check cf
```

The shell scripts here should show how to run the scans, note that adding the switch `--format=documentation`
will provide you the test by test insight you many need.

Potential gotcha: The CF API user you are authenticated as may only have some of the permissions
you need for everything to work (manager v. developer v. auditor). Note that `remote.sh`
needs a developer CF user to gain SSH access.

A sample run:

```
$ ./remote.sh
++ cf curl /v2/info
++ jq .app_ssh_endpoint -r
+ ssh_hostport=ssh.run.pivotal.io:2222
++ echo ssh.run.pivotal.io:2222
++ awk -F: '{print $1}'
+ ssh_host=ssh.run.pivotal.io
++ echo ssh.run.pivotal.io:2222
++ awk -F: '{print $2}'
+ ssh_port=2222
++ cf app govready-q --guid
+ ssh_guid=98fa8d65-c6f6-4244-8b80-61752d54679f
++ cf ssh-code
+ ssh_pass=HG3ggG
+ ssh_user=cf:98fa8d65-c6f6-4244-8b80-61752d54679f/0
++ basename /Users/pburkholder/Projects/GovReady/govready-q/compliance
+ '[' compliance = compliance ']'
+ bundle exec inspec exec ./app -b ssh --host=ssh.run.pivotal.io --user=cf:98fa8d65-c6f6-4244-8b80-61752d54679f/0 --password HG3ggG --port=2222

Profile: Cloud Foundry Application Compliance Profile (cloudfoundry)
Version: 1.0.0
Target:  ssh://cf:98fa8d65-c6f6-4244-8b80-61752d54679f/0@ssh.run.pivotal.io:2222

  ✔  papertrail-logging: Papertrail Log Drain
  ✔  listening-ports: Enumerate listening ports
  ✔  non-listening-ports: Ensure no other ports/processes

Summary: 8 successful, 0 failures, 0 skipped
```
