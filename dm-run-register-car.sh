#!/bin/bash
# How to run this script.
# sudo crontab -e
# @reboot /home/pi/Desktop/driving-matter-car/dm-run-register-car.sh
# 
cd /home/pi/Desktop/driving-matter-car/classes/
/usr/bin/python /home/pi/Desktop/driving-matter-car/classes/RegisterCar.py &