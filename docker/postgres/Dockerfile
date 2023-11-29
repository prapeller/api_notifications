FROM postgres:13.9

#COPY docker/postgres/init.sql /docker-entrypoint-initdb.d/

COPY api_notifications/scripts/postgres /usr/local/bin/temp
RUN chmod +x /usr/local/bin/temp/* && \
    mv /usr/local/bin/temp/* /usr/local/bin &&  \
    rmdir /usr/local/bin/temp