from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium import webdriver
from PIL import Image
import string
import io
import os
import cv2
from time import sleep
from textextract import extract_text_from_image

class Itax(object):
    def __init__(self, file_nil, channel_id,itax_pin, itax_password, doc_to_be_uploaded=None, screenshot_path=None):
        print(doc_to_be_uploaded)
        self.itax_website_url = "https://itax.kra.go.ke/KRA-Portal/"
        
        self.pin_input_xpath = "//*[@id=\"logid\"]"
        self.password_input_xpath = "//*[@id=\"xxZTT9p2wQ\"]"
        self.continue_button_xpath = "//*[@id=\"normalDiv\"]/table/tbody/tr[3]/td[2]/a"
        self.captcha_image_xpath = "//*[@id=\"captcha_img\"]"
        self.captcha_input_xpath = "//*[@id=\"captcahText\"]"
        self.login_button_xpath = "//*[@id=\"loginButton\"]"
        self.main_returns_page_button_xpath = "//*[@id=\"ddtopmenubar\"]/ul/li[3]/a"
        self.sub_returns_page_button_xpath = "//*[@id=\"Returns\"]/li[1]/a"
        self.sub_nil_returns_page_button_xpath = "//*[@id=\"Returns\"]/li[4]/a"
        self.type_of_tax_obligation_button_xpath = "//*[@id=\"regType\"]"
        self.navigate_to_final_page_button_xpath = "//*[@id=\"btnSubmit\"]"
        self.type_of_tax_return_xpath = "//*[@id=\"cmbReturnType\"]"
        self.agree_to_terms_and_conditions_checkbox_xpath = "//*[@id=\"chkTermsAndCond\"]"
        self.tax_return_period_from_xpath = "//*[@id=\"txtPeriodFrom\"]"
        self.tax_return_period_to_xpath = "//*[@id=\"txtPeriodTo\"]"
        self.upload_tax_return_input_xpath = "//*[@id=\"file\"]"
        self.invalid_credentials_xpath = "/html/body/div[3]/div[3]/table/tbody/tr/td/div/form/table/tbody/tr[1]/td[1]/table/tbody/tr[3]/td/div[3]/table[1]/tbody/tr/td/font"
        self.wrong_password = False
        self.captcha_file = f"C:\\taxbot\\web_channel\\media\\uploads\\{channel_id}\\capture_image.png"
        
        self.success_text = '//*[@id="PINReceipt"]/div[2]/center/div/table/tbody/tr[2]/td'
        '''	Return Submitted successfully with Acknowledgement Number: KRA202445300049 '''
        self.download_confirmation = '//*[@id="PINReceipt"]/div[2]/center/div/table/tbody/tr[3]/td/a'
        
        self.screenshot_path = screenshot_path
        self.itax_pin = itax_pin
        self.itax_password = itax_password

        self.type_of_tax_obligation_select_options = [{"name": "Income Tax - Resident Individual", "value": "2"},
                                                      {"name": "Income Tax Non-Resident Individual", "value": "3"}]
        self.type_of_tax_return_options = [{"name": "Original", "value": "Original"},
                                           {"name": "Amended", "value": "Amended"}]

        self.selected_type_of_tax_obligation_options = "2"
        self.selected_type_of_tax_return_options = "Original"

        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)
        self.zipfile_location = doc_to_be_uploaded

        try:
            self.load_itax_website()
            self.login_to_itax_website()

            if not self.wrong_password:
                if file_nil:
                    self.navigate_to_file_nil_tax_page()
                else:
                    self.navigate_to_filing_tax_page()
                    self.upload_and_submit_tax_returns()

                self.take_screenshot()
            
            self.driver.close()

        except Exception as e:
            self.driver.close()
            Itax(file_nil=file_nil,channel_id=channel_id, itax_pin=itax_pin, itax_password=itax_password,
                 doc_to_be_uploaded=doc_to_be_uploaded, screenshot_path=screenshot_path)

    def captcha_solver(self):
        captcha_image = self.wait.until(EC.visibility_of_element_located((By.XPATH, self.captcha_image_xpath)))
        location = captcha_image.location
        size = captcha_image.size
        screenshot = self.driver.get_screenshot_as_png()
        image = Image.open(io.BytesIO(screenshot))

        location = {"x": 400, "y": 700}
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
        
        print("="*30)
        print(result)
        print(eval(result))
        print("="*30)

        return eval(result)

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
            self.wait.until(EC.alert_is_present(),
                                   'Timed out waiting for PA creation ' +
                                   'confirmation popup to appear.')
            alert = self.driver.switch_to_alert()

            alert.accept()

            self.wrong_password = True

        except:
            pass


        if not self.wrong_password:
           
            itax_password_input = self.wait.until(EC.visibility_of_element_located((By.XPATH, self.password_input_xpath)))
            itax_password_input.send_keys(self.itax_password)

            result = self.captcha_solver()

            captcha = self.wait.until(EC.visibility_of_element_located((By.XPATH, self.captcha_input_xpath)))
            captcha.send_keys(result)

            login_button = self.wait.until(EC.visibility_of_element_located((By.XPATH, self.login_button_xpath)))
            login_button.click()


            try:
                self.wait.until(EC.visibility_of_element_located((By.XPATH, self.invalid_credentials_xpath)))
                self.wrong_password = True
            except:
                pass

    def navigate_to_file_nil_tax_page(self):
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

    def navigate_to_filing_tax_page(self):
        main_returns_page_button = self.wait.until(
            EC.visibility_of_element_located((By.XPATH, self.main_returns_page_button_xpath)))
        hover = ActionChains(self.driver).move_to_element(main_returns_page_button)
        hover.perform()

        sub_returns_page_button = self.wait.until(
            EC.visibility_of_element_located((By.XPATH, self.sub_returns_page_button_xpath)))
        sub_returns_page_button.click()

        type_of_tax_obligation = self.wait.until(
            EC.visibility_of_element_located((By.XPATH, self.type_of_tax_obligation_button_xpath)))
        select = Select(type_of_tax_obligation)
        select.select_by_value(self.selected_type_of_tax_obligation_options)

        navigate_to_final_page_button = self.wait.until(
            EC.visibility_of_element_located((By.XPATH, self.navigate_to_final_page_button_xpath)))
        navigate_to_final_page_button.click()

    def upload_and_submit_tax_returns(self):
        type_of_tax_return = self.wait.until(
            EC.visibility_of_element_located((By.XPATH, self.type_of_tax_return_xpath)))
        select = Select(type_of_tax_return)
        select.select_by_value(self.selected_type_of_tax_return_options)

        tax_return_period_from = self.wait.until(
            EC.visibility_of_element_located((By.XPATH, self.tax_return_period_from_xpath))).get_attribute('value')
        tax_return_period_to = self.wait.until(
            EC.visibility_of_element_located((By.XPATH, self.tax_return_period_to_xpath))).get_attribute('value')
        agree_to_terms_and_conditions_checkbox = self.wait.until(
            EC.visibility_of_element_located((By.XPATH, self.agree_to_terms_and_conditions_checkbox_xpath)))
        agree_to_terms_and_conditions_checkbox.click()
        upload_zip_file = self.wait.until( EC.visibility_of_element_located((By.XPATH, self.upload_tax_return_input_xpath)))
        try:
            upload_zip_file.send_keys(self.zipfile_location)
        except Exception as e:
            print(e)

        print(tax_return_period_from, "-", tax_return_period_to)


    #def get obligations