FROM php:8.1-apache

# Install MySQL extensions
RUN docker-php-ext-install mysqli pdo pdo_mysql

# Enable Apache modules
RUN a2enmod rewrite headers

# Set ServerName to suppress warning
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf

# Configure Apache to allow .htaccess
RUN echo '<Directory /var/www/html/>' > /etc/apache2/conf-available/allow-override.conf && \
    echo '    Options Indexes FollowSymLinks' >> /etc/apache2/conf-available/allow-override.conf && \
    echo '    AllowOverride All' >> /etc/apache2/conf-available/allow-override.conf && \
    echo '    Require all granted' >> /etc/apache2/conf-available/allow-override.conf && \
    echo '</Directory>' >> /etc/apache2/conf-available/allow-override.conf && \
    a2enconf allow-override

# Set working directory
WORKDIR /var/www/html

# Copy all files
COPY . /var/www/html/

# Set correct permissions
RUN chown -R www-data:www-data /var/www/html && \
    chmod -R 755 /var/www/html

# Enable error reporting for debugging
RUN echo "display_errors = On" >> /usr/local/etc/php/php.ini && \
    echo "error_reporting = E_ALL" >> /usr/local/etc/php/php.ini

EXPOSE 80

CMD ["apache2-foreground"]