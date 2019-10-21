FROM nginx:alpine

ARG HOST

COPY nginx.conf /etc/nginx/nginx.conf
RUN sed -i -e "s|test.example.com|$HOST|" /etc/nginx/nginx.conf

COPY cert.pem /tmp/fullchain.pem
COPY key.pem /tmp/privkey.pem

CMD "cp /tmp/*.pem /etc/letsencrypt/live/text.example.com/"