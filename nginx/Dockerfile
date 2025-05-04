FROM nginx:alpine

RUN apk add --no-cache bash gettext

WORKDIR /etc/nginx


COPY nginx/nginx.conf.template /etc/nginx/nginx.conf.template
COPY nginx/entrypoint.sh /etc/nginx/entrypoint.sh

RUN chmod +x /etc/nginx/entrypoint.sh

ENTRYPOINT ["/etc/nginx/entrypoint.sh"]