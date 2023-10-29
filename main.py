import logging
import webbrowser

import click
import yaml

from api.player import Player
from api.riot import Auth

log = logging.getLogger(__name__)


@click.command()
@click.option("--config", "-c", default="config.yaml", help="Config file (default = config.yaml)")
@click.option("--open-images", is_flag=True, default=False, help="Whether to open all links in browser.")
def main(config: str, open_images: bool):
    with open(config, 'r') as file:
        parsed = yaml.safe_load(file)

    if not parsed:
        log.error("Invalid config file: %s", config)
        return

    for account in parsed.get("accounts", []):
        if not account:
            log.warning("Invalid account: '%s'", account)
            continue

        user = account.get("user", "").strip()
        pw = account.get("pw", "").strip()
        weapons = get_shop(user, pw)

        print(f"Username: {user}")
        for weapon in weapons:
            print(f"\t{weapon.name} - Cost: {weapon.cost} - {weapon.image}")

            if open_images:
                webbrowser.open(weapon.image)

        print()


def get_shop(user: str, pw: str):
    if not user or not pw:
        log.warning("Missing credentials for user '%s' - '%s'", user, pw)
        return

    auth = Auth(user, pw)
    auth.auth()

    if not auth.auth_successful():
        log.warning("Riot login failed for user: '%s' - '%s's", user, pw)
        return

    player = Player(auth.access_token, auth.entitlement, auth.region, auth.user_id)
    return player.get_weapons()


if __name__ == '__main__':
    main()
