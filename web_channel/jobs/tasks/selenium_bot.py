from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from .textextract import extract_text_from_image
from PIL import Image
import string
import io
import os
from time import sleep


import chromedriver_autoinstaller

#chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists


# and if it doesn't exist, download it automatically,


class Itax(object):
    def __init__(self,task_id,itax_pin, itax_password,filing_date_from):


        self.itax_website_url = "https://itax.kra.go.ke/KRA-Portal/"
        self.pin_input_xpath = "//*[@id=\"logid\"]"
        self.password_input_xpath = "//*[@id=\"xxZTT9p2wQ\"]"
        self.continue_button_xpath = "//*[@id=\"normalDiv\"]/table/tbody/tr[3]/td[2]/a"
        self.login_error_xpath = '/html/body/div[3]/div[3]/table/tbody/tr/td/div/form/table/tbody/tr[1]/td[1]/table/tbody/tr[3]/td/div[2]/table[1]/tbody/tr/td'


        self.captcha_image_xpath = "//*[@id=\"captcha_img\"]"
        self.captcha_input_xpath = "//*[@id=\"captcahText\"]"
        self.login_button_xpath = "//*[@id=\"loginButton\"]"
        self.main_returns_page_button_xpath = "//*[@id=\"ddtopmenubar\"]/ul/li[3]/a"
        self.sub_returns_page_button_xpath = "//*[@id=\"Returns\"]/li[1]/a"

        self.main_certificate_page_button_xpath = "//*[@id=\"ddtopmenubar\"]/ul/li[8]/a"
        self.sub_certificate_page_button_xpath = "//*[@id=\"Certificates\"]/li[1]/a"

        self.sub_nil_returns_page_button_xpath = "//*[@id=\"Returns\"]/li[4]/a"
        self.type_of_tax_obligation_button_xpath = "//*[@id=\"regType\"]"
        self.navigate_to_final_page_button_xpath = "//*[@id=\"btnSubmit\"]"


        self.submit_nil_returns_button_xpath = '//*[@id="sbmt_btn"]'
        self.type_of_tax_return_xpath = "//*[@id=\"cmbReturnType\"]"
        self.agree_to_terms_and_conditions_checkbox_xpath = "//*[@id=\"chkTermsAndCond\"]"
        self.tax_return_period_from_xpath = "//*[@id=\"txtPeriodFrom\"]"
        self.tax_return_period_to_xpath = "//*[@id=\"txtPeriodTo\"]"

        self.certificates_page_button_xpath = "/html/body/div[2]/div[2]/div/table/tbody/tr/td/form/div/ul/li[8]/a"

        self.upload_tax_return_input_xpath = "//*[@id=\"file\"]"
        self.invalid_credentials_xpath = "/html/body/div[3]/div[3]/table/tbody/tr/td/div/form/table/tbody/tr[1]/td[1]/table/tbody/tr[3]/td/div[3]/table[1]/tbody/tr/td/font"
        self.wrong_arithmetic_xpath = '/html/body/div[3]/div[3]/table/tbody/tr/td/div/form/table/tbody/tr[1]/td[1]/table/tbody/tr[3]/td/div[2]/table[1]/tbody/tr/td'
        self.success_text = '//*[@id="PINReceipt"]/div[2]/center/div/table/tbody/tr[2]/td'
        self.download_confirmation = '//*[@id="PINReceipt"]/div[2]/center/div/table/tbody/tr[3]/td/a' #        '''	Return Submitted successfully with Acknowledgement Number: KRA202445300049 '''
        self.itr_employment_xpath = "/html/body/ul[2]/li[5]/a"
        self.itr_page_returns_date_xpath = '//*[@id="txtPeriodFromITR"]'
        self.itr_page_returns_end_date_xpath = '//*[@id="txtPeriodToITR"]'
        self.itr_page_returns_have_employment_radio_button_xpath = '/html/body/div[2]/div[4]/table/tbody/tr/td/div/form/div[3]/center/div/table/tbody/tr[7]/td[2]/input[1]'

        #######################################file tax##################################
        self.drop_down_yes_value = "Yes"
        self.drop_down_no_value = "No"

        #section A
        self.itr_name_of_taxpayer_xpath = '//*[@id="txPayerName"]'
        self.have_life_insurance_xpath = '//*[@id="hvPolicy"]'
        self.has_employer_provided_you_with_a_car_xpath = '//*[@id="hvCarFlag"]'
        self.have_a_mortgage_xpath = '//*[@id="hvMortgage"]'
        self.have_income_from_another_country_xpath = '//*[@id="hvFrnInc"]'
        self.have_disability_certificate_xpath = '//*[@id="hvEC"]'
        self.itr_bank_name_select_xpath = '//*[@id="lngBankId"]'
        #section L
        self.section_l_xpath = '//*[@id="etrSecL"]'
        self.insurance_company_pin_xpath = '//*[@id="in_empIncomeInsRelfDtl_3"]'
        self.type_of_policy_dropdown_xpath = '//*[@id="in_empIncomeInsRelfDtl_5"]'
        self.type_of_policy_dropdown_nhif_value = 'LIFE'
        self.policy_number_input_xpath = '//*[@id="in_empIncomeInsRelfDtl_6"]'
        self.type_of_holder_xpath ='//*[@id="in_empIncomeInsRelfDtl_7"]'
        self.type_of_holder_value ='S'
        self.commencement_date_input_xpath = '//*[@id="in_empIncomeInsRelfDtl_9"]'
        self.maturity_date_input_xpath = '//*[@id="in_empIncomeInsRelfDtl_10"]'
        self.sum_assured_input_xpath = '//*[@id="in_empIncomeInsRelfDtl_11"]'
        self.annual_premiums_paid_xpath = '//*[@id="in_empIncomeInsRelfDtl_12"]'

        #section T
        self.section_t_xpath = '//*[@id="etrSecT"]'
        self.pension_contributions_input_xpath = '//*[@id="dblPensionContribution"]'

        #################################################################################




        self.nhif_pin = "P051099232D"

        self.screenshot_path = os.getenv("SCREENSHOT_PATH").format(task_id)
        self.captcha_file = os.getenv("CAPTURE_FILE_LOCATION").format(task_id)
        self.itax_pin = itax_pin
        self.itax_password = itax_password
        self.wrong_password = False
        self.error_detected = False
        self.error_text = ""
        self.has_obligations = False
        self.invalid_pin = False
        self.is_blocked = False

        self.filing_date = filing_date_from

        self.type_of_tax_obligation_select_options = [{"name": "Income Tax - Resident Individual", "value": "2"},
                                                      {"name": "Income Tax Non-Resident Individual", "value": "3"}]

        self.type_of_tax_return_options = [{"name": "Original", "value": "Original"},
                                           {"name": "Amended", "value": "Amended"}]

        self.selected_type_of_tax_obligation_options = "2"
        self.selected_type_of_tax_return_options = "Original"


        options = Options()
        # options.add_argument("start-maximized")
        options.binary_location = "/usr/local/bin/"
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--remote-debugging-pipe')
        options.add_argument("--headless=new")
        try:
            self.driver = webdriver.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, 10)
        except Exception as e:
            sleep(5)
            Itax(task_id,itax_pin, itax_password)

    def captcha_solver(self):
        captcha_image = self.wait.until(EC.visibility_of_element_located((By.XPATH, self.captcha_image_xpath)))
        location = captcha_image.location
        size = captcha_image.size
        screenshot = self.driver.get_screenshot_as_png()
        image = Image.open(io.BytesIO(screenshot))

        location = {"x": 400, "y": 700}
        location = {"x": 600, "y": 700}
        size = {"width": 200, "height": 100}
        
        # Define the coordinates for cropping
        left = location['x']
        top = location['y']
        right = location['x'] + size['width']
        bottom = location['y'] + size['height']

        # Crop the image to the element's area
        cropped_image = image.crop((left, top, right, bottom))
        cropped_image.save(self.captcha_file)  # Save the image to a file
        
        acceptable_characters = string.digits + "-+*/"
        extracted_text = extract_text_from_image(self.captcha_file)
        result = "".join(list(filter(lambda c: c in acceptable_characters, extracted_text)))
        if result[-1] in ["-","+"]:
            result = result[:-1]

        print("="*30)
        print(result)
        try:
            print(eval(result))
            return eval(result)
        except:
            self.captcha_solver()


    def take_screenshot(self):
        screenshot = self.driver.get_screenshot_as_png()
        image = Image.open(io.BytesIO(screenshot))
        print(self.screenshot_path)
        image.save(self.screenshot_path)  # Save the image to a file

    def load_itax_website(self):
        self.driver.get(self.itax_website_url)

    def login_to_itax_website(self):
        
        itax_pin_input = self.wait.until(EC.visibility_of_element_located((By.XPATH, self.pin_input_xpath)))
        itax_pin_input.send_keys(self.itax_pin)
        continue_button = self.wait.until(EC.visibility_of_element_located((By.XPATH, self.continue_button_xpath)))
        continue_button.click()


        try:
            alert = self.driver.switch_to.alert
            alert.accept()
            self.invalid_pin = True
        except:
                itax_password_input = self.wait.until(EC.visibility_of_element_located((By.XPATH, self.password_input_xpath)))
                itax_password_input.send_keys(self.itax_password)

                result = self.captcha_solver()

                captcha = self.wait.until(EC.visibility_of_element_located((By.XPATH, self.captcha_input_xpath)))
                captcha.send_keys(result)

                login_button = self.wait.until(EC.visibility_of_element_located((By.XPATH, self.login_button_xpath)))
                login_button.click()

                try:
                    error_box =self.wait.until(EC.visibility_of_element_located((By.XPATH, self.invalid_credentials_xpath)))
                    self.wrong_password = True
                    self.error_text = error_box.text
                except:
                    try:
                        #wrong arithmetic
                        error_box = self.wait.until(element_located((By.XPATH, self.wrong_arithmetic_xpath)))
                        print(error_box)
                        sleep(5)

                        self.login_to_itax_website()
                    except Exception as e:
                        pass


    def navigate_to_file_nil_tax_page(self,number_of_recursion=0):
        try:
            main_returns_page_button = self.wait.until(
                EC.visibility_of_element_located((By.XPATH, self.main_returns_page_button_xpath)))
            hover = ActionChains(self.driver).move_to_element(main_returns_page_button)
            hover.perform()

            sub_nil_returns_page_button = self.wait.until(
                EC.visibility_of_element_located((By.XPATH, self.sub_nil_returns_page_button_xpath)))
            sub_nil_returns_page_button.click()

            type_of_tax_obligation = self.wait.until(
                EC.visibility_of_element_located((By.XPATH, self.type_of_tax_obligation_button_xpath)))
            select = Select(type_of_tax_obligation)
            select.select_by_value(self.selected_type_of_tax_obligation_options)

            navigate_to_final_page_button = self.wait.until(
                EC.visibility_of_element_located((By.XPATH, self.navigate_to_final_page_button_xpath)))
            navigate_to_final_page_button.click()

            submit_nil_returns_button = self.wait.until(
                EC.visibility_of_element_located((By.XPATH, self.submit_nil_returns_button_xpath)))
            submit_nil_returns_button.click()
            self.take_screenshot()
        except Exception as e:
            print(e)
            if number_of_recursion < 3:
                sleep(5)
                self.navigate_to_file_nil_tax_page(number_of_recursion= number_of_recursion+1)
            else:
                self.error_detected = True

    def get_obligations_and_date_to_file(self):

        #get date
        main_returns_page_button = self.wait.until(EC.visibility_of_element_located((By.XPATH, self.main_returns_page_button_xpath)))
        hover = ActionChains(self.driver).move_to_element(main_returns_page_button)
        hover.perform()

        sub_returns_page_button = self.wait.until(EC.visibility_of_element_located((By.XPATH, self.sub_returns_page_button_xpath)))
        sub_returns_page_button.click()

        type_of_tax_obligation = self.wait.until(EC.visibility_of_element_located((By.XPATH, self.type_of_tax_obligation_button_xpath)))
        select = Select(type_of_tax_obligation)
        select.select_by_value(self.selected_type_of_tax_obligation_options)

        navigate_to_final_page_button = self.wait.until(EC.visibility_of_element_located((By.XPATH, self.navigate_to_final_page_button_xpath)))
        navigate_to_final_page_button.click()

        try:
            alert = self.driver.switch_to.alert
            print("found alert")
            print(f"Alert text: {alert.text}")
            alert.accept()

            if "You have already filed the Original Return" in alert.text:
                self.has_obligations = False
            else:
                self.has_obligations = True
        except Exception as e:
            print("Alert not found")

        tax_return_period_from = self.wait.until( EC.visibility_of_element_located((By.XPATH, self.tax_return_period_from_xpath))).get_attribute('value')
        self.filing_date = tax_return_period_from

        if self.filing_date.strip() == "":
            tax_return_period_from = "01/01/2023"
            self.filing_date = tax_return_period_from


        # check if obligations
        main_returns_page_button = self.wait.until(
            EC.visibility_of_element_located((By.XPATH, self.main_returns_page_button_xpath)))
        hover = ActionChains(self.driver).move_to_element(main_returns_page_button)
        hover.perform()

        sub_returns_page_button = self.wait.until(
            EC.visibility_of_element_located((By.XPATH, self.itr_employment_xpath)))
        sub_returns_page_button.click()

        try:
            itr_page_returns_date_input = self.wait.until( EC.visibility_of_element_located((By.XPATH, self.itr_page_returns_date_xpath)))
            itr_page_returns_date_input.send_keys(tax_return_period_from)
        except Exception as e:
            print(self.filing_date)


            self.driver.execute_script(f"""
                                            var el =document.getElementById('txtPeriodFromITR');
                                            el.value = '{self.filing_date}';
                                            el.dispatchEvent(new Event("change"));
                                       """)

        itr_page_returns_end_date = self.wait.until(
            EC.visibility_of_element_located((By.XPATH, self.itr_page_returns_end_date_xpath)))
        itr_page_returns_end_date.click()
        sleep(3)


        itr_page_returns_have_employment_radio_button = self.wait.until(
            EC.visibility_of_element_located((By.XPATH, self.itr_page_returns_have_employment_radio_button_xpath)))
        itr_page_returns_have_employment_radio_button.click()
        self.driver.execute_script("document.getElementById('btnSubmitITR').disabled = false;")
        sleep(3)
        self.driver.execute_script("document.getElementById('btnSubmitITR').click();")
        sleep(3)
        try:
            alert = self.driver.switch_to.alert
            print("found alert")
            # Print alert text (optional)
            print(f"Alert text: {alert.text}")
            alert.accept()

            if "You have already filed the Original Return" in alert.text:
                self.has_obligations = False
            else:
                self.has_obligations = True
        except Exception as e:
            print("Alert not found")




        return {"tax_return_period_from":tax_return_period_from,
                "has_obligations":self.has_obligations}



    def navigate_to_filing_tax_page(self,number_of_recursion=0):
        main_returns_page_button = self.wait.until(EC.visibility_of_element_located((By.XPATH, self.main_returns_page_button_xpath)))
        hover = ActionChains(self.driver).move_to_element(main_returns_page_button)
        hover.perform()

        sub_returns_page_button = self.wait.until(EC.visibility_of_element_located((By.XPATH, self.itr_employment_xpath)))
        sub_returns_page_button.click()

        itr_page_returns_date_input = self.wait.until(EC.visibility_of_element_located((By.XPATH, self.itr_page_returns_date_xpath)))
        itr_page_returns_date_input.send_keys(self.filing_date)
        sleep(10)

        itr_page_returns_end_date = self.wait.until(EC.visibility_of_element_located((By.XPATH, self.itr_page_returns_end_date_xpath)))
        itr_page_returns_end_date.click()
        self.end_date = itr_page_returns_end_date.get_attribute('value')


        itr_page_returns_have_employment_radio_button = self.wait.until(EC.visibility_of_element_located((By.XPATH, self.itr_page_returns_have_employment_radio_button_xpath)))
        itr_page_returns_have_employment_radio_button.click()
        self.driver.execute_script("document.getElementById('btnSubmitITR').disabled = false;")
        sleep(10)
        self.driver.execute_script("document.getElementById('btnSubmitITR').click();")
        sleep(10)

        try:
            alert = self.driver.switch_to.alert
            print("found alert")
            # Print alert text (optional)
            print(f"Alert text: {alert.text}")
            alert.accept()
            if "You have already filed the Original Return" in alert.text:
                self.has_obligations = False
            else:
                self.has_obligations = True
        except Exception as e:
            has_error = False

            '''try:
                self.driver.page_source.find("Error")
                has_error = True
            except:
                has_error = False'''
            print(has_error)
            #save to batch process
            if has_error:
                if number_of_recursion < 3:
                    sleep(5)
                    self.navigate_to_filing_tax_page(number_of_recursion= number_of_recursion+1)
                else:
                    self.error_detected = True

        self.take_screenshot()

    def file_itr_tax(self,pension_contributions,tax_payer_nhif_pin,nhif_contributions):
        print("="*30)
        # section A
        self.tax_payer_name = self.wait.until( EC.visibility_of_element_located((By.XPATH, self.itr_name_of_taxpayer_xpath))).get_attribute('value')

        life_insurance_input = self.wait.until(EC.visibility_of_element_located((By.XPATH, self.have_life_insurance_xpath)))
        select = Select(life_insurance_input)
        select.select_by_value(self.drop_down_yes_value)

        employer_provided_you_with_a_car_input = self.wait.until(EC.visibility_of_element_located((By.XPATH, self.has_employer_provided_you_with_a_car_xpath)))
        select = Select(employer_provided_you_with_a_car_input)
        select.select_by_value(self.drop_down_no_value)

        have_mortgage_input = self.wait.until(EC.visibility_of_element_located((By.XPATH, self.have_a_mortgage_xpath)))
        select = Select(have_mortgage_input)
        select.select_by_value(self.drop_down_no_value)

        have_income_from_another_country_input = self.wait.until(EC.visibility_of_element_located((By.XPATH, self.have_income_from_another_country_xpath)))
        select = Select(have_income_from_another_country_input)
        select.select_by_value(self.drop_down_no_value)

        have_disability_certificate_input = self.wait.until(EC.visibility_of_element_located((By.XPATH, self.have_disability_certificate_xpath)))
        select = Select(have_disability_certificate_input)
        select.select_by_value(self.drop_down_no_value)

        sleep(10)

        # section L
        section_l = self.wait.until(EC.visibility_of_element_located((By.XPATH, self.section_l_xpath)))
        section_l.click()

        insurance_company_pin_input = self.wait.until(EC.visibility_of_element_located((By.XPATH, self.insurance_company_pin_xpath)))
        insurance_company_pin_input.clear()
        insurance_company_pin_input.send_keys(self.nhif_pin)

        type_of_policy_dropdown = self.wait.until(EC.visibility_of_element_located((By.XPATH, self.type_of_policy_dropdown_xpath)))
        select = Select(type_of_policy_dropdown)
        select.select_by_value(self.type_of_policy_dropdown_nhif_value)
        try:
            policy_number_input = self.wait.until(EC.visibility_of_element_located((By.XPATH, self.policy_number_input_xpath)))
            policy_number_input.clear()
            policy_number_input.send_keys(tax_payer_nhif_pin)

            type_of_holder_dropdown = self.wait.until( EC.visibility_of_element_located((By.XPATH, self.type_of_holder_xpath)))
            select = Select(type_of_holder_dropdown)
            select.select_by_value(self.type_of_holder_value)
        except Exception as e:
            print(e)

        commencement_date_input = self.wait.until( EC.visibility_of_element_located((By.XPATH, self.commencement_date_input_xpath)))
        commencement_date_input.clear()
        commencement_date_input.send_keys(self.filing_date)


        maturity_date_input = self.wait.until(EC.visibility_of_element_located((By.XPATH, self.maturity_date_input_xpath)))
        maturity_date_input.clear()
        maturity_date_input.send_keys(self.end_date)


        sum_assured_input = self.wait.until(EC.visibility_of_element_located((By.XPATH, self.sum_assured_input_xpath)))
        sum_assured_input.clear()
        sum_assured_input.send_keys(nhif_contributions)


        annual_premiums_paid_input = self.wait.until(EC.visibility_of_element_located((By.XPATH, self.annual_premiums_paid_xpath)))
        annual_premiums_paid_input.clear()
        annual_premiums_paid_input.send_keys(nhif_contributions)

        # section T
        section_t = self.wait.until(EC.visibility_of_element_located((By.XPATH, self.section_t_xpath)))
        section_t.click()

        pension_contributions_input = self.wait.until(EC.visibility_of_element_located((By.XPATH, self.pension_contributions_input_xpath)))
        pension_contributions_input.clear()
        pension_contributions_input.send_keys(pension_contributions)

        sleep(100)
        self.take_screenshot()


