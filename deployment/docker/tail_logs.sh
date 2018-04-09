#!/bin/sh
exec tail $@ /var/log/supervisor/*.log
