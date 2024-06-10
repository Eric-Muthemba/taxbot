@echo off

start /b docker-compose up --build

cd utilities

start /b python start_rabbitmq_consumers.py 5
start /b python start_close_popup_job.py
