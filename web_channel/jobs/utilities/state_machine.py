from jobs.models import Job
import json
import os
from django.conf import settings
from app.celery import app
import requests


def publish_notification(message):
    with app.producer_pool.acquire(block=True) as producer:
        producer.publish( message,  exchange='myexchange', routing_key='p9_upload',)

def initiate_stkpush(amount,msisdn,account_no):
    url = "https://tinypesa.com/api/v1/express/initialize"
    payload = json.dumps({
      "amount": amount,
      "msisdn": str(msisdn),
      "account_no": str(account_no)
    })
    headers = {'Apikey': 'Egci8yRoMlv','Content-Type': 'application/json'}

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    return response.json()


def state_machine(channel,message,channel_id):


    if message == "":
        return { "message": "Invalid input."}

    jobs = Job.objects.filter(channel=channel, channel_id=channel_id, session_status="Active")

    print(jobs[0].step)
    print(message)
    if channel == "Web":
        if not jobs:
            return {"message": "No active job found"}
    else:
        if not jobs:
            Job.objects.create(channel=channel, channel_id=channel_id, session_status="Active")
            jobs = Job.objects.filter(channel=channel, channel_id=channel_id, session_status="Active")



    if message == "cancelled":
        jobs.delete()

    elif message == "reset" or jobs[0].step == "START":
        response = {
            "message": "Hello, my name is TaxbotKE<br>"
                       "I will assist you file your tax obligations.<br>"
                       "NB visit https://itax.kra.go.ke/ to reset password.<br>"
                       "For any assistance call 0726215805.<br><br>"
                       "To continue choose a service.",
            "action": "START",
            "keyboard_type": "options",
            "data": [
                {"key": "File Taxes","value": 1},
                {"key": "Check on previously filed status", "value": 2}
            ]
        }
        jobs.update(step="CHOOSE_PROCESS",payment_status="Unpaid")
    elif jobs[0].step == "CHOOSE_PROCESS":
        response = {}

        if message == "1":
            response["message"] = "Which year do you want to file for?"
            jobs.update(step="GET_YEAR_TO_FILE")
        elif message == "2":
            response["message"] = "Kindly input the mpesa received after payment."
            jobs.update(step="CHECK_PREVIOUS_STATUS")
        else:
            response["message"] = "Invalid input."
    elif jobs[0].step == "CHECK_PREVIOUS_STATUS":
        jobs = Job.objects.filter(channel=channel, mpesa_reference=message)
        if jobs.count() == 0:
            response = {"message": "Mpesa Reference does not exist."}
            jobs.update(step="START")
        else:
            status = "done"
            response = {"message": f"The status of your filing is :{status}",
                        "links":["https://itax.kra.go.ke/",]}
            jobs.update(step="START")
    elif jobs[0].step == "PREVIOUS_STATUS":
        try:
            job = Job.objects.get(channel="Web", uuid=message)
            response = {
                "message": f"Your KRA filing job with Ticket no. {message} Exists"
            }
            jobs.update(session_status="Inactive")
        except:
            response = {
                "message": f"Your KRA filing job with Ticket no. {message} doesn't exists"
            }
    elif jobs[0].step == "GET_YEAR_TO_FILE":
        response = {"message": "Kindly enter your KRA PIN"}
        try:
            year_of_filling = int(message)
            if year_of_filling < 1990 or year_of_filling > 2023:
                response["message"] = "Invalid input.<br>Which year do you want to file for?"
            else:
                jobs.update(year_of_filling=int(message), step="GET_KRA_PIN")
        except ValueError:
            response["message"] = "Invalid input.<br>Which year do you want to file for?"
    elif jobs[0].step == "GET_KRA_PIN":
        response = {}

        if len(message) == 11:
            response = {
                "message": f"Were you employed or had any source of income in {jobs[0].year_of_filling}",
                "keyboard_type": "options",
                "data": [
                    {"key": "Yes", "value": 1},
                    {"key": "No", "value": 0},
                ]
            }
            jobs.update(kra_pin=message, step="CHECK_IF_EMPLOYED_OR_HAD_INCOME")
        else:
            response["message"] = "Invalid KRA Pin entered.<br>Kindly enter your correct KRA PIN?"
    elif jobs[0].step == "CHECK_IF_EMPLOYED_OR_HAD_INCOME":

        if message == "1":
            response = {"message": "From 2023, KRA allows for tax relief from your NHIF contributions.\n Enter your NHIF Number ..."}
            jobs.update(step="GET_NHIF_NO")
        else:
            response = {"message": " To File Nil returns, Enter your phone number to pay KES 100.00"}
            jobs.update(file_nil=True, step="REQUEST_PAYMENT")
    elif jobs[0].step == "GET_NHIF_NO":
        jobs.update(nhif_no=message, step="UPLOAD_P9_FORM")
        response = {
            "keyboard_type": "options",
            "message": f"Answer yes if any of the below apply in the year {jobs[0].year_of_filling}  <br>"
                       f"1.) Did you have more than one employer? <br>"
                       f"2.) Did you have any other source of income apart from employment?<br>"
                       f"3.) Did you have any partnership income?<br>"
                       f"4.) Did you have any estate trust income?<br>"
                       f"5.) Did your employer provide you with a car?<br>"
                       f"6.) Did you have a mortgage?<br>"
                       f"7.) Did you have home ownership saving plan?<br>"
                       f"8.) Did you have any extra insurance policy apart from NHIF ?<br>"
                       f"9.) Did you have a commercial vehicle (PSV,Cabs) ?<br>"
                       f"10.) Did you have income from a foreign country ?<br>"
                       f"11.) Did you have a disability certificate ?<br>"
                       f"12.) Did you want to declare your wife's income ?",
            "data": [
                {"key": "Yes","value": 1},
                {"key": "No","value": 0},
            ]
        }
    elif jobs[0].step == "UPLOAD_P9_FORM":
        response = {
            "keyboard_type": "upload_pdf",
            "message": "Kindly upload your P9 form"
        }
        jobs.update(step="GENERATING_TAX_DOCUMENT")
    elif jobs[0].step == "GENERATING_TAX_DOCUMENT":
        # Save the file using FileSystemStorage
        base_path = os.path.join(settings.MEDIA_ROOT, f'uploads/{channel_id}')
        screenshot_path = base_path +f'/screenshot'

        if not os.path.exists(base_path):
            os.makedirs(base_path)
        if not os.path.exists(screenshot_path):
            os.makedirs(screenshot_path)

        file_path=base_path+"/file.pdf"
        with open(file_path, 'wb') as f:
            print(type(message))
            f.write(message)

        publish_notification({'operation':"p9_form",
                              'channel':'Web',
                              'channel_id': channel_id,
                              "path":file_path})
        response = { "message": "Processing ..." }
        jobs.update(screenshot_path=screenshot_path,step="VALIDATE_EXTRACTED_INFO")
    elif jobs[0].step == "VALIDATE_EXTRACTED_INFO":
        tax_document_extracted_info = json.loads(jobs[0].tax_document_extracted_info)
        print(tax_document_extracted_info)
        response = {
            "keyboard_type": "data_validator",
            "message": "Kindly confirm if the following extracted information is correct",
            "data":[
                {"key": "Employer name","value": tax_document_extracted_info['standard_data']['employers_name']},
                {"key": "Employer pin","value": tax_document_extracted_info['standard_data']['employers_pin']},
                {"key": "January gross","value": tax_document_extracted_info['data'][0]['A']},
                {"key": "February gross","value": tax_document_extracted_info['data'][1]['A']},
                {"key": "March gross","value": tax_document_extracted_info['data'][2]['A']},
                {"key": "April gross","value": tax_document_extracted_info['data'][3]['A']},
                {"key": "May gross","value": tax_document_extracted_info['data'][4]['A']},
                {"key": "June gross","value": tax_document_extracted_info['data'][5]['A']},
                {"key": "July gross","value": tax_document_extracted_info['data'][6]['A']},
                {"key": "August gross","value": tax_document_extracted_info['data'][7]['A']},
                {"key": "September gross","value": tax_document_extracted_info['data'][8]['A']},
                {"key": "October gross","value": tax_document_extracted_info['data'][9]['A']},
                {"key": "November gross","value": tax_document_extracted_info['data'][10]['A']},
                {"key": "December gross","value": tax_document_extracted_info['data'][11]['A']},
                {"key": "A Total","value": tax_document_extracted_info['totals']['totals_A']},
                {"key": "B Total","value": tax_document_extracted_info['totals']['totals_B']},
                {"key": "C Total","value": tax_document_extracted_info['totals']['totals_C']},
                {"key": "D Total","value": tax_document_extracted_info['totals']['totals_D']},
                {"key": "E1 Total","value": tax_document_extracted_info['totals']['totals_E1']},
                {"key": "E2 Total","value": tax_document_extracted_info['totals']['totals_E2']},
                {"key": "E3 Total","value": tax_document_extracted_info['totals']['totals_E3']},
                {"key": "F Total","value": tax_document_extracted_info['totals']['totals_F']},
                {"key": "G Total","value": tax_document_extracted_info['totals']['totals_G']},
                {"key": "H Total","value": tax_document_extracted_info['totals']['totals_H']},
                {"key": "J Total","value": tax_document_extracted_info['totals']['totals_J']},
                {"key": "K Personal Relief Total","value": tax_document_extracted_info['totals']['totals_personal_relief_K']},
                {"key": "K Insurance Relief Total","value": tax_document_extracted_info['totals']['totals_insurance_relief-K']},
                {"key": "L Total","value": tax_document_extracted_info['totals']['totals_L']},
                {"position":"end"}
            ]
        }
        jobs.update(step="CHOOSE_SERVICE")
    elif jobs[0].step == "CHOOSE_SERVICE":
        response = {
            "message": "Select the services you want",
            "keyboard_type": "options",
            "data":[
                    {"key": "Generate filed tax return documents Excel + XML (final document to upload to itax portal)","value":1},
                    {"key": "Auto file your tax on the itax portal (includes 1)", "value": 2}
            ]
        }
        jobs.update( step="CHECK_SERVICE_CHOOSEN")
    elif jobs[0].step == "CHECK_SERVICE_CHOOSEN":
            response = {"message": "To continue, Enter your phone number to pay KES 200.00"}
            jobs.update( output_option=message,step="REQUEST_PAYMENT")
    elif jobs[0].step == "GET_KRA_PASSWORD":
        response = {"message": "To continue, Enter your phone number to pay KES 200.00"}
        jobs.update(kra_password=message, step="REQUEST_PAYMENT")
    elif jobs[0].step == "REQUEST_PAYMENT" or (message == "2" and jobs[0].step == "CHECK_IF_PAID"):
        if len(message) >= 9:
            phone_number = "0" + message[-9:]
            if jobs[0].file_nil:
                amount=1
            else:
                amount=2
            jobs.update(phone_number=phone_number,expected_payment_amount=amount)
            try:
                initiate_stkpush(amount=amount, msisdn=phone_number, account_no=str(jobs[0].uuid))
            except Exception as e:
                print(e)
        elif message == "2" and len(jobs[0].phone_number) == 10:
            try:
                initiate_stkpush(amount=jobs[0].expected_payment_amount, msisdn=jobs[0].phone_number, account_no=str(jobs[0].uuid))
            except Exception as e:
                print(e)
        response = {"message": "Once paid press PAID else CANCEL.",
                    "keyboard_type": "options",
                    "data": [
                        {"key": "Paid", "value": 1},
                        {"key": "Retrigger STK push", "value": 2},
                        {"key": "Cancel", "value": 0}
                    ]
                    }
        jobs.update(step="CHECK_IF_PAID")
    elif jobs[0].step == "CHECK_IF_PAID":
        if message == "1":


            if jobs[0].mpesa_paid_amount == jobs[0].expected_payment_amount:
                response = {"message": "Filing. Kindly be patient."}
                if jobs[0].file_nil:
                    publish_notification({'operation': "excel_filing_and_file_tax_on_itax",
                                          'channel': 'Web',
                                          'channel_id': channel_id,
                                          'file_nil':True})

                else:
                    if jobs[0].output_option == "1":
                            publish_notification({'operation': "excel_filing",
                                                  'channel': 'Web',
                                                  'channel_id': channel_id})
                    elif jobs[0].output_option == "2":
                            publish_notification({'operation': "excel_filing_and_file_tax_on_itax",
                                                  'channel': 'Web',
                                                  'channel_id': channel_id,
                                                  'file_nil':False})
                jobs.update(step="GENERATING_TAX_DOCUMENT", payment_status="PAID")

            else:
                response = {"message": "Not paid.<br>Once paid press PAID else CANCEL.<br>Press Retrigger STK push to get the stk push ",
                    "keyboard_type": "options",
                    "data": [
                        {"key": "Paid", "value": 1},
                        {"key": "Retrigger STK push", "value": 2},
                        {"key": "Cancel", "value": 0}
                    ]
                    }

        else:
            response = { "message": "Thanks for using TaxbotKE." }
            jobs.update(step="DONE")
    elif jobs[0].step == "GENERATING_TAX_DOCUMENT":
        response = {"message": message}
        if "END" in message:
            jobs.update(step="DONE")
    else:
        response = {
            "message": "Hello, my name is TaxbotKE<br>"
                       "I will assist you file your tax obligations.<br>"
                       "NB visit https://itax.kra.go.ke/ to reset password.<br>"
                       "For any assistance call 0726215805.<br><br>"
                       "Do you want to :<br>"
                       "1.) File Taxes <br>"
                       "2.) Check on previously filed status",
            "action": "START"
        }
        jobs.update(step="CHOOSE_PROCESS")

    if channel != "Web" and "message" in list(response.keys()):
        response["message"] = response["message"].replace("<br>","\n")

    return response

