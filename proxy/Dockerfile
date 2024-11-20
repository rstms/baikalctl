FROM nginx
COPY nginx.conf /etc/nginx/nginx.conf.in
COPY --chmod=0755 configure /docker-entrypoint.d/configure
COPY require_client_cert /etc/nginx/require_client_cert
RUN mkdir -p /var/www/acme
RUN chown -R 0755 /var/www/acme
COPY VERSION /
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
