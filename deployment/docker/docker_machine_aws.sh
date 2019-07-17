#!/bin/bash

set -euf -o pipefail # abort script on error

# Defaults
##########

# The site's public address as would be entered in a
# web browser. Set with --address HOST:PORT. The port
# is optional if 80. The default is:
HOST=localhost
PORT=80

# Docker machine name
# The name for the ec2 instance hosting Docker.
# Set with `--dm-name NAME`. If set to the empty
# string, no name is used. The default is:
DM_NAME="govready-q-sandbox"

# AWS Region to launch ec2 instance.
# The default is:
AWS_REGION="us-east-1"

# Turn on Django DEBUG mode?
DEBUG=false

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

    --address)
      # Split --address on a colon and store in HOST and PORT..
      IFS=':' read -r -a ADDRESS <<< "$2"
      HOST=${ADDRESS[0]-localhost}
      PORT=${ADDRESS[1]-80}
      shift 2 ;;

    --debug)
      DEBUG=true
      shift 1 ;;

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
echo "Running following docker-machine command..."
echo "docker-machine create --driver amazonec2 --amazonec2-open-port 80 --amazonec2-region $AWS_REGION $DM_NAME"
docker-machine create --driver amazonec2 --amazonec2-open-port 80 --amazonec2-region $AWS_REGION $DM_NAME

# Let's grab the Host machine's Public and Private IP addresses
export PRIVATE_IP=$(docker-machine inspect -f '{{ .Driver.PrivateIPAddress }}' $DM_NAME)
echo "Private IP: $PRIVATE_IP"
export PUBLIC_IP=$(docker-machine ip $DM_NAME)
echo "Public IP: $PUBLIC_IP"
# Transpose '.' in IP address to '-' required in AWS Domain name
echo "AWS address is: ec2-$(echo $PUBLIC_IP | tr . "-").$AWS_REGION_STR.amazonaws.com"

# Set HOST
if [ -z ${ADDRESS+x} ]
then
  # ADDRESS is not set, use public IP
  export HOSTNAME=$PUBLIC_IP
else
  export HOSTNAME=$HOST
fi

echo "HOSTNAME is: $HOSTNAME"

# Make the created docker-machine the active docker-machine for docker commands
# docker-machine env $DM_NAME
eval $(docker-machine env $DM_NAME)

# Show current docker machine configuration
docker-machine ls

echo "EC2 instance running and active. Proceed with docker run commands..."

echo "Setting GOVREADY_Q_HOST=ec2-$(echo $PUBLIC_IP | tr . "-").$(echo $AWS_REGION_STR).amazonaws.com"
export GOVREADY_Q_HOST=ec2-$(echo $PUBLIC_IP | tr . "-").$(echo $AWS_REGION_STR).amazonaws.com
echo "Setting GOVREADY_Q_IMAGENAME=govready/govready-q-0.9.0"
export GOVREADY_Q_IMAGENAME=govready/govready-q-0.9.0
# export GOVREADY_Q_DBURL=postgres://govready_q:my_private_password@grq-002.cog63arfw9bib.us-east-1.rds.amazonaws.com/govready_q
echo "Set GOVREADY_Q_DBURL to default (blank for SQLITE)"

echo "Bring containers up using: docker run commands..."
# Pull and run GovReady-Q 0.9.0 container making site available on port 80 with no https
docker run --detach --name govready-q-0.9.0 -p $PRIVATE_IP:80:8000 \
-e HTTPS=false -e DBURL= -e DEBUG=$DEBUG \
-e HOST=$HOSTNAME \
govready/govready-q-0.9.0

# Configure Superuser account for GovReady-Q
echo " "
echo "Load demo assessments and create superuser"
docker exec -it govready-q-0.9.0 first_run

# Provide some friendly feedback
echo " "
echo "AWS address is: ec2-$(echo $PUBLIC_IP | tr . "-").$AWS_REGION_STR.amazonaws.com"
echo "Private IP: $PRIVATE_IP"
echo "Public IP: $PUBLIC_IP"
echo " "
echo "Point your browser to http://$HOSTNAME"
echo "Remember to update DNS server..."
echo "To stop container run: docker-machine stop $DM_NAME"
echo "To remove container and hosting ec2 instance run: docker-machine rm $DM_NAME"
echo "To make new ec2 instance the active docker-machine run: eval \$(docker-machine env $DM_NAME)"
