#!/bin/bash
# This script simulates an incoming email from Mailgun for a notification whose target
# is a Discussion. The token, timestamp, and signature are specific to a Mailgun API
# key. The recipient address has a Notification object primary key and a UUID attached
# to it in the database. All of those fields will need to be updated for the test to
# be successful.
curl \
	-F 'stripped-text=Hello this is a message.' \
	-F 'recipient=q+notification+3+79cc6726-1e26-4f78-8158-ed1e2c4cb206@mg.govready.com' \
	-F 'timestamp=1478551437' \
	-F 'token=1f1cddd95014825eb8cee6edee380d33b998b847ae3c95a1ea' \
	-F 'signature=64646301d80146e9ba2f1a01caa7babc7ad8836cb2f7e58cefe13ffe77e554ca' \
	http://localhost:8000/notification_reply_email_hook
