from jobs.models import Job
import json
import os
from django.conf import settings
from app.celery import app
import requests
from jobs.tasks import itax

def publish_notification(message):
    with app.producer_pool.acquire(block=True) as producer:
        producer.publish(message, exchange='myexchange', routing_key=message['queue'], )


def initiate_stkpush(amount, msisdn, reference):
    url = "https://tinypesa.com/api/v1/express/initialize"
    payload = json.dumps({
        "amount": amount,
        "msisdn": str(msisdn),
        "account_no": str(reference)
    })
    headers = {'Apikey': 'Egci8yRoMlv', 'Content-Type': 'application/json'}

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    return response.json()


user_matrix =  {
    "1": {"question":"Did you have withholding certificates?","required_docs":"Withholding certificates *optional"},
    "2": {"question":"Did you have a house mortgage?","required_docs":"Mortgage documentation"},
    "3": {"question": "Did you have more than one employer?", "required_docs": "Your other employers P9"},
    "4": {"question": "Did you have any partnership income?", "required_docs": "Details of Share/Surplus/Loss in which you are a partner."},
    "5": {"question": "Did you have an estate trust income?","required_docs": "Details of share of income in which you are a beneficiary of estate/trust/settlement"},
    "6": {"question": "Did you your employer supply you with a car?", "required_docs": "Computation of value of car benefit"},
    "7": {"question": "Did you have a home ownership saving plan?","required_docs": "Computation of deduction of home ownership saving plan"},
    "8": {"question": "Did you any commercial vehicle?","required_docs": "Details of advance tax paid on commercial vehicles"},
    "9": {"question": "Did you earn any income from foreign country?","required_docs": "Details of double taxation avoidance agreement"}

}

