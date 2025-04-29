FROM nginx:stable-alpine3.21


RUN apk update --no-check-certificate && apk add --no-check-certificate bash

COPY --chown=nginx:nginx nginx.conf /etc/nginx/nginx.conf
COPY --chown=nginx:nginx start.sh /app/start.sh

WORKDIR /app

RUN chown -R nginx:nginx /app && chmod -R 755 /app && \
        chown -R nginx:nginx /var/cache/nginx && \
        chown -R nginx:nginx /var/log/nginx && \
        chmod -R 755 /var/log/nginx; \
        chown -R nginx:nginx /etc/nginx/conf.d
RUN touch /var/run/nginx.pid && chown -R nginx:nginx /var/run/nginx.pid

USER nginx

CMD ["nginx", "-g", "'daemon off;'"]