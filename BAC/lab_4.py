# Lab #4 User role can be modified in user profile 
# import re
import sys

# from typing import Optional, cast

# import requests
import urllib3
# from bs4 import BeautifulSoup
# from bs4.element import Tag
from colorama import Fore

# import urllib.parse
# from requests.exceptions import RequestException

urllib3.disable_warnings()

proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}



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
    # exploit()
