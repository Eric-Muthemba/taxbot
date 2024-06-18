#import win32com.client
from openpyxl import load_workbook
import os
from database import database
import configparser
import win32com
import win32com.client 

db = database()


class Excel():
    
    def _get_parameters(self,channel_id):
        # definition of the object used to read the config file
        configfile = configparser.ConfigParser()
        configfile.read("./config.ini")

        params = configfile["system"]
        self.BASE_PATH = params["BASE_PATH"]
        self.TEMPLATE_FILE = params["TEMPLATE_FILE"]
        self.GENERATED_DOCUMENT_FOLDER = params["GENERATED_DOCUMENT_FOLDER"].replace("channel_id",channel_id)
        
    def __init__(self, saving_name,channel_id=None):
        self._get_parameters(channel_id)
        self.template_file_path = self.BASE_PATH+self.TEMPLATE_FILE
        self.saving_path =  self.BASE_PATH+self.GENERATED_DOCUMENT_FOLDER + f'{saving_name}.xlsm'
        self.channel_id = saving_name
    def update_cells(self,P9_data=None,):
        self.P9_data = P9_data
        db_response_object = db.read(self.channel_id)
        if len(db_response_object) > 0:
            start_filing_date = f"01/01/{db_response_object[0][12]}"
            end_filing_date = f"31/12/{db_response_object[0][12]}"
            nhif_no = db_response_object[0][15]
            employees_pin = db_response_object[0][5]

            workbook_updates = [
                {"worksheet": "F_Employment_Income",
                 "cell_updates": [
                     {"cell_id": "A3", "value": self.P9_data["standard_data"]["employers_pin"]},
                     {"cell_id": "B3", "value": self.P9_data["standard_data"]["employers_name"]},
                     {"cell_id": "C3", "value": self.P9_data["totals"]["totals_A"]},
                     {"cell_id": "D3", "value": self.P9_data["totals"]["totals_B"]},
                     {"cell_id": "F3", "value": self.P9_data["totals"]["totals_C"]},
                     {"cell_id": "G3",
                      "value": self.P9_data["totals"]["totals_E3"] if self.P9_data["totals"]["totals_E3"] > 300000 else 0.00},
                     {"cell_id": "H6",
                      "value": sum(
                          [month_data["A"] for idx, month_data in enumerate(self.P9_data["data"]) if idx < 6])},
                     # jan to june income
                     {"cell_id": "H7",
                      "value": sum(
                          [month_data["E3"] for idx, month_data in enumerate(self.P9_data["data"]) if idx < 6]) if
                      self.P9_data["totals"]["totals_E3"] > 300000 else 0.00},  # jan to june pension
                     {"cell_id": "H8",
                      "value": sum(
                          [month_data["A"] for idx, month_data in enumerate(self.P9_data["data"]) if idx > 5])},
                     # july to Dec income
                     {"cell_id": "H9",
                      "value": sum(
                          [month_data["E3"] for idx, month_data in enumerate(self.P9_data["data"]) if idx > 5]) if
                      self.P9_data["totals"]["totals_E3"] > 300000 else 0.00},  # july to Dec pension
                 ]
                 },
                {"worksheet": "M_Details_of_PAYE_Deducted",
                 "cell_updates": [
                     {"cell_id": "A3", "value": self.P9_data["standard_data"]["employers_pin"]},
                     {"cell_id": "B3", "value": self.P9_data["standard_data"]["employers_name"]},
                     {"cell_id": "C3", "value": self.P9_data["totals"]["totals_H"]},  # chargable pay
                     {"cell_id": "D3", "value": self.P9_data["totals"]["totals_J"]},  # tax charged
                     {"cell_id": "E3", "value": self.P9_data["totals"]["totals_L"]},  # paye
                 ]
                 },
                {"worksheet": "A_Basic_Info",
                 "cell_updates": [
                     {"cell_id": "B3", "value": employees_pin},
                     {"cell_id": "B4", "value": "Original"},
                     {"cell_id": "B5", "value": start_filing_date},
                     {"cell_id": "B6", "value": end_filing_date},
                     {"cell_id": "B13", "value": "Yes"},
                 ]
                 },
                {"worksheet": "L_Computation_of_Insu_Relief",
                 "cell_updates": [
                     {"cell_id": "A3", "value": "P051099232D"},
                     {"cell_id": "B3", "value": "National Hospital Insurance Fund"},
                     {"cell_id": "C3", "value": "Health"},
                     {"cell_id": "E3", "value": "Self"},
                     {"cell_id": "D3", "value": nhif_no},
                     {"cell_id": "G3", "value": start_filing_date},  # pick from date
                     {"cell_id": "H3", "value": end_filing_date},
                     {"cell_id": "I3", "value": self.P9_data["totals"]["totals_insurance_relief-K"] / 0.15},
                     {"cell_id": "J3", "value": self.P9_data["totals"]["totals_insurance_relief-K"] / 0.15},
                 ]
                 },
                {"worksheet": "T_Tax_Computation",
                 "cell_updates": [
                     {"cell_id": "C5", "value": self.P9_data["totals"]["totals_E2"]},
                     {"cell_id": "C18", "value": self.P9_data["totals"]["totals_personal_relief_K"]},
                 ]
                 }
            ]

        workbook = load_workbook(self.template_file_path, read_only=False, keep_vba=True)
        for workbook_update in workbook_updates:
            sheet = workbook[workbook_update['worksheet']]
            for cell_update in workbook_update["cell_updates"]:
                sheet[cell_update["cell_id"]] = cell_update["value"]

        # Save changes
        workbook.save(self.saving_path)

    def get_tax_refund_value(self):
        xl = win32com.client.DispatchEx("Excel.Application")
        # Open the Excel workbook
        xl.Visible = False
        xl.DisplayAlerts = False
        xl.AskToUpdateLinks = False
        wb = xl.Workbooks.Open(self.saving_path, ReadOnly=True)
        worksheet = wb.Worksheets("T_Tax_Computation")
        cell_value = worksheet.Range("C31").Value
        print("Value of cell C31:", cell_value)
        wb.Close(SaveChanges=False)
        xl.Quit()
        return cell_value

    def generate_upload_file(self):
        xl = win32com.client.DispatchEx("Excel.Application")
        xl.Visible = False
        xl.DisplayAlerts = False
        xl.AskToUpdateLinks = False
        wb = xl.Workbooks.Open(self.saving_path, ReadOnly=True)
        wb.Application.Run("createErrorSheet")
        wb.Close(SaveChanges=False)
        xl.Quit()



