import csv
from decimal import Decimal
from operator import itemgetter
import os
import pprint
from re import sub


# go to https://client.schwab.com/Areas/Accounts/Positions
# in the securities table, click on the cost basis
# then click export
COST_BASIS_FILES = {
    "VOO": os.path.join("reports", "voo.csv"),
    "VTI": os.path.join("reports", "vti.csv"),
    "VXUS": os.path.join("reports", "vxus.csv"),
}
DONATION_AMOUNT = 5000


def parse_cost_basis_row(row):
    money_fields = ["Price", "Cost/Share", "Market Value", "Cost Basis", "Gain/Loss $"]
    for field in money_fields:
        # straight from https://stackoverflow.com/a/8422055
        row[field] = Decimal(sub(r"[^\d.]", "", row[field]))
    return row


def parse_cost_basis_report(filename):
    with open(filename, newline="") as csvfile:
        next(
            csvfile
        )  # first line is a report heading, e.g. "VOO Lot Details for XXXX-1608 as of 06:36 PM ET, 12/19/2020"
        next(csvfile)  # next line is empty
        reader = csv.DictReader(csvfile)
        rows = [r for r in reader]

    rows = rows[:-1]  # the last row is a total
    return [parse_cost_basis_row(r) for r in rows]


def main():
    all_cost_bases = []
    for stock, f in COST_BASIS_FILES.items():
        cost_bases = parse_cost_basis_report(f)
        for c in cost_bases:
            c["Stock"] = stock
        all_cost_bases.extend(cost_bases)

    long_term_bases = [c for c in all_cost_bases if c["Holding Period"] == "Long Term"]

    # we want to maximize unrealized gains
    long_term_bases.sort(key=itemgetter("Gain/Loss $"), reverse=True)

    total_donated = 0
    total_cost_basis = 0
    donation_rows = []
    for base in long_term_bases:
        if total_donated >= DONATION_AMOUNT:
            break
        total_donated += base["Market Value"]
        total_cost_basis += base["Cost Basis"]
        donation_rows.append(base)

    for r in donation_rows:
        print(f"{r['Stock']}: Purchased {r['Open Date']}, Quantity {r['Quantity']}")
    print(f"COST BASIS: ${total_cost_basis} (out of total ${total_donated})")


if __name__ == "__main__":
    main()
