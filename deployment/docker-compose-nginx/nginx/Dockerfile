FROM nginx:alpine

ARG HOST

COPY nginx.conf /etc/nginx/nginx.conf
RUN sed -i -e "s|test.example.com|$HOST|" /etc/nginx/nginx.conf

COPY cert.pem /etc/pki/tls/certs/cert.pem
COPY key.pem /etc/pki/tls/private/key.pem
