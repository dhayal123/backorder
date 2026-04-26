import os
import csv
from datetime import datetime
from pytz import timezone, UTC

folder = "/Users/dhayalmani/Downloads/Data/backorder"
input_csv = os.path.join(folder, "automatticlist.csv")
output_csv = os.path.join(folder, "Processedautomatticlist.csv")

output_fields = [
    "DOMAIN", "TLD", "DROPDATE", "LENGTH",
    "LINK", "SOURCE", "APPRAISAL", "TYPE"
]

def parse_join_by_date_et(dt_str):
    """
    Convert 'MM/DD/YYYY HH:MM' (or M/D/YY) in ET to 'YYYY-MM-DD HH:MM' UTC.
    """
    dt_str = dt_str.strip()
    if not dt_str:
        return ""
    for fmt in ("%m/%d/%Y %H:%M", "%m/%d/%y %H:%M"):
        try:
            dt_local = datetime.strptime(dt_str, fmt)
            ny_tz = timezone("America/New_York")
            dt_et = ny_tz.localize(dt_local)
            dt_utc = dt_et.astimezone(UTC)
            return dt_utc.strftime("%Y-%m-%d %H:%M")
        except ValueError:
            continue
    return dt_str

with open(input_csv, newline="", encoding="utf-8-sig") as f_in, \
     open(output_csv, "w", newline="", encoding="utf-8") as f_out:

    reader = csv.DictReader(f_in, delimiter=",")
    writer = csv.DictWriter(f_out, fieldnames=output_fields)
    writer.writeheader()

    for row in reader:
        # Skip completely empty rows (including the blank row after headers)
        if not row or all((v is None or str(v).strip() == "") for v in row.values()):
            continue

        domain = (row.get("Domain Name") or "").strip()
        if not domain:
            continue

        tld = (row.get("TLD") or "").strip()
        length_str = (row.get("Length") or "").strip()
        try:
            length = int(length_str)
        except ValueError:
            length = len(domain.split(".")[0]) if "." in domain else len(domain)

        join_by_et = (row.get("Join By Date (ET)") or "").strip()
        dropdate_utc = parse_join_by_date_et(join_by_et)

        seller = (row.get("Seller") or "").strip()
        auction_type = (row.get("Auction Type") or "").strip()

        link = f"https://www.snapnames.com/domain/{domain}.action"

        out_row = {
            "DOMAIN": domain,
            "TLD": tld,
            "DROPDATE": dropdate_utc,
            "LENGTH": length,
            "LINK": link,
            "SOURCE": seller,
            "APPRAISAL": "",     # keep blank
            "TYPE": auction_type,
        }
        writer.writerow(out_row)

print(f"Processed data written to {output_csv}")