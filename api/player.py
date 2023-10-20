"""Source: https://github.com/GamerNoTitle/Valora/blob/master/utils/GetPlayer.py"""
from collections import namedtuple

import requests


# server list
AP_SERVER = "https://pd.ap.a.pvp.net"
NA_SERVER = "https://pd.na.a.pvp.net"
EU_SERVER = "https://pd.eu.a.pvp.net"
KR_SERVER = "https://pd.kr.a.pvp.net"

# API path
API_ACCOUNT_XP = "/account-xp/v1/players/"
API_MMR = "/mmr/v1/players/"
API_STORE = "/store/v2/storefront/"
API_WALLET = "/store/v1/wallet/"
API_OWNED = "/store/v1/entitlements/"

# UUIDs
UUID_AGENTS = "01bb38e1-da47-4e6a-9b3d-945fe4655707"
UUID_CONTRACTS = "f85cb6f7-33e5-4dc8-b609-ec7212301948"
UUID_SPRAYS = "d5f120f8-ff8c-4aac-92ea-f2b5acbe9475"
UUID_GUN_BUDDIES = "dd3bf334-87f3-40bd-b043-682a57a8dc3a"
UUID_PLAYER_CARDS = "3f296c07-64c3-494c-923b-fe692a4fa1bd"
UUID_SKINS = "e7c63390-eda7-46e0-bb7a-a6abdacd2433"
UUID_CHROMAS = "3ad1b2b2-acdb-4524-852f-954a76ddae0a"
UUID_PLAYER_TITLES = "de7caa6b-adf7-4588-bbd1-143831e786c6"

# Initialized variables
RIOT_CLIENT_VERSION = requests.get("https://valorant-api.com/v1/version", timeout=30).json()["data"]["riotClientVersion"]
WEAPON_UUID_MAPPING = {x["uuid"]: x for x in requests.get("https://valorant-api.com/v1/weapons/skinlevels").json()["data"]}

# Classes
Weapon = namedtuple("Weapon", ["name", "cost", "image"])


class Player:
    def __init__(self, access_token: str, entitlement_token: str, region: str, user_id: str):
        self.access_token = access_token
        self.entitlement = entitlement_token
        self.region = region
        self.__header = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Riot-Entitlements-JWT": self.entitlement,
            "X-Riot-ClientPlatform": "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9",
            "X-Riot-ClientVersion": RIOT_CLIENT_VERSION,
            "Content-Type": "application/json"
        }
        if region == "ap":
            server = AP_SERVER
        elif region == "eu":
            server = EU_SERVER
        elif region == "na":
            server = NA_SERVER
        else:
            server = KR_SERVER
        self.server = server
        self.user_id = user_id
        self.down = False
        response = requests.get(
            f"{server}{API_STORE}{user_id}", headers=self.__header, timeout=30)
        if response.status_code >= 500:
            self.down = True
            raise requests.exceptions.ConnectionError(f"It seems that Riot Games server run into an error ({response.status_code}): " + response.text)
        elif response.status_code == 403:
            if response.json()["errorCode"] == "SCHEDULED_DOWNTIME":
                self.down = True
            else:
                raise requests.exceptions.ConnectionError(f"It seems that Riot Games server run into an error ({response.status_code}): " + response.text)
        if not self.down:
            self.shop = response.json()
            if response.status_code == 400 or response.status_code == 404:
                self.auth = False
            else:
                self.auth = True

    def get_wallet(self):
        data = requests.get(f"{self.server}{API_WALLET}{self.user_id}",
                            headers=self.__header, timeout=30).json()
        try:
            self.vp = data["Balances"]["85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741"]
            self.rp = data["Balances"]["e59aa87c-4cbf-517a-5983-6e81511be9b7"]
            self.kc = data["Balances"]["85ca954a-41f2-ce94-9b45-8ca3dd39a00d"]
        except KeyError:
            self.auth = False
        self.wallet = data

    def get_skins(self):
        data = requests.get(f"{self.server}{API_OWNED}{self.user_id}/{UUID_SKINS}", headers=self.__header, timeout=30).json()
        skins = data["Entitlements"]
        owned_skins = []
        for skin in skins:
            owned_skins.append(skin["ItemID"].upper())
        self.skins = skins
        return skins, owned_skins

    def get_chromas(self):
        data = requests.get(f"{self.server}{API_OWNED}{self.user_id}/{UUID_CHROMAS}", headers=self.__header, timeout=30).json()
        chromas = data["Entitlements"]
        owned_chromas = []
        for chroma in chromas:
            owned_chromas.append(chroma["ItemID"].upper())
        self.chromas = chromas
        return chromas, owned_chromas

    def get_weapons(self) -> list[Weapon]:
        weapons = []
        shop = self.shop["SkinsPanelLayout"]
        for item in shop["SingleItemStoreOffers"]:
            offer_id = item["OfferID"]
            cost = item["Cost"]["85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741"]
            weapon_obj = WEAPON_UUID_MAPPING.get(offer_id)

            name = weapon_obj["displayName"]
            image = weapon_obj["displayIcon"]

            try:
                weapon = Weapon(name, cost, image)
            except IndexError:
                weapon = Weapon(f"N/A (unsupported id: {offer_id})", cost, "")

            weapons.append(weapon)

        return weapons


if __name__ == "__main__":
    p = Player("",
               "",
               "ap",
               "")
