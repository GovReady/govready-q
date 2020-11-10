# use the Alpine version because it's compact
FROM python:3.7-alpine

# copy Simple IAM Proxy Server source code
COPY iam.py login_page.html ./

# set up "networking"
ENV BIND_HOST=${BIND_HOST:-0.0.0.0}
ENV BACKEND_URL=${BACKEND_URL:-http://host.docker.internal:8001}

# run proxy
CMD [ "python3", "iam.py" ]
