#!/bin/bash

# A wrapper script for running Compliance
# from a circleci node against a deployed app container

set -euf -o pipefail -x

ssh_hostport=$(cf curl /v2/info | jq '.app_ssh_endpoint' -r )
ssh_host=$(echo $ssh_hostport| awk -F: '{print $1}')
ssh_port=$(echo $ssh_hostport| awk -F: '{print $2}')
ssh_guid=$(cf app govready-q --guid)
ssh_pass=$(cf ssh-code)
ssh_user="cf:$ssh_guid/0"

control=staging-info
#ssh -p $ssh_port cf:$ssh_guid/0@$ssh_host
bundle exec inspec exec ./app \
  -b ssh \
  --host=$ssh_host \
  --user=$ssh_user \
  --password $ssh_pass \
  --port=$ssh_port
#  -t ssh://cf:$ssh_guid/0@$ssh_host --password $ssh_pass
