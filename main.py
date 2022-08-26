import os
import random
import string
import time

from email_validator import validate_email, EmailNotValidError
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from twocaptcha import TwoCaptcha
from webdriver_manager.chrome import ChromeDriverManager


SITE_KEY = "4c672d35-0701-42b2-88c3-78380b0db560"
REGISTER_URL = "https://discord.com/register"

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


def check_email():
    email = input("Please provide your email: ")
    try:
        validated_email = validate_email(email).email
        return validated_email
    except EmailNotValidError as e:
        print(str(e))
        return check_email()


def check_username():
    username = input("Please provide your username: ")
    if len(username) < 5:
        print("Username should have minimum 5 characters. Please try again.")
        return check_username()
    return username


def generate_password(length: int = 15):
    source = string.ascii_letters + string.digits
    password = "".join((random.choice(source) for _ in range(length)))
    print("Password generated successfully.")

    return password


def register_user(email: str, username: str, password: str):

    driver.get(REGISTER_URL)

    email_field = driver.find_element(By.NAME, "email")
    password_field = driver.find_element(By.NAME, "password")
    username_field = driver.find_element(By.NAME, "username")

    time.sleep(1)

    email_field.send_keys(email)
    username_field.send_keys(username)
    password_field.send_keys(password)

    day = driver.find_element(By.XPATH, "//*[@id='react-select-2-input']")
    month = driver.find_element(By.XPATH, "//*[@id='react-select-3-input']")
    year = driver.find_element(By.XPATH, "//*[@id='react-select-4-input']")

    day.send_keys(1)
    month.send_keys("січень")
    month.send_keys(Keys.ENTER)
    year.send_keys(1990)
    year.send_keys(Keys.ENTER)
    year.send_keys(Keys.ENTER)

    time.sleep(2)


def solve_captcha(site_key: str, url: str) -> dict:
    api_key = os.getenv('API_KEY')

    solver = TwoCaptcha(api_key)

    try:
        result = solver.hcaptcha(
            sitekey=site_key,
            url=url,
        )

    except Exception as e:
        print(e)
        return

    else:
        return result


def bypass_captcha(captcha_code: str):
    try:
        driver.execute_script(
            f"document.querySelector('iframe').parentElement."
            f"parentElement.__reactProps$.children"
            f".props.onVerify('{captcha_code}')"
        )
        WebDriverWait(driver, 10).until(
            EC.url_to_be("https://discord.com/channels/@me")
        )

    except Exception:
        print("Oops, this email is already registered. Try other one")


def get_token():
    token = driver.execute_script(
        "location.reload();var i=document.createElement('iframe');"
        "document.body.appendChild(i);return "
        "i.contentWindow.localStorage.token"
    ).strip('"')

    print("token:", token)


def main():
    email = check_email()
    username = check_username()
    password = generate_password(15)

    try:
        register_user(email, username, password)
    except Exception as e:
        print(e)
    else:
        try:
            captcha = solve_captcha(SITE_KEY, REGISTER_URL)
            bypass_captcha(captcha["code"])
            get_token()
        except AttributeError:
            print("Please try again")


if __name__ == '__main__':
    main()
