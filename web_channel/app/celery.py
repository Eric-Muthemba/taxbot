from __future__ import absolute_import, unicode_literals

# Standard Library
import json
import os

import kombu
from celery import Celery, bootsteps

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

app = Celery("app")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# setting publisher
with app.pool.acquire(block=True) as conn:
    exchange = kombu.Exchange( name='myexchange', type='direct', durable=True, channel=conn)
    exchange.declare()
    mpesa_queue = kombu.Queue(  name='excel_filing_and_file_tax_on_itax', exchange=exchange, routing_key='excel_filing_and_file_tax_on_itax',  channel=conn,message_ttl=600, queue_arguments={ 'x-queue-type': 'classic' }, durable=True)
    mpesa_queue.declare()
    excel_filing_queue = kombu.Queue(name='excel_filing', exchange=exchange, routing_key='excel_filing_queue', channel=conn, message_ttl=600,queue_arguments={'x-queue-type': 'classic'}, durable=True)
    excel_filing_queue.declare()
    p9_upload_queue = kombu.Queue(name='p9_upload', exchange=exchange, routing_key='p9_upload',channel=conn, message_ttl=600, queue_arguments={'x-queue-type': 'classic'},durable=True)
    p9_upload_queue.declare()
    queue = kombu.Queue(name='notifications', exchange=exchange, routing_key='notifications', channel=conn,message_ttl=600, queue_arguments={'x-queue-type': 'classic'}, durable=True)
    queue.declare()

# setting consumer
class MyConsumerStep(bootsteps.ConsumerStep):

    def get_consumers(self, channel):
        return [kombu.Consumer(channel, queues=[queue], callbacks=[self.handle_message], accept=['json'])]

    def handle_message(self, body, message):
        channel_layer = get_channel_layer()
        print('Received message: {0!r}'.format(body))
        try:
            body = json.loads(body)
            room_group_name = f"chat_{body['channel_id']}"
            print(room_group_name)
            async_to_sync(channel_layer.group_send)(room_group_name, {"type": "chat_message", "message": body["message"]})

        except Exception as e:
            print("error",e)
        message.ack()

app.steps['consumer'].add(MyConsumerStep)