def state_machine(channel, message,file=None):
    if message["is_start"] == True:
        job_object = {
            "channel": channel,
            "channel_id": message["id"],
            "email": message["email"].lower(),
            "action": message["action"],
        }
        if "itax_pin" in message:
            job_object["kra_pin"] = message["itax_pin"].upper()
        if "itax_password" in message:
            job_object["kra_password"] = message["itax_password"]
        if "nhif_no" in message:
            job_object["nhif_no"] = message["nhif_no"]


        if message['action'] == "1": #file tax with p9
            job_object["next_step"] = "GET_TAXPAYER_MATRIX_DATA"
            job_object["expected_payment_amount"] = 200
            response = {"message":["Kindly check the box if the statement relates  to you:"],
                        "has_table":True,
                        "table_type":"toggle",
                        "table_id":"taxpayer_matrix_table",
                        "data": [{"id": key, "label": user_matrix[key]['question'] } for key in user_matrix],
                        "keyboard_type": "buttons",
                        "buttons":[{"id":"taxpayer_matrix","label":"submit"}]}

        elif message['action'] == "2": #file nil returns
            job_object["next_step"] = "VERIFYING_IF_YOU_HAVE_TAX_OBLIGATIONS"
            job_object["expected_payment_amount"] = 100
            response = {
                        "message": ["Hold on as I check if you have any tax obligations ..."],
                        "has_table": False,
                        "keyboard_type": None
                       }

        elif message['action'] == "3": #get witholding taxes
            job_object["next_step"] = "GET_PHONE_NUMBER"
            job_object["expected_payment_amount"] = 50
            response = {
                "message": ["To get your witholding taxes documents, kindly input your valid phone number to pay KES 50.00 to proceed."],
                "has_table": False,
                "keyboard_type": "normal"}

        elif message['action'] == "4": #check year to file
            job_object["next_step"] = "GET_PHONE_NUMBER"
            job_object["expected_payment_amount"] = 15
            response = {
                "message": ["To proceed and check which year you are due for filing, kindly input your valid phone number to pay KES 15.00 to proceed."],
                "has_table": False,
                "keyboard_type": "normal"}

        elif message['action'] == "5": #check status
            job_object["expected_payment_amount"] = 0
            job_object["next_step"] = "CHECK_PREVIOUS_FILINGS_STATUS"

            existing_jobs = Job.objects.filter(email=message["email"],payment_status = "Paid")
            if existing_jobs.count() == 0:
                response = {"message": ["You have no taxes filed with TaxbotKE"],
                            "has_table": False,
                            "keyboard_type": None}
            else:
                response_text ="<br>".join([f"{idx+1}.) PIN: {existing_job.kra_pin}, Filed on:{existing_job.date_added}, Filing status: {'Filed' if existing_job.is_filed else 'Pending'}"  for idx,existing_job in enumerate(existing_jobs)])


                response = {"message": ["Here are your current paid active tax filings.<br><br>"+response_text],
                            "has_table": False,
                            "keyboard_type": None}

            """response = {
                "message": ["Here are your current active tax filings."],
                "has_table": False,
                "keyboard_type": "buttons",
                "buttons":[
                            {"id":"1","label":"job 1"},
                            {"id": "2", "label": "job 2"}
                          ]}"""

        else:
            return ({"message": ["Invalid input"],
                     "has_table": False,
                     "keyboard_type": None})


        job = Job.objects.create(**job_object)

        if message["action"] == "2":
            itax.delay(operation="check_if_tax_obligation_exists",channel=channel,channel_id=message["id"])


    else:
        job = Job.objects.get(channel=channel, channel_id=message["id"])

        print(job.next_step)

        if job.next_step =="GET_TAXPAYER_MATRIX_DATA":
            matrix = [  f"{idx+1}.) {user_matrix[key]['required_docs']}" for idx,key in enumerate(message["data"]) if message["data"][key] == True ]

            if len(matrix) > 0:
                response = {
                    "message": ["Kindly upload the following documents:<br>"+"<br>".join(matrix)],
                    "has_table": False,
                    "keyboard_type": "multi_upload"
                }
                job.next_step = "UPLOAD_COMPLEX_SCENARIO_DOCUMENTS"
                job.expected_payment_amount = 1500
                job.is_manual = True
                job.save()
                print(response)

            else:
               response =  {
                                "message": ["Bot checking for any existing witholding tax obligations.<br><br>Do not refresh, this might take up to 1 minute to complete."],
                                "has_table": False,
                                "keyboard_type": None
                            }
               job.next_step ="VERIFYING_IF_YOU_HAVE_TAX_OBLIGATIONS"
               job.save()
               itax.delay(operation="check_if_tax_obligation_exists",channel=channel, channel_id=message["id"])

        elif job.next_step == "VERIFYING_IF_YOU_HAVE_TAX_OBLIGATIONS":
            print(message)
            if message["error"]:
                response = {
                    "message": [message["text"]],
                    "has_table": False,
                    "keyboard_type": None
                }
            elif message["action"] == "haven't filed in a while":
                response = {"message": ["It looks like you haven't filed your taxes for multiple years.<br><br>" \
                                        "Redirecting you to our live human agent<br><br>" \
                                        "To proceed, kindly input your valid phone number to pay KES 1500.00 to proceed."],
                            "has_table": False,
                            "keyboard_type": "normal"}

                job.next_step = "GET_PHONE_NUMBER"
                job.save()
            elif message["text"] == "no_obligations":
                if job.action == "1":
                    year_of_filing = message['expected_filing_period'].split("/")[-1]
                    response = {
                        "message": [f"Great,I have verified that you have no witholding tax obligations for {year_of_filing}.<br><br>"\
                                    f"You are expected to file your taxes of the year {year_of_filing}.<br><br> "\
                                    f"Kindly upload the pdf version of your P9 form, for the year {year_of_filing}"],
                        "has_table": False,
                        "keyboard_type": "upload"
                    }
                    job.next_step = "UPLOAD_P9_FORM"
                    job.save()

                elif job.action == "2":
                    response = {"message": ["To file nil returns, kindly input your valid phone number to pay KES 100.00 to proceed."],
                                "has_table": False,
                                "keyboard_type": "normal"}
                    job.next_step = "GET_PHONE_NUMBER"
                    job.save()
            elif message["text"] == "has_obligations":
                response = {
                    "message": ["It looks like you have some tax obligations. Redirecting you to our live human agent. <br>Kindly upload the following documents:<br>" + "<br>1.) Witholding tax certificate(s) form <br>2.) Any other relevant document"],
                    "has_table": False,
                    "keyboard_type": "multi_upload"
                }
                job.next_step = "UPLOAD_COMPLEX_SCENARIO_DOCUMENTS"
                job.is_manual = True
                job.expected_payment_amount = 1500
                job.save()
            elif message["text"] == "already_filed":
                response = {
                    "message": [ "You have Already filed your taxes."],
                    "has_table": False,
                    "keyboard_type": None
                }
                job.next_step = "ALREADY_FILED"
                job.save()


        elif job.next_step == "GET_PHONE_NUMBER":
            #push stk push
            amount = job.expected_payment_amount
            msidn = "0"+message["text"][-9:]

            initiate_stkpush(amount=amount,
                                         msisdn=msidn,
                                         reference = f"{job.channel_id}")

            response = {
                "message": ["Once paid, press continue to proceed.","If you dont receive an stk push, press resend STKpush button."],
                "has_table": False,
                "keyboard_type": "buttons",
                "buttons": [
                    {"id": "continue_button", "label": "Continue"},
                    {"id": "resend_stk_push", "label": "Resend STK push"}
                ]}
            job.next_step = "CONFIRM_PAYMENT"
            job.phone_number = msidn
            job.save()

        elif job.next_step == "UPLOAD_P9_FORM":
            response = {
                "message": ["Extracting P9 tax information, do not interrupt"],
                "has_table": False,
                "keyboard_type": None}

            directory = os.getenv("UPLOADED_DOCUMENT_PATH").format(message["id"])
            print(directory)
            if not os.path.exists(directory):
                os.makedirs(directory)

            #save document
            file_path = os.path.join(directory, "p9_file.pdf")
            with open(file_path, 'wb') as f:
                f.write(file)

            job.next_step = "DISPLAY_EXTRACTED_DATA"
            job.p9_file_path = file_path
            job.save()

            itax.delay(operation="extract_p9_document_info",channel=channel, channel_id=message["id"])

        elif job.next_step == "DISPLAY_EXTRACTED_DATA":

            print(message)

            extracted_data = message["extracted_data"]
            standard_data = message["standard_data"]


            response = {"message": ["Kindly confirm if the data extracted from provided document is correct.<br> if not, please update accordingly and validate."],
                         "has_table": True,
                         "table_type": "validator",
                         "table_id": "p9_data_verifier",
                         "data": [{"id": key, "label": key.replace("_"," "),"value":standard_data[key]  } for key in standard_data],
                         "keyboard_type": "buttons",
                         "buttons": [{"id": "validate", "label": "Validate"}]}

            job.next_step = "VALIDATE_P9_DATA"
            job.tax_document_extracted_info = extracted_data
            job.pension_contributions = standard_data['Pension_contributions_column_E2']
            job.nhif_contributions = standard_data['NHIF_contributions_column_K2_insurance_relief']
            job.save()

        elif job.next_step == "VALIDATE_P9_DATA":
            print(message)

            response = {
                "message": [ "To proceed and file your taxes, kindly input your valid phone number to pay KES 200.00 to proceed."],
                "has_table": False,
                "keyboard_type": "normal"}

            job.pension_contributions = message["data"]["Pension_contributions_column_E2"]
            job.nhif_contributions = message["data"]["NHIF_contributions_column_K2_insurance_relief"]
            job.next_step ="GET_PHONE_NUMBER"
            job.expected_payment_amount = 200
            job.save()

        elif job.next_step == "UPLOAD_COMPLEX_SCENARIO_DOCUMENTS":

            directory = os.getenv("UPLOADED_DOCUMENT_PATH").format(message["id"])
            print(directory)
            if not os.path.exists(directory):
                os.makedirs(directory)

            # save document
            file_path = os.path.join(directory, message["file_name"])
            with open(file_path, 'wb') as f:
                f.write(file)


            if message["is_last_doc"]:
                response = {"message": ["Document uploaded sucessfully<br><br>"\
                                        "Redirecting you to our live human agent<br><br>" \
                                        "To proceed, kindly input your valid phone number to pay KES 1500.00 to proceed."],
                            "has_table": False,
                            "keyboard_type": "normal"}

                job.next_step = "GET_PHONE_NUMBER"
                job.save()
            else:
                response = {"message": ["Document uploaded sucessfully"],
                            "has_table": False,
                            "keyboard_type": None}

        elif job.next_step == "CONFIRM_PAYMENT":
            option_choosen =  message["text"]
            if option_choosen == "continue_button":
                #check if paid
                #if True:
                if job.expected_payment_amount == job.mpesa_paid_amount:
                    response = {
                        "message": ["Tax filing in progress, do not interrupt"],
                        "has_table": False,
                        "keyboard_type": None}
                    if job.is_manual:
                        response["message"] = ["Once our human agent is done, we will send an email confirming your tax filing status.",]
                    else:
                        if job.action == "1":
                            itax.delay(operation="file_p9_tax",channel=channel,channel_id=message["id"])
                        elif job.action == "2":
                            itax.delay(operation="file_nil_returns",channel=channel,channel_id=message["id"])

                        job.next_step = "FILING"
                        job.save()
                else:
                    response = {
                        "message": ["Sorry, we haven't received your payment yet, kindly retry.",
                                    "If you dont receive an stk push, press resend STKpush button."],
                        "has_table": False,
                        "keyboard_type": "buttons",
                        "buttons": [
                            {"id": "continue_button", "label": "Continue"},
                            {"id": "resend_stk_push", "label": "Resend STK push"}
                        ]}
            elif option_choosen == "resend_stk_push":
                amount = job.expected_payment_amount
                msidn = job.phone_number

                initiate_stkpush(amount=amount,
                                 msisdn=msidn,
                                 reference=f"{job.channel_id}")

                response = {
                    "message": ["STK push retriggered, press continue to proceed.",
                                "If you dont receive an stk push, press resend STKpush button."],
                    "has_table": False,
                    "keyboard_type": "buttons",
                    "buttons": [
                        {"id": "continue_button", "label": "Continue"},
                        {"id": "resend_stk_push", "label": "Resend STK push"}
                    ]}

        elif job.next_step == "FILING":
            if "error" in message:
                if message["error"] == True:
                    response = {"message": ["Due to the high traffic on the KRA website we have batched your filing and it should complete in the next 1 hour."],
                                "has_table": False,
                                "keyboard_type": None}
                else:
                    response = {"message": [message["text"]],
                                "has_table": False,
                                "keyboard_type": None}


    print("="*30)
    print(message)
    print(job.id)
    print("="*30)
    return response
