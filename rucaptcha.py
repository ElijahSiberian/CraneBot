import requests
import time
import re as reg_exp
import error_hook

class RuCaptcha:
    captcha_image = ' '
    captcha_api = ' '

    def captcha_solver(self, image, api, browser):
        self.captcha_image = image
        self.captcha_api = api
        if not RuCaptcha.captcha_grabber(self, browser):
            return None
        url = 'http://rucaptcha.com/in.php'
        files_attrib = {"file": open("data/captcha_shots/" + self.captcha_image, "rb")}
        api_attrib = {"key": self.captcha_api}
        try:
            answer = requests.post(url, files=files_attrib, data=api_attrib)
        except Exception as err:
            error_hook.fatal_err("Не удалось отправить капчу", err)
            return RuCaptcha.captcha_solver(self, self.captcha_image, self.captcha_api, browser)
        print("[+]Отправил капчу на RuCaptcha \n[+]Ответили: " + answer.text)
        result_busy = reg_exp.match('ERROR_NO_SLOT_AVAILABLE', answer.text)
        result_ok = reg_exp.match('OK|', answer.text)
        if result_busy:
            print('[.]Все слоты заняты, нужно подождать...')
            time.sleep(5)
            return RuCaptcha.captcha_solver(self, self.captcha_image, self.captcha_api, browser)
        elif result_ok:
            try:
                captcha_id = answer.text.split("|")[1]
            except Exception as err:
                error_hook.fatal_err("Не удалось обработать ответ: " + answer.text, err)
                time.sleep(5)
                return RuCaptcha.captcha_solver(self, self.captcha_image, self.captcha_api, browser)
        else:
            error_hook.warn_err("Проблемы с RuCaptcha.")
            time.sleep(5)
            return RuCaptcha.captcha_solver(self, self.captcha_image, self.captcha_api, browser)
        url2 = 'http://rucaptcha.com/res.php?key='
        request_url = url2 + str(self.captcha_api) + '&action=get&id=' + captcha_id
        try:
            print("[+]Делаю запрос на " + request_url)
            solved = requests.get(request_url)
        except Exception as err:
            error_hook.fatal_err("Не удалось получить ответ от RuCaptcha", err)
            return RuCaptcha.captcha_solver(self, self.captcha_image, self.captcha_api, browser)
        captcha_answ = RuCaptcha.cap_check(self, solved, request_url)
        if not captcha_answ:
            RuCaptcha.captcha_solver(self, self.captcha_image, self.captcha_api, browser)
        else:
            return captcha_answ

    def cap_check(self, solved, request_url):
        try:
            result_wait = reg_exp.match('CAPCHA_NOT_READY', solved.text)
            result_unsolv = reg_exp.match('ERROR_CAPTCHA_UNSOLVABLE', solved.text)
            result_solv = reg_exp.match('OK\|', solved.text)
        except Exception as err:
            error_hook.warn_err("Странный ответ от RuCapcha" + solved.text)
            return None
        if result_wait:
            print('[.]Капча еще не готова, жду...')
            time.sleep(5)
            solved = requests.get(request_url)
            return RuCaptcha.cap_check(self, solved, request_url)
        elif result_solv:
            res = reg_exp.split('\|', solved.text, maxsplit=1)
            if len(res) < 2:
                return None
            captcha_answ = str(res[1])
            print("[+]Капча получена: " + captcha_answ)
            return captcha_answ
        elif result_unsolv:
            error_hook.warn_err('Не удалось обработать капчу. Ответ от макаки: ' + str(solved.text))
            return None
        else:
            return None

    def captcha_grabber(self, browser):
        from PIL import Image
        try:
            refresh = browser.find_element_by_id("adcopy-link-refresh")
            refresh.click()
        except Exception as err:
            error_hook.fatal_err("Не удалось обновить капчу", err)
            error_hook.screen_grab(browser)
            return None
        time.sleep(5)
        try:
            element = browser.find_element_by_id("adcopy-puzzle-image-image")
            if not element:
                element = browser.find_element_by_id("adcopy-puzzle-image")
            el_locate = element.location
            el_size = element.size
        except Exception as err:
            error_hook.fatal_err("Не удалось найти капчу", err)
            return None
        try:
            browser.save_screenshot("data/captcha_shots/" + self.captcha_image)
            captcha_to_solve = Image.open("data/captcha_shots/" + self.captcha_image)
            left = el_locate['x']
            top = el_locate['y']
            right = left + el_size['width']
            bottom = top + el_size['height']
            captcha_to_solve = captcha_to_solve.crop((left, top, right, bottom))
            captcha_to_solve.save("data/captcha_shots/" + self.captcha_image)
        except Exception as err:
            error_hook.fatal_err("Не удалось подготовить капчу к отправке", err)
            return RuCaptcha.captcha_grabber(self, browser)
        print("[+]Сохранил капчу с именем " + str(self.captcha_image))
        return 1
