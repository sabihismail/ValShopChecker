"""Source: https://github.com/GamerNoTitle/Valora/blob/master/utils/RiotLogin.py"""

import ssl
import requests
import time
import sys
from datetime import datetime
from typing import Any
from collections import OrderedDict
from requests.adapters import HTTPAdapter
from re import compile
from colorama import Fore

CIPHERS = [
    "ECDHE-ECDSA-AES128-GCM-SHA256",
    "ECDHE-ECDSA-CHACHA20-POLY1305",
    "ECDHE-RSA-AES128-GCM-SHA256",
    "ECDHE-RSA-CHACHA20-POLY1305",
    "ECDHE+AES128",
    "RSA+AES128",
    "ECDHE+AES256",
    "RSA+AES256",
    "ECDHE+3DES",
    "RSA+3DES"
]

version_info = requests.get("https://valorant-api.com/v1/version").json()["data"]
RIOT_CLIENT_BUILD = version_info["riotClientBuild"]
RIOT_CLIENT_VERSION = version_info["riotClientVersion"]

AUTH_URL = "https://auth.riotgames.com/api/v1/authorization"
REGION_URL = "https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant"
VERIFIED_URL = "https://email-verification.riotgames.com/api/v1/account/status"
ENTITLEMENT_URL = "https://entitlements.auth.riotgames.com/api/token/v1"
USERINFO_URL = "https://auth.riotgames.com/userinfo"


class SSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *a: Any, **k: Any) -> None:
        c = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        c.set_ciphers(":".join(CIPHERS))
        k["ssl_context"] = c
        return super(SSLAdapter, self).init_poolmanager(*a, **k)


