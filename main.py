import logging
import webbrowser

import click
import yaml

from api.player import Player, Weapon
from api.riot import Auth

log = logging.getLogger(__name__)


@click.command()
@click.option("--config", "-c", default="config.yaml", help="Config file (default = config.yaml)")
@click.option("--accounts", default="", help="Specific accounts to check separated by a comma ','")
@click.option("--open-images", is_flag=True, default=False, help="Whether to open all links in browser.")
@click.option("--look-for", default=None, help="Specific skin to look for (case insensitive)")
@click.option("--dont-stall", is_flag=True, default=False, help="Whether to stall in program and wait for user input.")
def command(config: str, accounts: str, open_images: bool, look_for: str, dont_stall: bool):
    main(config=config, accounts=accounts, open_images=open_images, look_for=look_for, dont_stall=dont_stall)


def main(config: str, open_images: bool, accounts: str, look_for: str, dont_stall: bool):
    with open(config, "r") as file:
        parsed = yaml.safe_load(file)

    if not parsed:
        log.error("Invalid config file: %s", config)
        return

    accounts_to_check = set(accounts.split(","))
    for account in parsed.get("accounts", []):
        if not account:
            log.warning("Invalid account: '%s'", account)
            continue

        user = account.get("user", "").strip()
        pw = account.get("pw", "").strip()

        if accounts_to_check and user not in accounts_to_check:
            print(f"Skipping profile ${user} since it isn't present in '${accounts_to_check}'")
            continue

        print(f"Username: {user}")

        look_for_set = set(x.lower().strip() for x in look_for.split(",")) if look_for else set()
        weapons = get_shop(user, pw)
        for weapon in weapons:
            if not any(x in weapon.name.lower() for x in look_for_set):
                continue

            print(f"\t{weapon.name} - Cost: {weapon.cost} - {weapon.image}")

            if open_images:
                webbrowser.open(weapon.image)

        print()

    if not dont_stall:
        input("Press enter to exit...")


def get_shop(user: str, pw: str) -> list[Weapon] | None:
    if not user or not pw:
        log.warning("Missing credentials for user '%s' - '%s'", user, pw)
        return None

    auth = Auth(user, pw)
    auth.auth()

    if not auth.auth_successful():
        log.warning("Riot login failed for user: '%s' - '%s's", user, pw)
        return None

    player = Player(auth.access_token, auth.entitlement, auth.region, auth.user_id)
    return player.get_weapons()


if __name__ == "__main__":
    with open(".env", "r") as filename:
        username = filename.readline()

    main(
        config="config.yaml",
        open_images=False,
        accounts=username,
        look_for="luna",
        dont_stall=True
    )
