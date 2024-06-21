from celery import shared_task
from django.core.mail import EmailMessage
from .selenium_bot import Itax
from jobs.models import Job
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from time import sleep
import os
from .pdf_extractor import pdf_extractor
from .send_email import send_email_with_multiple_attachments


@shared_task
def itax(operation=None,action=None,channel=None,channel_id=None):
    job = Job.objects.get(channel=channel, channel_id=channel_id)
    response = {"id": channel_id,"is_start":False, "text": "no_obligations", "error": False}

    if operation == "extract_p9_document_info":
        data = pdf_extractor(job.p9_file_path)
        response = {"id": channel_id, "is_start":False, "extracted_data": data.response,"standard_data":data.standard_data}
    else:
        directory = os.getenv("BASE_UPLOAD_DIR").format(channel_id)
        if not os.path.exists(directory):
            os.makedirs(directory)

        kra_pin = job.kra_pin
        kra_password = job.kra_password

        itax = Itax(itax_pin=kra_pin,
                    itax_password=kra_password,
                    task_id=channel_id,
                    filing_date_from=job.date_to_file
                    )
        itax.load_itax_website()
        itax.login_to_itax_website()


        if not (itax.invalid_pin or itax.wrong_password or itax.is_blocked):
            if operation == "check_if_tax_obligation_exists":
                try:
                    obligations_and_date_to_file = itax.get_obligations_and_date_to_file()
                    job.has_tax_obligations = obligations_and_date_to_file["has_obligations"]
                    job.date_to_file = obligations_and_date_to_file["tax_return_period_from"]
                    job.save()
                    if obligations_and_date_to_file["has_obligations"]:
                        response["text"] = "has_obligations"
                    response["expected_filing_period"] = obligations_and_date_to_file["tax_return_period_from"]
                except Exception as e:
                    print(e)

                    response = {"id": channel_id, "is_start": False, "error": True,"text": "An error occured, kindly retry in a few."}

            if operation == "file_nil_returns":
                try:
                    itax.navigate_to_file_nil_tax_page()
                    job.screenshot_path = itax.screenshot_path
                    job.is_filed = True
                    job.save()
                    response = {"id": channel_id, "is_start": False, "text": "Congraturations Nil Tax sucessfully filled", "error": False}
                    send_email_with_multiple_attachments(recipient_email=job.email,
                                                         path=itax.screenshot_path)
                except Exception as e:
                    print(e)
                    response = {"id": channel_id, "is_start": False, "error": True}

            elif operation == "file_p9_tax":
                try:
                    itax.navigate_to_filing_tax_page()
                    itax.file_itr_tax( pension_contributions=job.pension_contributions,
                                            tax_payer_nhif_pin=job.nhif_no,
                                            nhif_contributions=job.nhif_contributions)

                    if itax.error_detected:
                        response = {"id": channel_id, "is_start": False, "error": True}
                    else:
                        response = {"id": channel_id, "is_start": False, "error": False, "text":"Congraturations Tax sucessfully filled"}
                        job.screenshot_path = itax.screenshot_path
                        job.save()
                        send_email_with_multiple_attachments(recipient_email=job.email,
                                                             path=itax.screenshot_path)

                except Exception as e:
                    print(e)
                    response = {"id": channel_id, "is_start": False, "error": True}

            itax.driver.close()
        else:
            if itax.is_blocked or itax.wrong_password:
                response = {"id": channel_id,
                            "is_start": False,
                            "text": f"Error: {itax.error_text} <br>Correct the error above and retry.",
                            "error": True}
            if itax.invalid_pin:
                response = {"id": channel_id,
                            "is_start": False,
                            "text": "Invalid PIN.",
                            "error": True}

    try:
        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            str(channel_id),
            {
                'type': 'chat_message',
                'message': response
            }
        )

    except Exception as e:
        print(e)

    print(action,job)
