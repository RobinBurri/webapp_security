import sys
import urllib.parse

import requests
import urllib3
from colorama import Fore

urllib3.disable_warnings()

proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}

DB = None
COMMENTS = None


def find_tables_name(base_url: str, db_version: str, number_table) -> bool:
    base_queries = []
    return False


if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()

    except IndexError:
        print(f"[-] Usage: {sys.argv[0]} <url>")
        print(f'[-] Example: {sys.argv[0]} www.google.com"')
        sys.exit(-1)
    found_name = find_tables_name(url)
    if not found_name:
        print("[-] Exploit failed")
