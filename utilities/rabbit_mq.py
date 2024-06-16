import time
import argparse
import pika
import json
from datetime import datetime
from selenium_bot import Itax
from excel import Excel
from mpesa import Mpesa
from pdf_extractor import pdf_extractor
import os
from database import database


database = database()
class rabbitMQ():
    
    def __init__(self,queue):
        credentials = pika.PlainCredentials("guest", "guest")
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='127.0.0.1', port="5672", credentials=credentials))
        self.queue = queue
        self.exchange = 'myexchange'
        self.notifications_queue = "notifications"


    def publisher(self, data):
        channel = self.connection.channel()
        channel.queue_declare(queue=self.notifications_queue,durable=True,arguments={'x-message-ttl': 600000} )
        channel.basic_publish(exchange=self.exchange, routing_key=self.notifications_queue, body=json.dumps(data))
        #self.connection.close()
        print("published")

    def consumer(self):
        def callback(ch, method, properties, body):

            print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' Processing...')
            data = json.loads(body)
            print(data)

            if self.queue == "p9_upload":
                path = data["path"].replace("/app/",f"{os.getenv("BASE_PATH")}/web_channel/")
                P9_data = pdf_extractor(path).response
                #update row in db
                database.update(data={"tax_document_extracted_info":(json.dumps(P9_data))},
                                channel=data["channel"],
                                channel_id=data["channel_id"],
                                session_status="Active")

                self.publisher({"channel_id": data["channel_id"],
                                "message": "Finished data extraction.<br>Generating tax document ..."})

            elif self.queue == "excel_filing":
                db_instance = database.read(channel_id=data["channel_id"])            
                P9_data = db_instance[0][16]

                xl = Excel(saving_name=data["channel_id"],P9_data=P9_data,channel_id=data["channel_id"])
                xl.update_cells()
                tax_refund = xl.get_tax_refund_value()
                if data['operation']=="excel_filing_get_tax_refund":
                    self.publisher({"channel_id": data["channel_id"],
                                    "message": f"Your tax refund is KSh. {tax_refund}"})
            
                elif data['operation'] in ["excel_filing","excel_filing_and_file_tax_on_itax"]:
                    xl.generate_upload_file()
                    self.publisher({"channel_id": data["channel_id"],
                                    "message": f"Here is your generated documents"})
                    
                if data['operation']== "excel_filing_and_file_tax_on_itax":
                    screenshot_path = db_instance[8].replace("/app/",f"{os.getenv("BASE_PATH")}/web_channel/")
                    print(db_instance)
                    '''itax = Itax(file_nil=False,
                                    itax_pin=data["channel_id"],
                                    itax_password=data["channel_id"],
                                    doc_to_be_uploaded=xl.saving_path,
                                    screenshot_path= screenshot_path)
                    
                    if itax.wrong_password:
                        self.publisher({"channel_id": data["channel_id"],
                                        "message": f"Wrong password. kindly restart and use correct credentials"})
                    else:'''
                    self.publisher({"channel_id": data["channel_id"],
                                        "message": f"{screenshot_path}"})

            
                
            print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' Processed !')



        channel = self.connection.channel()
        channel.basic_consume(queue=self.queue, on_message_callback=callback, auto_ack=True)
        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()


parser = argparse.ArgumentParser(description='start rabbitmq consumer')
# Add arguments
parser.add_argument('queue', metavar='N', type=str, nargs='+', help='queue')
# Parse the arguments
args = parser.parse_args()
queue = args.queue[0]

rabbit = rabbitMQ(queue)
rabbit.consumer()