# VOCMonitor app for PC

## Overview

Python app created in Python designed to continously take messages from MQTT and display them in a chart on a webpage. Received data should be temperature, humidity and VOC index from a device on the same LAN.


## Requirements

* SQLite3
* flask
* flask_socketio
* flask_mail
* paho.mqtt
* gevent
* mosquitto broker

In order to achieve HTTPS, nginx can be used as a reverse proxy.

## Warning

In order to use email notifications for exceeded data thresholds, gmail account is required. Configuration file config.py needs to get updated with your own mail address and password.

Molitoris Erik
