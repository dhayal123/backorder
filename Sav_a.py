import csv
from datetime import datetime
import pytz
import os
import re

# Folder where the file is downloaded
folder = "/Users/dhayalmani/Downloads/Data/backorder"

# Target name
input_csv = os.path.join(folder, "sav_active_auctions_export.csv")
output_csv = os.path.join(folder, "processed_Sav.csv")

# UUID pattern: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.csv
uuid_pattern = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.csv$',
    re.IGNORECASE
)

# Auto-detect UUID-named CSV in the folder and rename it
for filename in os.listdir(folder):
    if uuid_pattern.match(filename):
        original_path = os.path.join(folder, filename)
        if os.path.exists(input_csv):
            os.remove(input_csv)
        os.rename(original_path, input_csv)
        print(f"Renamed: {filename} -> sav_active_auctions_export.csv")
        break  # Only rename the first match

# Safety check
if not os.path.exists(input_csv):
    raise FileNotFoundError(
        f"No UUID-named CSV found in {folder} and sav_active_auctions_export.csv does not exist."
    )

output_fields = ["DOMAIN", "TLD", "DROPDATE", "LENGTH", "LINK", "SOURCE", "APPRAISAL"]


def is_idn(domain):
    return any(ord(c) > 127 for c in domain)


def cdt_to_utc(dtstr):
    # Parse CDT time as 'MM/DD/YYYY HH:MM:SS'
    try:
        cdt_tz = pytz.timezone('America/Chicago')  # CDT / CST zone
        dt_local = datetime.strptime(dtstr, '%m/%d/%Y %H:%M:%S')
        dt_cdt = cdt_tz.localize(dt_local)
        dt_utc = dt_cdt.astimezone(pytz.utc)
        return dt_utc.strftime('%m/%d/%y %H:%M')
    except Exception as e:
        print(f"Error converting {dtstr}: {e}")
        return dtstr


with open(input_csv, newline='', encoding='utf-8-sig') as f_in, \
     open(output_csv, 'w', newline='', encoding='utf-8') as f_out:

    reader = csv.DictReader(f_in)
    writer = csv.DictWriter(f_out, fieldnames=output_fields)
    writer.writeheader()

    for row in reader:
        domain = row.get("domain_name", "").strip()
        auction_id = row.get("auction_id", "").strip()
        tld = domain.split('.')[-1] if '.' in domain else ''
        main_part = domain.split('.')[0] if '.' in domain else domain
        end_time_raw = row.get("end_time", "").strip()
        dropdate = cdt_to_utc(end_time_raw) if end_time_raw else ""
        length = len(main_part)
        link = f"https://v2.sav.com/domains/buy/{domain}"
        # link = f"https://www.sav.com/auctions/details/{auction_id}/{domain}"
        is_idn_str = "Yes" if is_idn(domain) else "No"
        source = "Sav Auctions"

        out_row = {
            "DOMAIN": domain,
            "TLD": tld,
            "DROPDATE": dropdate,
            "LENGTH": length,
            "LINK": link,
            "SOURCE": source,
            "APPRAISAL": ""
        }

        writer.writerow(out_row)

print(f"Processed data written to {output_csv}")
