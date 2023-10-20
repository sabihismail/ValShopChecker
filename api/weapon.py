"""Source: https://github.com/GamerNoTitle/Valora/blob/master/utils/Weapon.py#L15"""
import json
import sqlite3

import yaml

WEAPON_RARITY_DICT = {
    "12683d76-48d7-84a3-4e09-6985794f0445": {"name": "Select", "img": "/assets/img/Select-edition-icon.webp"},
    "0cebb8be-46d7-c12a-d306-e9907bfc5a25": {"name": "Deluxe", "img": "/assets/img/Deluxe-edition-icon.webp"},
    "60bca009-4182-7998-dee7-b8a2558dc369": {"name": "Premium", "img": "/assets/img/Premium-edition-icon.webp"},
    "411e4a55-4e59-7757-41f0-86a53f101bb5": {"name": "Ultra", "img": "/assets/img/Ultra-edition-icon.webp"},
    "e046854e-406c-37f4-6607-19a9ba8426fc": {"name": "Exclusive", "img": "/assets/img/Exclusive-edition-icon.webp"}
}


class Weapon:
    def __init__(self, uuid: str, cost: int = 0, discount: int = 0, discountPercentage: int = 0, lang: str = "en"):
        if not uuid:
            return

        conn = sqlite3.connect("res/data.db")
        c = conn.cursor()
        with open(f"res/{lang}.yml", encoding="utf8") as f:
            transtable = f.read()
        levelup_info = dict(yaml.load(transtable, Loader=yaml.FullLoader))["metadata"]["level"]
        description_to_del = dict(yaml.load(transtable, Loader=yaml.FullLoader))["metadata"]["description"]
        self.uuid = uuid
        self.cost = cost
        self.weapon_id = None
        # Get Weapon Name
        if lang == "en":
            c.execute(f"SELECT name FROM skinlevels WHERE uuid = ?", (self.uuid,))
        else:
            c.execute(
                f"SELECT 'name-{lang}' FROM skinlevels WHERE uuid = ?", (self.uuid,))

        conn.commit()
        self.name = c.fetchall()[0][0]

        # Get Weapon Data
        if lang == "en":
            c.execute(f"SELECT data FROM skins WHERE name = ?", (self.name,))
        else:
            c.execute(
                f"SELECT 'data-{lang}' FROM skins WHERE 'name-{lang}' = ?", (self.name,))

        conn.commit()
        self.data = json.loads(c.fetchall()[0][0])

        self.levels = self.data["levels"]    # Skin Levels
        self.chromas = self.data["chromas"]  # Skin Chromas
        self.base_img = self.data["levels"][0]["displayIcon"]
        self.tier = self.data["contentTierUuid"]
        self.tier_img = WEAPON_RARITY_DICT.get(self.tier).get("img")
        self.discount = discount
        self.per = discountPercentage

        for level in self.levels:
            level["uuid"] = level["uuid"].upper()
            level["displayName"] = level["displayName"].replace(self.name, "").replace("\n", "").replace(
                "（", "").replace("）", "").replace(" / ", "").replace("／", "/").replace("(", "").replace(")", "").replace("：", "").replace(" - ", "").replace("。", "")
            for descr in dict(description_to_del).values():
                level["displayName"] = level["displayName"].replace(descr, "")
            try:
                if level["levelItem"] == None:
                    level["levelItem"] = levelup_info["EEquippableSkinLevelItem::VFX"]
                else:
                    level["levelItem"] = levelup_info[level["levelItem"]]
            except KeyError:
                level["levelItem"] = level["levelItem"].replace(
                    "EEquippableSkinLevelItem::", "")

        for chroma in self.chromas:
            chroma["uuid"] = chroma["uuid"].upper()
            chroma["displayName"] = chroma["displayName"].replace(self.name, "").replace("\n", "").replace(
                "（", "").replace("）", "").replace(" / ", "").replace("／", "/").replace("(", "").replace(")", "").replace("：", "").replace(" - ", "")
            chroma["displayName"] = chroma["displayName"].strip().replace(
                levelup_info["level"] + "1", "").replace(levelup_info["level"] + "2", "").replace(
                levelup_info["level"] + "3", "").replace(levelup_info["level"] + "4", "").replace(
                    levelup_info["level"] + "5", "").replace(
                levelup_info["level"] + " 1", "").replace(levelup_info["level"] + " 2", "").replace(
                levelup_info["level"] + " 3", "").replace(levelup_info["level"] + " 4", "").replace(
                    levelup_info["level"] + " 5", "")   # Clear out extra level symbols
