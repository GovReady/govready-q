#!/bin/sh
# Get uWSGI's stats. Same as 'telnet localhost 9191'
# but with less noise.
exec nc localhost 9191 2>/dev/null
