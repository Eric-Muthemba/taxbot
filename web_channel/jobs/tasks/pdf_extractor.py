import pdfplumber


class pdf_extractor():
    def __init__(self,path):
        self.tests = {"employers_name":False,
                      "employers_pin":False,
                      "line_items":False,
                      "combined_relief_separated": True}
        self.response = {"standard_data": {"employers_name": "", "employers_pin": ""}, "data": [], "totals": {}}
        with pdfplumber.open(path) as pdf:
            page = pdf.pages[0]
            self.tables = page.extract_tables()
            self.lines = page.extract_text().split("\n")
        self.extract_employer_info()
        self.extract_table()
        self.standard_data = {"pension_contributions_column_E2":0.00,
                              "nhif_contributions":0.00 }
        self.validator()



    def extract_employer_info(self):
        for line in self.lines:
            line = line.replace(".", "").replace(",", "").replace("'", "")
            if "employers" in line.lower():
                line = line.upper()
                line = line.split("EMPLOYERS")
                try:
                    self.response["standard_data"]["employers_name"] = line[1].replace("NAME","").replace(":","").strip()
                    self.response["standard_data"]["employers_pin"] = line[2].replace("PIN","").strip()
                except:
                    pass

    def try_except(self,cell):
        try:
            return float(cell.replace(",", ""))
        except:
            return 0.00

    def extract_table(self):
        start = False
        totals = False
        relief_combined = False

        for table in self.tables:
            for idx,row in enumerate(table):
                try:
                    if row[0].lower() == "january":
                        start = True
                        if len(row) == 15:
                            if self.try_except(row[12]) == 0 or self.try_except(row[13]) == 0:
                                self.tests["combined_relief_separated"] = False

                        if len(row) == 14:
                            relief_combined = True

                    elif row[0].lower() == "totals":
                        totals = True
                    if start == True and totals == False:
                        data = {
                                "Month": row[0],
                                "A": self.try_except(row[1]),
                                "B": self.try_except(row[2]),
                                "C": self.try_except(row[3]),
                                "D": self.try_except(row[4]),
                                "E1": self.try_except(row[5]),
                                "E2": self.try_except(row[6]),
                                "E3": self.try_except(row[7]),
                                "F": self.try_except(row[8]),
                                "G": self.try_except(row[9]),
                                "H": self.try_except(row[10]),
                                "J": self.try_except(row[11])
                               }
                        if relief_combined:
                            data = {**data, **{"personal_relief_K": 2400,
                                               "insurance_relief-K": self.try_except(row[12])-2400,
                                               "L": self.try_except(row[13])}
                                    }

                        else:
                            data = {**data,**{"personal_relief_K": self.try_except(row[12]),
                                              "insurance_relief-K": self.try_except(row[13]),
                                              "L": self.try_except(row[14])}
                                    }

                        self.response["data"].append(data)

                except Exception as e:
                    pass
        sums = {}
        for row in self.response["data"]:
            for key, value in row.items():
                if key == "Month":
                    continue
                if "totals_" + key in sums:
                    sums["totals_" + key] += value
                else:
                    sums["totals_" + key] = value
                sums["totals_" + key] = round(sums["totals_" + key], 2)
        self.response["totals"] = sums

        if relief_combined and (self.response["totals"]["totals_insurance_relief-K"] < 0 or self.response["totals"]["totals_personal_relief_K"] < 0):
            self.tests["combined_relief_separated"] = False

    def validator(self):
        print(self.response["totals"])
        try:
            self.standard_data["pension_contributions_column_E2"] = self.response["totals"]["totals_E2"]
        except:
            pass
        try:
            self.standard_data["NHIF_contributions_column_K2_insurance_relief"] = self.response["totals"]["totals_insurance_relief-K"]
        except:
            pass

        #check if employers_name and pin were extracted
        if self.response["standard_data"]["employers_name"] != "":
            self.tests["employers_name"] = True
        if self.response["standard_data"]["employers_pin"] != "":
            self.tests["employers_pin"] = True
        if len(self.response["data"]) != 0:
            self.tests["line_items"] = True




        return self.tests




