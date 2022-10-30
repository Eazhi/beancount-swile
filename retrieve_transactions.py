import json
from datetime import datetime, timezone

import requests
import typer

SWILE_URL = "https://neobank-api.swile.co/api/v1/user/operations"


def main(token: str, output_file: str = "all_transactions.json"):
    """
    Retrieve your token connecting to swile.co
    In the network calls search for `operation?`
    Retrieve your tokens from the headers
    """
    now = datetime.now(timezone.utc)
    response = requests.get(
        f"{SWILE_URL}?before={now}&per=50",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    if not response.ok:
        raise Exception(f"Request failed: {response.text}")
    transactions = response.json()["data"]

    while response.json()["has_more"]:
        date = response.json()["next_date"]
        response = requests.get(
            f"{SWILE_URL}?before={date}&per=50",
            headers={"Authorization": f"Bearer {token}"},
            timeout=15,
        )
        if not response.ok:
            raise Exception(f"Request failed: {response.text}")

        transactions += response.json()["data"]

    with open(output_file, "w+") as transactions_file:
        json.dump(transactions, transactions_file, indent=2)


if __name__ == "__main__":
    typer.run(main)
