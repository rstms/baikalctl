#!/bin/sh
envsubst '$BAIKALCTL_FQDN' </etc/nginx/nginx.conf.in >/etc/nginx/nginx.conf
