import argparse
import threading
from rabbit_mq import rabbitMQ

def main():
    # Create the parser
    parser = argparse.ArgumentParser(description='start rabbitmq consumer')

    # Add arguments
    parser.add_argument('number_of_consumers', metavar='N', type=int, nargs='+', help='an integer for the number of consumers')

    # Parse the arguments
    args = parser.parse_args()
    number_of_consumers = args.number_of_consumers[0]

    def consumer():
        rabbit_mq = rabbitMQ()
        rabbit_mq.consumer()


    for thread_number in range(0,number_of_consumers):
        thread = threading.Thread(target=consumer)
        thread.start()
        thread.join()


if __name__ == '__main__':
    main()
