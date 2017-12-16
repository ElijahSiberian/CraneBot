import time


def screen_grab(browser):
    try:
        a = time.strftime("[%H.%M.%S]", time.localtime())
        captcha_image = a + "Error.png"
        browser.save_screenshot("data/error_hooks/" + captcha_image)
    except Exception as err:
        print("[!]Не удалось сохранить скриншот ощибки. Error " + str(err))
    else:
        print("[+]Сохранил скриншот ошибки с именем " + str(captcha_image))


def fatal_err(text, problemo):
    shitty_time = time.strftime("%H:%M:%S", time.localtime())
    print("[!]|" + shitty_time + "|" + str(text) + " Ошибка-> " + str(problemo))


def warn_err(text):
    print("[-]" + str(text))
