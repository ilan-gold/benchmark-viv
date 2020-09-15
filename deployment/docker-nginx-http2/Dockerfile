FROM nginx
RUN openssl req -config /etc/ssl/openssl.conf -new -newkey rsa:2048 -nodes -keyout /etc/ssl/private/nginx-selfsigned.key -days 365 -out /etc/ssl/certs/nginx-selfsigned.crt
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
EXPOSE 443