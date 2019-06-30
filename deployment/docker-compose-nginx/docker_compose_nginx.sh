#!/bin/bash

set -euf -o pipefail # abort script on error

# Defaults
##########
# Defaults
##########

# Docker machine name
# The name for the ec2 instance hosting Docker.
# Set with `--dm-name NAME`. If set to the empty
# string, no name is used. The default is:
DM_NAME="grq-ngninx-sandbox"

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

# Have docker-machine create the ec2 instance to host docker
docker-machine create --driver amazonec2 --amazonec2-open-port 80 --amazonec2-region $AWS_REGION $DM_NAME

# Let's grab the Host machine's Public and Private IP addresses
PRIVATE_IP=$(docker-machine inspect -f '{{ .Driver.PrivateIPAddress }}' $DM_NAME)
echo $PRIVATE_IP
PUBLIC_IP=$(docker-machine ip $DM_NAME)
echo $PUBLIC_IP
echo "ec-$PUBLIC_IP.compute-1.amazonaws.com"

# Make the created docker-machine the active docker-machine for docker commands
# docker-machine env $DM_NAME
eval $(docker-machine env $DM_NAME)

# Show current docker machine configuration
docker-machine ls

echo "EC2 instance running and active. Proceed with docker-compose commands..."

echo "Setting GOVREADY_Q_HOST=ec-$PUBLIC_IP.compute-1.amazonaws.com"
export GOVREADY_Q_HOST=ec-$PUBLIC_IP.compute-1.amazonaws.com
echo "Setting GOVREADY_Q_IMAGENAME=govready/govready-q-0.9.0"
export GOVREADY_Q_IMAGENAME=govready/govready-q-0.9.0
# export GOVREADY_Q_DBURL=postgres://govready_q:my_private_password@grq-002.cog63arfw9bib.us-east-1.rds.amazonaws.com/govready_q
echo "Set GOVREADY_Q_DBURL to default (blank for SQLITE)"

# echo "export GOVREADY_Q_HOST=ec2-nnn-nnn-nnn-nnn.us-east-1.compute.amazonaws.com"
# echo "export GOVREADY_Q_HOST=$PUBLIC_IP"
# # export GOVREADY_Q_HOST=ec2-18-233-158-98.compute-1.amazonaws.com
# echo "export GOVREADY_Q_IMAGENAME=govready/govready-q-0.9.0"
# echo "docker-compose build"
# echo "docker-compose up -d"

echo "Build images (on active docker machine)"
#docker-compose build

echo "Following is run: docker-compose up -d"
#docker-compose up -d


# Pull and run GovReady-Q 0.9.0 container making site available on port 80 with no https
# docker run --detach --name govready-q-0.9.0 -p $PRIVATE_IP:80:8000 \
# -e HTTPS=false -e DBURL= -e DEBUG=true \
# -e HOST=$PUBLIC_IP \
# govready/govready-q-0.9.0

# # Configure Superuser account for GovReady-Q
# docker exec -it govready-q-0.9.0 first_run

# Provide some frienly feedback
echo "Point your browser to https://$GOVREADY_Q_HOST"

echo " "
echo "To stop container run: docker-machine stop $DM_NAME"
echo "To remove container and hosting ec2 instance run: docker-machine rm $DM_NAME"

# Getting information about ec2 instance from within
# curl http://169.254.169.254/latest/meta-data/public-ipv4
# curl http://169.254.169.254/latest/meta-data/public-hostname 2>/dev/null

