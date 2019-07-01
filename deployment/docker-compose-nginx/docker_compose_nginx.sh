#!/bin/bash

# This script simplifies what users need to know in
# order to launch GovReady-Q docker container plus
# NGINX reverse proxy to support HTTPS

# Usage
#    ./docker_compose_nginx.sh --dm-name <host name> --aws-region <aws region>
#
# Example:
#   ./docker_compose_nginx.sh --dm-name grq-https-01
#   ./docker_compose_nginx.sh --dm-name grq-https-01 --aws-region us-east-1
#

set -euf -o pipefail # abort script on error

# Defaults
##########

# Docker machine name
# The name for the ec2 instance hosting Docker.
# Set with `--dm-name NAME`. If set to the empty
# string, no name is used. The default is:
DM_NAME="grq-nginx-sandbox"

# AWS Region to launch ec2 instance.
# The default is:
AWS_REGION="us-east-1"

# Parse command-line arguments
##############################

while [ $# -gt 0 ]; do
  case "$1" in
    --dm-name)
      DM_NAME="$2"
      shift 2 ;;
    --aws-region)
      AWS_REGION="$2"
      shift 2 ;;
    --)
        shift
        break
        ;;
    *)
      echo "Unrecognized command line option: $1";
      exit 1;
    esac
done

WARNINGS=0

# Adjust AWS public domain string appropriately for different regions
# us-east-1 (compute-1.amazonaws.com), us-east-2 (us-east-2.compute.amazonaws.com),
# us-west-1 (us-west-1.compute.amazonaws.com), etc...
if [ $AWS_REGION = "us-east-1" ]
then
  AWS_REGION_STR="compute-1"
else
  AWS_REGION_STR="$AWS_REGION.compute"
fi

# Have docker-machine create the ec2 instance to host docker
echo "Running: docker-machine create --driver amazonec2 --amazonec2-open-port 80 --amazonec2-region $AWS_REGION $DM_NAME"
docker-machine create --driver amazonec2 --amazonec2-open-port 80 --amazonec2-open-port 443 --amazonec2-region $AWS_REGION $DM_NAME

# Let's grab the Host machine's Public and Private IP addresses
export PRIVATE_IP=$(docker-machine inspect -f '{{ .Driver.PrivateIPAddress }}' $DM_NAME)
echo "Private IP: $PRIVATE_IP"
export PUBLIC_IP=$(docker-machine ip $DM_NAME)
echo "Public IP: $PUBLIC_IP"
# Transpose '.' in IP address to '-' required in AWS Domain name
echo "AWS address is: ec2-$(echo $PUBLIC_IP | tr . "-").$AWS_REGION_STR.amazonaws.com"

# Make the created docker-machine the active docker-machine for docker commands
# docker-machine env $DM_NAME
eval $(docker-machine env $DM_NAME)

# Show current docker machine configuration
docker-machine ls

echo "EC2 instance running and active. Proceed with docker-compose commands..."

echo "Setting GOVREADY_Q_HOST=ec2-$(echo $PUBLIC_IP | tr . "-").$(echo $AWS_REGION_STR).amazonaws.com"
export GOVREADY_Q_HOST=ec2-$(echo $PUBLIC_IP | tr . "-").$(echo $AWS_REGION_STR).amazonaws.com
echo "Setting GOVREADY_Q_IMAGENAME=govready/govready-q-0.9.0"
export GOVREADY_Q_IMAGENAME=govready/govready-q-0.9.0
# export GOVREADY_Q_DBURL=postgres://govready_q:my_private_password@grq-002.cog63arfw9bib.us-east-1.rds.amazonaws.com/govready_q
echo "Set GOVREADY_Q_DBURL to default (blank for SQLITE)"

echo "Build images (on active docker machine)"
docker-compose build

echo "Bring containers up using: docker-compose up -d"
echo "GOVREADY_Q_HOST=ec2-$(echo $PUBLIC_IP | tr . "-").$(echo $AWS_REGION_STR).amazonaws.com GOVREADY_Q_IMAGENAME=govready/govready-q-0.9.0 docker-compose up -d"
# Environmental variables must be pre-pended to docker-compose commands
# as per https://stackoverflow.com/questions/49293967/how-to-pass-environment-variable-to-docker-compose-up
GOVREADY_Q_HOST=ec2-$(echo $PUBLIC_IP | tr . "-").$(echo $AWS_REGION_STR).amazonaws.com GOVREADY_Q_IMAGENAME=govready/govready-q-0.9.0 docker-compose up -d

# Configure Superuser account for GovReady-Q
echo " "
echo "Load demo assessments and create superuser"
docker exec -it docker-compose-nginx_govready-q_1 first_run

# Provide some frienly feedback
echo "Point your browser to https://$GOVREADY_Q_HOST"

echo " "
echo "To stop container run: docker-machine stop $DM_NAME"
echo "To remove container and hosting ec2 instance run: docker-machine rm $DM_NAME"

# Getting information about ec2 instance from within
# curl http://169.254.169.254/latest/meta-data/public-ipv4
# curl http://169.254.169.254/latest/meta-data/public-hostname 2>/dev/null
