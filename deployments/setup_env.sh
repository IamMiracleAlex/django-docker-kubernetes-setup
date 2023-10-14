#!/bin/sh

echo DEBUG=0 >> .env.prod
echo ENVIRONMENT=$ENVIRONMENT >> .env.prod

echo SECRET_KEY=$SECRET_KEY >> .env.prod
echo ENGINE=$ENGINE >> .env.prod
echo DB_NAME=$DB_NAME >> .env.prod
echo POSTGRES_USER=$POSTGRES_USER >> .env.prod
echo POSTGRES_PASSWORD=$POSTGRES_PASSWORD >> .env.prod
echo DB_HOST=$DB_HOST >> .env.prod
echo DB_PORT=$DB_PORT >> .env.prod

echo EMAIL_BACKEND=$EMAIL_BACKEND >> .env.prod
echo EMAIL_HOST=$EMAIL_HOST >> .env.prod
echo EMAIL_HOST_USER=$EMAIL_HOST_USER >> .env.prod
echo EMAIL_HOST_PASSWORD=$EMAIL_HOST_PASSWORD >> .env.prod
echo EMAIL_PORT=$EMAIL_PORT >> .env.prod
echo EMAIL_USE_TLS=$EMAIL_USE_TLS >> .env.prod
echo DEFAULT_FROM_EMAIL=$DEFAULT_FROM_EMAIL >> .env.prod
