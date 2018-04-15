#!/bin/sh
exec tail $@ /var/log/*.log
