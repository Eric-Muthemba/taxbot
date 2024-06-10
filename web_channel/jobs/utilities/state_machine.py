from jobs.models import Job
import json

def state_machine(channel,message,channel_id):
    print(message)
    if message == "":
        return { "message": "Invalid input."}

    jobs = Job.objects.filter(channel=channel, channel_id=channel_id, session_status="Active")
    if channel == "Web":
        if not jobs:
            return {"message": "No active job found"}
    else:
        if not jobs:
            Job.objects.create(channel=channel, channel_id=channel_id, session_status="Active")
            jobs = Job.objects.filter(channel=channel, channel_id=channel_id, session_status="Active")

    if message      == "cancelled":
        jobs.delete()
    elif message == "reset" or jobs[0].step == "START":
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
    elif jobs[0].step == "CHOOSE_PROCESS":
        response = {}

        if message == "1":
            response["message"] = "Which year do you want to file for?"
            jobs.update(step="GET_YEAR_TO_FILE")
        elif message == "2":
            response["message"] = "Kindly input your ticket number."
            jobs.update(step="PREVIOUS_STATUS")
        else:
            response["message"] = "Invalid input."
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
        response = {
            "message": "Kindly enter your KRA PIN"
        }
        try:
            jobs.update(year_of_filling=int(message), step="GET_KRA_PIN")
        except ValueError:
            response["message"] = "Invalid input.<br>Which year do you want to file for?"
    elif jobs[0].step == "GET_KRA_PIN":
        response = {
            "message": f"Were you employed or had any source of income in {jobs[0].year_of_filling}",
            "keyboard_type": "options",
        }

        if len(message) == 11:
            jobs.update(kra_pin=message, step="CHECK_IF_EMPLOYED_OR_HAD_INCOME")
        else:
            response["message"] = "Invalid KRA Pin entered.<br>Kindly enter your correct KRA PIN?"
    elif jobs[0].step == "CHECK_IF_EMPLOYED_OR_HAD_INCOME":
        response = {
            "message": "From 2023, KRA allows for tax relief from your NHIF contributions.\n Enter your NHIF Number ..."
        }
        jobs.update(step="GET_NHIF_NO")
    elif jobs[0].step == "GET_NHIF_NO":
        print("message")
        print(message)
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
                       f"12.) Did you want to declare your wife's income ?"
        }
    elif jobs[0].step == "UPLOAD_P9_FORM":
        response = {
            "keyboard_type": "upload_pdf",
            "message": "Kindly upload your P9 form"
        }
        jobs.update(step="VALIDATE_EXTRACTED_INFO")
    elif jobs[0].step == "VALIDATE_EXTRACTED_INFO":
        tax_document_extracted_info = json.loads(jobs[0].tax_document_extracted_info)
        response = {
            "keyboard_type": "validator",
            "message": "Kindly confirm if the following extracted information is correct",
            "data":[
                {"type":"label","value":"Employer details"},
                {"label": f"Employer name: {tax_document_extracted_info.employer_name}","value":1},
                {"label": f"Employer pin:  {tax_document_extracted_info.employer_name}", "value": 2},
                {"type": "label", "value": "Monthly Gross income details"},
                {"label": f"January gross: {tax_document_extracted_info.employer_name}", "value": 3},
                {"label": f"February gross: {tax_document_extracted_info.employer_name}", "value": 4},
                {"label": f"March gross: {tax_document_extracted_info.employer_name}", "value": 5},
                {"label": f"April gross: {tax_document_extracted_info.employer_name}", "value": 6},
                {"label": f"May gross: {tax_document_extracted_info.employer_name}", "value": 7},
                {"label": f"June gross: {tax_document_extracted_info.employer_name}", "value": 8},
                {"label": f"July gross: {tax_document_extracted_info.employer_name}", "value": 9},
                {"label": f"August gross: {tax_document_extracted_info.employer_name}", "value": 10},
                {"label": f"September gross: {tax_document_extracted_info.employer_name}", "value": 11},
                {"label": f"October gross: {tax_document_extracted_info.employer_name}", "value": 12},
                {"label": f"November gross: {tax_document_extracted_info.employer_name}", "value": 13},
                {"label": f"December gross: {tax_document_extracted_info.employer_name}", "value": 14},
                {"type": "label", "value": "Totals"},
                {"label": f"A Total: {tax_document_extracted_info.employer_name}", "value": 15},
                {"label": f"B Total: {tax_document_extracted_info.employer_name}", "value": 16},
                {"label": f"C Total: {tax_document_extracted_info.employer_name}", "value": 17},
                {"label": f"D Total: {tax_document_extracted_info.employer_name}", "value": 18},
                {"label": f"E Total: {tax_document_extracted_info.employer_name}", "value": 19},
                {"label": f"F Total: {tax_document_extracted_info.employer_name}", "value": 20},
                {"label": f"G Total: {tax_document_extracted_info.employer_name}", "value": 21},
                {"label": f"H Total: {tax_document_extracted_info.employer_name}", "value": 22},
                {"label": f"I Total: {tax_document_extracted_info.employer_name}", "value": 23},
                {"label": f"J Total: {tax_document_extracted_info.employer_name}", "value": 24},
                {"label": f"K Total: {tax_document_extracted_info.employer_name}", "value": 25},
                {"label": f"L Total: {tax_document_extracted_info.employer_name}", "value": 26},

            ]
        }
        jobs.update(step="CHOOSE_SERVICE")
    elif jobs[0].step == "CHOOSE_SERVICE":
        response = {
            "message": f"Select the services you want",
            "keyboard_type": "checkboxes",
            "data":[
                    {"label": f"1.) Generate filed tax return Excel","value":1},
                    {"label": f"2.) Generate filed tax return xml (final document to upload to itax portal)", "value": 2},
                    {"label": f"3.) Auto file your tax on the itax portal (includes 1 and 2)", "value": 3}
            ]
        }
        jobs.update(kra_password=message, step="CHECK_SERVICE_CHOOSEN")
    elif jobs[0].step == "CHECK_SERVICE_CHOOSEN":
        if message in [1,2]:
            response = {"message": f"To continue, Enter your phone number to pay KES 200.00"}
            jobs.update( step="REQUEST_PAYMENT")

        else:
            response = {"message": "Kindly enter your KRA password"}
            jobs.update(step="GET_KRA_PASSWORD")
    elif jobs[0].step == "GET_KRA_PASSWORD":
        response = {"message": f"To continue, Enter your phone number to pay KES 200.00"}
        jobs.update(kra_password=message, step="REQUEST_PAYMENT")
    elif jobs[0].step == "REQUEST_PAYMENT":
        if len(message) == 10:
            response = {"keyboard_type": "validate",
                        "message": "Once paid press PAID else CANCEL."}
        jobs.update(step="CHECK_IF_PAID")
    elif jobs[0].step == "CHECK_IF_PAID":
        # check mpesa
        paid = True
        if paid:
            response = {"message": "Filing. Kindly be patient."}
            jobs.update(step="GENERATING_TAX_DOCUMENT", payment_status="PAID")
        else:
            response = {"keyboard_type": "validate",
                        "message": "Not paid.<br>Kindly pay to proceed<br>Once paid press PAID else CANCEL."}
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

