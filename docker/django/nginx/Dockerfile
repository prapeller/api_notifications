FROM nginx:1.21.5-alpine

RUN rm /etc/nginx/nginx.conf
COPY ./docker/django/nginx/nginx.conf /etc/nginx/nginx.conf

RUN rm /etc/nginx/conf.d/default.conf
COPY ./docker/django/nginx/default.conf /etc/nginx/conf.d/default.conf

RUN sed -i '38 i sed -i "s/ADMIN_URL/${ADMIN_URL}/g" /etc/nginx/conf.d/default.conf' /docker-entrypoint.sh
RUN sed -i '38 i sed -i "s/DJANGO_NOTIFICATIONS_HOST/${DJANGO_NOTIFICATIONS_HOST}/g" /etc/nginx/conf.d/default.conf' /docker-entrypoint.sh
RUN sed -i '38 i sed -i "s/DJANGO_NOTIFICATIONS_PORT/${DJANGO_NOTIFICATIONS_PORT}/g" /etc/nginx/conf.d/default.conf' /docker-entrypoint.sh