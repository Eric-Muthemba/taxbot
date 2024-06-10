import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
import base64

class Mpesa():
    def __init__(self):
        self.base_url = "https://sandbox.safaricom.co.ke"
        self.callback_url = ""
        self.consumer_key = "V7OAAV4ZaX8krZEMHAWI2obHGntGsgCSiP5xdNCc7MRILo4y"
        self.consumer_secret = "K2SpyhYEchBRdj1HmiBC87gAgpLNOCekZAGGbWQ8mkmEgTDGbDJJ3rbbMjuIwMoL"
        self.passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
        self.get_token()

    def get_token(self):
        response = requests.request("GET",
                                    f'{self.base_url}/oauth/v1/generate?grant_type=client_credentials',
                                    auth=HTTPBasicAuth(self.consumer_key, self.consumer_secret)).json()

        self.headers = {"Authorization": "Bearer "+response["access_token"]}


    def stk_push(self,ref_no,phone_no,amount):
        BusinessShortCode = 174379
        Timestamp =  datetime.now().strftime("%Y%m%d%H%M%S")
        Password = base64.b64encode(bytes(f"{BusinessShortCode}{self.passkey}{Timestamp}", 'utf-8')).decode("utf-8")

        payload = {
            "BusinessShortCode": BusinessShortCode,
            "Password": Password,
            "Timestamp": Timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA":  phone_no,
            "PartyB": BusinessShortCode,
            "PhoneNumber": phone_no,
            "CallBackURL": self.callback_url,
            "AccountReference": ref_no,
            "TransactionDesc": "Payment of for tax filing"
        }
        response = requests.request("POST",
                                    f'{self.base_url}/mpesa/stkpush/v1/processrequest',
                                    headers=self.headers,
                                    json=payload)

        print(response.text)

        if response.status_code == 404:
            self.get_token()
            self.stk_push(company_name=company_name,phone_no=phone_no,amount=amount)

        return

