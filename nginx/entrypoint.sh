#!/bin/sh
set -e

# Определяем включён ли SSL
if [ -n "$SSL_CERT_PATH" ] && [ -n "$SSL_CERT_KEY" ]; then
  export SSL_REDIRECT_OR_PROXY="return 301 https://\$host\$request_uri;"

  export SSL_SERVER_BLOCK="server {
    listen 443 ssl;
    server_name localhost;

    ssl_certificate     $SSL_CERT_PATH;
    ssl_certificate_key $SSL_CERT_KEY;

    location / {
        proxy_pass http://chatwave:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
  }"
else
  export SSL_REDIRECT_OR_PROXY="location / {
    proxy_pass http://chatwave:8000;
    proxy_set_header Host \$host;
    proxy_set_header X-Real-IP \$remote_addr;
  }"

  export SSL_SERVER_BLOCK=""
fi

# Подставляем переменные в шаблон
envsubst "$(env | cut -d= -f1 | sed 's/^/$/')" < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

# Запускаем nginx
nginx -g "daemon off;"
