FROM nginx
COPY --chmod=0644 nginx.conf.in /etc/nginx/nginx.conf.in
COPY --chmod=0755 00-configure.sh /docker-entrypoint.d/
COPY require_client_cert /etc/nginx/require_client_cert
RUN mkdir -p /var/www/acme
RUN chown -R 0755 /var/www/acme
COPY --chmod=0644 VERSION /
