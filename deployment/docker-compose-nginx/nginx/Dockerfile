FROM nginx:alpine

ARG HOST

COPY nginx.conf /etc/nginx/nginx.conf
RUN \
   sed -i -e "s|test.example.com|$HOST|" /etc/nginx/nginx.conf \
&& mkdir -p /etc/pki/tls/certs /etc/pki/tls/private \
&& apk add --no-cache --update openssl \
&& openssl req -newkey rsa:4096 \
    -x509 \
    -sha256 \
    -days 3650 \
    -nodes \
    -out /etc/pki/tls/certs/cert.pem \
    -keyout /etc/pki/tls/private/key.pem \
    -subj "/C=US/ST=State/L=Locality/O=Organization/OU=Organizational Unit/CN=$HOST"
