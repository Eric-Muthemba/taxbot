echo "Starting docker-compose ... "
docker-compose up --build -d &
echo "Docker-compose started."
#cd utilities
#echo "Starting consumers and support programs ..."
#python start_close_popup_job.py &
#python start_rabbitmq_consumers.py 5 &
#echo "Consumers started."

