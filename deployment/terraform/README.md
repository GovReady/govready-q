# Terraform-driven deployment of GovReady-Q

## Overview

This is the beginning of a Terraform-driven deployment of GovReady-Q, starting with `govready-q.tf`.  The first version will be very simple, setting up one server running Q, using Terraform `remote-exec` commands to do the installation.  The initial cloud provider is AWS.

Later versions will evolve, to include database server, bastion server, possibly failover configurations, and either streamlined installation via an install script (reducing the number of `remote-exec` commands required) or application installation via a configuration management tool rather than Terraform.

As the Terraform file gets larger, other enhancements may include abstraction of hard-coded values to a `.tfvars` file, modularization of Terraform files, use of remote (shared) state storage, etc.

## Running Terraform

These instructions will briefly explain how to run Terraform via a Docker container, with an explicit image tag. (Note that Terraform versions appear to be [semver](https://semver.org/)-formatted, but do not have semver semantics.  See this [thread about HashiCorp app versioning](https://twitter.com/mitchellh/status/1012678790449786881).)

Running Terraform via Docker abstracts Terraform from the local dev machine; you don't have to install Terraform on your dev machine, and you get replicable results on different dev machines.  However, if you prefer, you can run Terraform directly on your local dev machine.

### Set Up Terraform Version and Command

Do something like this in an init script.  Update the Terraform tag and directory paths as appropriate:

```bash
export TERRAFORM_IMAGE=hashicorp/terraform:0.11.0
export TERRAFORM_CMD="docker run -ti --rm -w /app -v ${HOME}/.aws:/root/.aws -v ${HOME}/.ssh:/root/.ssh -v `pwd`:/app  $TERRAFORM_IMAGE"
```

### Configure `govready-q.tf`

In later versions, configuration will be abstracted/parameterized out of the Terraform file.  But for now, do this setup by hand in `govready-q.tf` and AWS:

* choose an AWS region (`us-east-2` in the example)
* make an AWS key pair (`terraform-us-east-2` in the example)
* look up the correct AMI (e.g., official CentOS 7)
* choose the instance type
* set up the VPC and security group appropriately

You'll see that the AWS credentials and private key are pointed to by volume mounts in `${TERRAFORM_CMD}`; make sure you have your secret files in the correct directories.  Remember that you can use [named profiles](https://docs.aws.amazon.com/cli/latest/userguide/cli-multiple-profiles.html) in your AWS configuration and credential files.


### Run Terraform

With the environment variables set from above, and `govready-q.tf` and AWS configured, you can now invoke Terraform like this:

```bash
${TERRAFORM_CMD} init
${TERRAFORM_CMD} plan
${TERRAFORM_CMD} apply
${TERRAFORM_CMD} show
${TERRAFORM_CMD} destroy
```

