#!/bin/sh

# run this, then 'cf push'

vendor_requirements() {
  mkdir -p vendor
  pip download --dest vendor -r requirements.txt
}

static_requirements() {
  ./deployment/fetch-vendor-resources.sh
}

vendor_requirements
static_requirements
