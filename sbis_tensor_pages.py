import os
import re
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec


class BasePage:
    def __init__(self, browser, wait):
        self.browser = browser
        self.wait = wait

    def get_current_url(self):
        return self.browser.current_url


class SbisPage(BasePage):
    def go_to_sbis_page(self):
        self.browser.get("https://sbis.ru/")

    def go_to_contacts_page(self):
        contacts_link = self.browser.find_element(By.LINK_TEXT, "Контакты")
        contacts_link.click()

    def go_to_tensor_page(self):
        self.wait.until(ec.invisibility_of_element_located((By.CLASS_NAME, "preload-overlay")))
        tensor_link = self.wait.until(ec.element_to_be_clickable((By.CLASS_NAME, "sbisru-Contacts__logo-tensor")))
        tensor_link.click()

    def switch_to_tensor_tab(self):
        self.browser.switch_to.window(self.browser.window_handles[-1])
        self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, "tensor_ru-Footer")))
        self.wait.until(ec.invisibility_of_element_located((By.CLASS_NAME, "preload-overlay")))
        return TensorPage(self.browser, self.wait)

    def get_current_partners(self):
        partners = self.wait.until(ec.visibility_of_all_elements_located((By.CLASS_NAME, 'sbisru-Contacts-List__item')))
        partners = [partner.text for partner in partners]
        return partners

    def get_current_region(self):
        current_region = self.wait.until(ec.visibility_of_element_located(
            (By.XPATH, "//span[contains(@class, 'sbis_ru-Region-Chooser__text sbis_ru-link')]")
        ))
        return current_region.text

    def change_region(self, value):
        current_region = self.wait.until(ec.element_to_be_clickable(
            (By.XPATH, "//span[contains(@class, 'sbis_ru-Region-Chooser__text sbis_ru-link')]")
        ))
        current_region.click()

        required_region = self.wait.until(ec.element_to_be_clickable(
            (By.XPATH,
             f"//div[@class='sbis_ru-Region-Panel']//span[contains(text(), '{value}')]"
             )
        ))
        required_region.click()

    def get_current_title(self):
        title = self.wait.until(ec.visibility_of_element_located(
            (By.XPATH, '//span[contains(@class, "sbis_ru-Region-Chooser__text sbis_ru-link")]')
        ))
        return title.text

    def go_to_download_page(self):
        download_page_link = self.wait.until(ec.element_to_be_clickable(
            (By.XPATH, "//div[contains(@class, 'sbisru-Footer sbisru-Footer__scheme--default')]"
                       "//a[contains(text(), 'Скачать СБИС')]")
        ))
        self.browser.execute_script("arguments[0].scrollIntoView();", download_page_link)
        download_page_link.click()

    def go_to_download_plugin_page(self):
        self.wait.until(ec.visibility_of_element_located(
            (By.XPATH,
             "//div[contains(@class, 'sbis_ru-FooterNew__bottom s-Grid-container')]")
        ))
        download_plugin_link = self.wait.until(ec.element_to_be_clickable(
            (By.XPATH,
             '//div[@data-id="plugin"]')
        ))
        download_plugin_link.click()

    def choose_plugin_windows_platform(self):
        windows_platform = self.wait.until(ec.element_to_be_clickable(
            (By.XPATH,
             "//div[contains(@class, 'controls-TabButton__inner')]"
             "//span[contains(text(), 'Windows')]")
        ))
        windows_platform.click()

    def download_windows_plugin(self):
        download_plugin_link = self.wait.until(ec.presence_of_element_located(
            (By.XPATH,
             "//div[contains(@class, 'sbis_ru-DownloadNew-block sbis_ru-DownloadNew-flex') and .//text()[contains(., "
             "'Веб-установщик')]]"
             "//a[contains(@class, 'sbis_ru-DownloadNew-loadLink__link js-link')]")
        ))

        downloaded_file = requests.get(download_plugin_link.get_attribute('href'), stream=True)
        with open('file.exe', 'wb') as file:
            file.write(downloaded_file.content)

        real_file_size = os.path.getsize('file.exe')
        match = re.search(r'\d+\.\d+', download_plugin_link.text)
        expected_file_size = float(match.group())

        return expected_file_size, round(real_file_size / 1024 / 1024, 2)  # переводим в мб и округляем


class TensorPage(BasePage):
    def get_block_power_in_people(self):
        block_power_in_people = self.wait.until(ec.presence_of_element_located(
            (By.CLASS_NAME, "tensor_ru-Index__block4-content")
        ))
        assert block_power_in_people is not None, "Блок \"Сила в людях\" не найден"
        return block_power_in_people

    def go_to_tensor_about_page(self, block_power_in_people):
        link_about = block_power_in_people.find_element(By.CLASS_NAME, "tensor_ru-link")
        self.browser.execute_script("arguments[0].scrollIntoView();", link_about)
        link_about.click()

    def get_tensor_about_images(self):
        block_with_images = self.wait.until(ec.presence_of_element_located((
            By.XPATH,
            "//div[contains(@class, 'tensor_ru-container tensor_ru-section tensor_ru-About__block3')]"
            "/div[@class='s-Grid-container']"
        )))
        images = block_with_images.find_elements(
            By.XPATH, "//img[contains(@class, 'tensor_ru-About__block3-image new_lazy')]"
        )
        return images
