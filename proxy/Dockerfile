FROM nginx
copy nginx.conf /etc/nginx/nginx.conf
copy require_client_cert /etc/nginx/require_client_cert
copy ssl/*.pem /etc/ssl/
copy ssl/*.key /etc/ssl/private/

RUN find /etc/nginx
run find /etc/ssl
