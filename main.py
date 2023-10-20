import logging

import click
import requests
import yaml

from api.player import Player
from api.riot import Auth

log = logging.getLogger(__name__)

AUTH_URL = "https://auth.riotgames.com/api/v1/authorization"
REGION_URL = 'https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant'
VERIFIED_URL = "https://email-verification.riotgames.com/api/v1/account/status"
ENTITLEMENT_URL = 'https://entitlements.auth.riotgames.com/api/token/v1'
USERINFO_URL = "https://auth.riotgames.com/userinfo"
RIOT_CLIENT_BUILD = requests.get('https://valorant-api.com/v1/version').json()['data']['riotClientBuild']


@click.command()
@click.option("--config", "-c", default="config.yaml", help="Config file (default = config.yaml)")
def main(config: str):
    with open(config, 'r') as file:
        parsed = yaml.safe_load(file)

    if not parsed:
        log.error("Invalid config file: %s", config)
        return

    for account in parsed.get("accounts", []):
        if not account:
            log.warning("Invalid value: %s", account)
            continue

        get_shop(account.get("user"), account.get("pw"))


def get_shop(user: str, pw: str):
    if not user or not pw:
        log.warning("Missing credentials for user: %s pw: %s", user, pw)
        return

    auth = Auth(user, pw)
    auth.auth()

    if not auth.auth_successful():
        log.warning("Riot login failed for user: %s pw: %s", user, pw)
        return

    player = Player(auth.access_token, auth.entitlement, auth.region, auth.user_id)
    weapons = player.get_weapons()

    for weapon in weapons:
        print(f"{weapon.name} - Cost: {weapon.cost}")


if __name__ == '__main__':
    main()
