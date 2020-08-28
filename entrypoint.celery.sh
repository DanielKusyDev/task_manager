#!/bin/bash
echo "Waiting for circus to be installed"
until command -v circusd; do
  sleep 1
done

echo "Circus found, waiting for RabbitMQ"
until (echo > /dev/tcp/rabbit/5672); do
  sleep 1
done

echo "Running circusd"
circusd "$APP_DIR/circus.ini"
