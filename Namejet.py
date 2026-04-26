import os
import glob
import csv
from datetime import datetime
from pytz import timezone, UTC

folder = '/Users/dhayalmani/Downloads/Data/backorder/'
output_file = os.path.join(folder, 'Processed_Namejet.csv')

def is_idn(domain):
    return any(ord(char) > 127 for char in domain)

def convert_est_to_utc(date_str):
    # Return blank immediately if input is empty
    if not date_str or not date_str.strip():
        return ""
    est = timezone('US/Eastern')
    formats = [
        "%m/%d/%Y %I:%M:%S %p",    # e.g. 10/14/2025 01:45:00 PM
        "%m/%d/%Y %H:%M:%S",       # e.g. 10/14/2025 13:45:00
        "%m/%d/%Y %H:%M",          # e.g. 10/14/2025 13:45
        "%Y-%m-%d %H:%M:%S",       # e.g. 2025-10-14 13:45:00
        "%Y-%m-%d %H:%M",          # e.g. 2025-10-14 13:45
    ]
    for fmt in formats:
        try:
            dt_local = datetime.strptime(date_str, fmt)
            dt_est = est.localize(dt_local)
            dt_utc = dt_est.astimezone(UTC)
            return dt_utc.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            continue
    print(f"Failed to convert: {date_str}")
    return date_str

def process_csv_file(infile, domain_field, dropdate_field, dropdate_type, skip_lines=2):
    rows = []
    with open(infile, encoding='utf-8-sig') as f:
        for _ in range(skip_lines):
            next(f)
        reader = csv.DictReader(f)
        for row in reader:
            # Lowercase and trim keys for case-insensitive matching
            row_lc = {k.strip().lower(): v for k, v in row.items()}
            domain = row_lc.get(domain_field.lower(), '').strip()
            if not domain:
                continue
            domain_main = domain.split('.')[0] if domain else ''
            tld = domain.split('.')[-1] if '.' in domain else ''
            link = f'https://namejet.com/store/basic.action?dom={domain}'
            is_idn_str = "Yes" if domain and is_idn(domain) else "No"
            source = "Namejet"
            length = len(domain_main)
            dropdate_raw = row_lc.get(dropdate_field.lower(), '').strip()

            # Parse dropdate field
            if dropdate_type == "date_only_with_3pm_est":
                try:
                    date_only = dropdate_raw.split()[0] if dropdate_raw else ''
                    est_dt_str = f"{date_only} 15:00"
                    dropdate = convert_est_to_utc(est_dt_str)
                except Exception:
                    dropdate = dropdate_raw
            elif dropdate_type == "full_est":
                dropdate = convert_est_to_utc(dropdate_raw)
            else:
                dropdate = dropdate_raw

            out_row = {
                "DOMAIN": domain,
                "TLD": tld,
                "DROPDATE": dropdate,
                "LENGTH": length,
                "LINK": link,
                "SOURCE": source,
                "TYPE": "Namejet backorder",
                "APPRAISAL": ""
            }
            rows.append(out_row)
    return rows

all_rows = []

# # File 1: alist.csv (Domain Name, Auction end date, skip 2 lines, add 3PM EST, to UTC)
# alist_path = os.path.join(folder, 'alist.csv')
# if os.path.isfile(alist_path):
#     all_rows += process_csv_file(alist_path, 'Domain Name', 'Auction end date', 'date_only_with_3pm_est', skip_lines=2)
#     print(f'Processed {alist_path} → merged output')

# File 2: preorderstarting*.csv (Domain name, Release date, skip 2 lines, full datetime EST to UTC)
for preorder_file in glob.glob(os.path.join(folder, 'preorderstarting*.csv')):
    all_rows += process_csv_file(preorder_file, 'Domain name', 'Release date', 'full_est', skip_lines=2)
    print(f'Processed {preorder_file} → merged output')

# File 3: deletinglist.csv (Domain name, Join By Date (ET), skip 1 line/header, full datetime EST to UTC)
deletinglist_path = os.path.join(folder, 'deletinglist.csv')
if os.path.isfile(deletinglist_path):
    all_rows += process_csv_file(deletinglist_path, 'Domain name', 'Join By Date (ET)', 'full_est', skip_lines=1)
    print(f'Processed {deletinglist_path} → merged output')

# File 4: allexpiring_list.csv (Domain name, Auction end date, skip 2 lines, add 3PM EST, to UTC)
allexpiring_path = os.path.join(folder, 'allexpiring_list.csv')
if os.path.isfile(allexpiring_path):
    all_rows += process_csv_file(allexpiring_path, 'Domain name', 'Auction end date', 'date_only_with_3pm_est', skip_lines=2)
    print(f'Processed {allexpiring_path} → merged output')

# Write combined output
output_fields = ["DOMAIN", "TLD", "DROPDATE", "LENGTH", "LINK", "SOURCE", "TYPE", "APPRAISAL"]
with open(output_file, 'w', newline='', encoding='utf-8') as f_out:
    writer = csv.DictWriter(f_out, fieldnames=output_fields)
    writer.writeheader()
    for row in all_rows:
        writer.writerow(row)

print(f'Final combined output written to {output_file} ({len(all_rows)} rows).')