class Auth:
    def __init__(self, username: str, password: str, session=None):
        self.region = None
        self.username = username
        self.password = password
        self.session = requests.Session() if not session else session
        self.session.headers = OrderedDict(
            {"User-Agent": f"RiotClient/{RIOT_CLIENT_BUILD} riot-status (Windows;10;;Professional, x64)",
             "Accept-Language": "en-US,en;q=0.9", "Accept": "application/json, text/plain, */*"})
        self.session.mount("https://", SSLAdapter())
        self.authed = False
        self.MFA = False
        self.remember = False
        self.user_id = ""

    def auth(self, mfa_code=""):
        tokens = self.authorize(mfa_code)
        try:
            if "x" in tokens:
                return
        except TypeError:
            raise
        self.authed = True
        self.access_token = tokens[0]
        self.id_token = tokens[1]

        self.base_headers = {
            "User-Agent": f"RiotClient/{RIOT_CLIENT_BUILD} riot-status (Windows;10;;Professional, x64)",
            "Authorization": f"Bearer {self.access_token}"
        }
        self.session.headers.update(self.base_headers)

        self.entitlement = self.get_entitlement_token()
        self.emailverifed = self.get_email_verified()

        userinfo = self.get_userinfo()
        self.user_id = userinfo[0]
        self.Name = userinfo[1]
        self.Tag = userinfo[2]
        self.creationdata = userinfo[3]
        self.typeban = userinfo[4]
        self.region_headers = {"Content-Type": "application/json",
                               "Authorization": f"Bearer {self.access_token}"}
        self.session.headers.update(self.region_headers)
        self.region = self.get_region()
        # self.p = self.print()

    def authorize(self, mfa_code=""):
        data = {"acr_values": "urn:riot:bronze", "claims": "", "client_id": "riot-client",
                "nonce": "oYnVwCSrlS5IHKh7iI16oQ",
                "redirect_uri": "http://localhost/redirect", "response_type": "token id_token",
                "scope": "openid link ban lol_region"}
        data2 = {"language": "en_US", "password": self.password,
                 "remember": "true", "type": "auth", "username": self.username}

        self.session.post(url=AUTH_URL, json=data)
        r = self.session.put(url=AUTH_URL, json=data2)
        data = r.json()
        if "access_token" in r.text:
            pattern = compile(
                "access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)"
            )
            data = pattern.findall(data["response"]["parameters"]["uri"])[0]
            token = data[0]
            token_id = data[1]
            return [token, token_id]

        elif "auth_failure" in r.text:
            print(F"{Fore.RED}[ACCOUNT DOESN'T EXIST] {Fore.RESET}{self.username}:{self.password}")
            return "x"

        elif "rate_limited" in r.text:
            print(F"{Fore.YELLOW}[RATE LIMITED] {Fore.RESET}{self.username}:{self.password}")
            time.sleep(40)
            return "x"
        elif self.MFA:
            # ver_code = input(F"{Fore.GREEN}2FA Auth Enabled{Fore.RESET}. Enter the verification code: \n")
            if __name__ == "__main__":
                ver_code = input("Please input your ver code: ")
            else:
                ver_code = mfa_code
            authdata = {
                "type": "multifactor",
                "code": ver_code,
                "rememberDevice": self.remember,
            }
            r = self.session.put(url=AUTH_URL, json=authdata)
            data = r.json()
            if "access_token" in r.text:
                pattern = compile(
                    "access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)")
                data = pattern.findall(
                    data["response"]["parameters"]["uri"])[0]
                token = data[0]
                token_id = data[1]
                return [token, token_id]

            elif "auth_failure" in r.text:
                # banned (?)
                print(
                    F"{Fore.RED}[ERROR] {Fore.RESET}{self.username}:{self.password}")
            else:
                print(
                    F"{Fore.RED}[ERROR] {Fore.RESET}{self.username}:{self.password}")
        else:
            self.MFA = True
            return "x"

    def get_entitlement_token(self):
        r = self.session.post(ENTITLEMENT_URL, json={})
        entitlement = r.json()["entitlements_token"]
        return entitlement

    def get_email_verified(self):
        r = self.session.get(url=VERIFIED_URL, json={})
        email_verified = r.json()["emailVerified"]
        return email_verified

    def get_userinfo(self):
        r = self.session.get(url=USERINFO_URL, json={})
        data = r.json()
        Sub = data["sub"]
        data1 = data["acct"]
        Name = data1["game_name"]
        Tag = data1["tag_line"]
        time4 = data1["created_at"]
        time4 = int(time4)
        Createdat = datetime.fromtimestamp(time4 / 1000.0)
        data2 = data["ban"]
        data3 = data2.get("restrictions", [])
        typeban = None
        if data3 != []:
            for x in data3:
                type = x["type"]
                if type == "TIME_BAN":
                    for y in data3:
                        lol = y["dat"]
                        exeperationdate = lol["expirationMillis"]
                        time1 = exeperationdate
                        time1 = int(time1)
                        try:
                            Exp = datetime.fromtimestamp(time1 / 1000.0)
                        except:
                            Exp = None
                        str(Exp)
                    typeban = "TIME_BAN"
                if type == "PERMANENT_BAN":
                    typeban = "PERMANENT_BAN"
        if data3 == [] or "PBE_LOGIN_TIME_BAN" in data3 or "LEGACY_BAN" in data3:
            typeban = "None"
        return [Sub, Name, Tag, Createdat, typeban]

    def get_region(self):
        json = {"id_token": self.id_token}
        r = self.session.put(
            "https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant", json=json)
        data = r.json()
        region = data["affinities"]["live"]
        return region

    def auth_successful(self):
        return self.authed and self.user_id and self.access_token

    def print(self):
        if not self.auth_successful():
            print("Auth failed!")
            return

        print(f"Access token: {self.access_token}")
        print("-" * 50)
        print(f"Entitlements: {self.entitlement}")
        print("-" * 50)
        print(f"Userid: {self.user_id}")
        print("-" * 50)
        print(f"Region: {self.region}")
        print("-" * 50)
        print(f"Name: {self.Name}#{self.Tag}")
        print("-" * 50)
        print(f"Created at: {self.creationdata}")
        print("-" * 50)
        print(f"Bantype: {self.typeban}")


if __name__ == "__main__":
    username, password = sys.argv[1], sys.argv[2]
    user = Auth(username, password)
    user.auth()
    user.print()
