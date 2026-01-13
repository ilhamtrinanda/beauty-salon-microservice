FROM php:8.1-apache
RUN docker-php-ext-install mysqli pdo pdo_mysql
RUN a2enmod rewrite
COPY . /var/www/html/
COPY .htaccess /var/www/html/.htaccess
RUN chown -R www-data:www-data /var/www/html
RUN sed -i '/<Directory \/var\/www\/>/,/<\/Directory>/ s/AllowOverride None/AllowOverride All/' /etc/apache2/apache2.conf
EXPOSE 80