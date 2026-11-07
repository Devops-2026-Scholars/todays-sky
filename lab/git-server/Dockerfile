FROM alpine:3.21

RUN apk add --no-cache git nginx fcgiwrap spawn-fcgi \
    && mkdir -p /repos /run /tmp

COPY nginx.conf /etc/nginx/nginx.conf
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80
ENTRYPOINT ["/entrypoint.sh"]
