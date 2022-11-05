import json
import logging
from datetime import date

from beancount.core import data
from beancount.core.amount import Amount
from beancount.core.number import Decimal
from beancount.ingest import importer


class SwileImporter(importer.ImporterProtocol):
    def __init__(
        self,
        account: str,
        file_encoding: str = "latin-1",
    ):
        self.account = account
        self.file_encoding = file_encoding

    def identify(self, file_) -> bool:
        try:
            with open(file_.name, encoding=self.file_encoding) as transaction_file:
                _ = transaction_file.readline().strip()
        except ValueError:
            return False
        return True

    def extract(self, file_, existing_entries=None):
        entries = []
        entry_ids = set()

        with open(file_.name, encoding=self.file_encoding) as transaction_file:
            transactions = json.load(transaction_file)

        for index, line in enumerate(transactions):
            if line["id"] in entry_ids:  # Also skip existing entries
                continue
            entry_ids.add(line["id"])
            failed_transaction = [
                a
                for a in line["operation"]["transactions"]
                if a["status"] == "DECLINED"
            ]
            if failed_transaction:
                continue

            voucher_payments = [
                a
                for a in line["operation"]["transactions"]
                if a["payment_method"] == "Wallets::MealVoucherWallet"
                and a["type"] == "ORIGIN"
                and a["status"] != "RELEASED"
            ]
            if not voucher_payments:
                continue

            meta = data.new_metadata(file_.name, index, {"id": line["id"]})

            amount_eur = Decimal(str(voucher_payments[0]["amount"]["value"]))
            currency = "EUR"
            day = date.fromisoformat(line["operation"]["date"][:10])
            payee = line["operation"]["name"]

            postings = [
                data.Posting(
                    self.account,
                    Amount(amount_eur, currency),
                    None,
                    None,
                    None,
                    None,
                ),
            ]

            entries.append(
                data.Transaction(
                    meta,
                    day,
                    "!" if len(voucher_payments) > 1 else self.FLAG,
                    payee,
                    "",
                    data.EMPTY_SET,
                    data.EMPTY_SET,
                    postings,
                )
            )

        return entries
