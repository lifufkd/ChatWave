#!/bin/sh
set -e

export SSL_CERT_PATH=$SSL_CERT_PATH
export SSL_CERT_KEY=$SSL_CERT_KEY

# Подставляем переменные в шаблон
envsubst "$(env | cut -d= -f1 | sed 's/^/$/')" < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

# Запускаем nginx
nginx -g "daemon off;"
