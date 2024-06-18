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
from datetime import datetime
import fnmatch
import shutil
import os
from send_email import send_email_with_multiple_attachments
import zipfile
database = database()

def find_files_with_today_date_and_string(folder_path, string_to_find):

    today_date = datetime.now().strftime('%d-%m-%Y')
    
    # List all files in the specified folder
    files = os.listdir(folder_path)
    
    # Filter files based on criteria: starting with today's date and containing the specified string
    matching_files = []
    for file in files:
        if file.startswith(today_date) and fnmatch.fnmatch(file, f'*{string_to_find}*'):
            matching_files.append(file)
    print(matching_files)
    
    return matching_files


def move_file_to_folder(source_file, destination_folder):
    # Check if the destination folder exists, create it if it doesn't
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    # Move the file to the destination folder
    shutil.move(source_file, destination_folder)

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
                
                if data['operation']=="excel_filing_get_tax_refund":
                
                    xl = Excel(saving_name=data["channel_id"],channel_id=data["channel_id"])
                    xl.update_cells(P9_data = db_instance[0][16])
                    tax_refund = xl.get_tax_refund_value()
                    self.publisher({"channel_id": data["channel_id"],
                                    "message": f"Your tax refund is KSh. {tax_refund}"})
            
                elif data['operation'] in ["excel_filing","excel_filing_and_file_tax_on_itax"]:
                    xl = Excel(saving_name=data["channel_id"],channel_id=data["channel_id"])

                    xl.generate_upload_file()
               
                    source_folder = "C:\\Users\\Administrator\\Documents"
                    generated_xml_files = find_files_with_today_date_and_string(folder_path=source_folder, 
                                                                               string_to_find=db_instance[0][5])
                    
                    if len(generated_xml_files) > 0:
                        source_file=source_folder+"\\"+generated_xml_files[-1]
                        destination_folder=f"C:\\taxbot\\web_channel\\media\\uploads\\{data["channel_id"]}\\generated_documents_folder"
                        with zipfile.ZipFile(source_file, 'r') as zip_ref:
                                zip_ref.extractall(destination_folder)
                        os.remove(source_file)

                        xml_files = find_files_with_today_date_and_string(folder_path=destination_folder, 
                                                                          string_to_find="xml")

                        

                        send_email_with_multiple_attachments(recipient_email=db_instance[0][24],
                                                             tax_pin=db_instance[0][5],
                                                             channel_id=data["channel_id"],
                                                             files=xml_files)
                        
                        self.publisher({"channel_id": data["channel_id"],
                                    "message": f"Check email for your tax documents"})
                
                        if data['operation']== "excel_filing_and_file_tax_on_itax":
                            
                            screenshot_path = db_instance[0][22].replace("/app/",f"{os.getenv("BASE_PATH")}/web_channel/")
                            
                            itax = Itax(file_nil=False,
                                        channel_id=data["channel_id"],
                                            itax_pin=db_instance[0][5],
                                            itax_password=db_instance[0][6],
                                            doc_to_be_uploaded=destination_folder+"\\"+xml_files[0],
                                            screenshot_path= screenshot_path)
                            
                            if itax.wrong_password:
                                self.publisher({"channel_id": data["channel_id"],
                                                "message": f"Wrong password. kindly restart and use correct credentials"})
                            else:
                                self.publisher({"channel_id": data["channel_id"],
                                                "message": f"{screenshot_path}"})

                    else:
                        self.publisher({"channel_id": data["channel_id"],
                                        "message": f"Invalid tax pin detected."})
                        
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