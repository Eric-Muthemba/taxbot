import time

import pika
import json
from datetime import datetime
#from selenium_bot import Itax
from excel import Excel
from mpesa import Mpesa
from pdf_extractor import pdf_extractor

class rabbitMQ():
    def __init__(self,queue):
        credentials = pika.PlainCredentials("admin", "admin")
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

            if self.queue == "mpesa":
                mpesa = Mpesa()
                mpesa.stk_push(ref_no=data["ref_no"],phone_no=data["phone_no"],amount=data["amount"])
            elif self.queue == "p9_upload":
                path = data["path"].replace("/app/","/Users/erickiarie/Desktop/Projects/python-whatsapp-bot-main/itax/Channels/web_channel/")
                P9_data = pdf_extractor(path).response
                self.publisher({"channel_id": data["channel_id"], "message": "Finished data extraction.<br>Generating tax document ..."})
                xl = Excel(saving_name=data["channel_id"],P9_data=P9_data)
                xl.update_cells()
                tax_refund = 0.5
                self.publisher({"channel_id": data["channel_id"],
                                "message": f"Your tax refund is KSh. {tax_refund} ."})
                self.publisher({"channel_id": data["channel_id"],
                                "message": "To continue, enter your phone number to pay KSH. 200.00 to proceed with filing your returns"})




            print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' Processed !')



        channel = self.connection.channel()
        channel.basic_consume(queue=self.queue, on_message_callback=callback, auto_ack=True)
        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()

rabbit = rabbitMQ("p9_upload")
rabbit.consumer()