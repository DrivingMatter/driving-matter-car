#!/bin/bash
# How to run this script.
# sudo crontab -e
# @reboot /home/pi/Desktop/driving-matter-car/scripts/dm-run-register-car.sh
# 
cd /home/pi/Desktop/driving-matter-car/
/usr/bin/python /home/pi/Desktop/driving-matter-car/RegisterCar.py &