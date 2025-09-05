FROM php:8.1-apache

RUN apt-get update && apt-get install -y \
    libpng-dev libjpeg-dev libwebp-dev libfreetype6-dev \
    mariadb-client unzip wget git \
    libicu-dev  # Añadido para intl

RUN docker-php-ext-install mysqli gd intl && a2enmod rewrite  # Añadido intl aquí

WORKDIR /var/www/html

RUN wget https://github.com/glpi-project/glpi/releases/download/10.0.10/glpi-10.0.10.tgz \
    && tar -xvzf glpi-10.0.10.tgz \
    && mv glpi/* . \
    && rm -rf glpi glpi-10.0.10.tgz

RUN chown -R www-data:www-data /var/www/html