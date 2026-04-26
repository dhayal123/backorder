import os
import csv
from datetime import datetime
from pytz import timezone, UTC

folder = '/Users/dhayalmani/Downloads/Data/backorder/'
combined_outfile = os.path.join(folder, 'processed_Dynadot_a.csv')

def is_idn(domain):
    return any(ord(c) > 127 for c in domain)


def format_end_time_to_utc(end_time):
    """
    Convert 'YYYY/MM/DD HH:MM America/New_York' to 'YYYY-MM-DD HH:MM' UTC.
    """
    try:
        parts = end_time.strip().split()
        if len(parts) < 3:
            return end_time
        date_part, time_part, tz_part = parts
        dt_local = datetime.strptime(f"{date_part} {time_part}", "%Y/%m/%d %H:%M")
        ny_tz = timezone("America/New_York")
        dt_ny = ny_tz.localize(dt_local)
        dt_utc = dt_ny.astimezone(UTC)
        return dt_utc.strftime("%Y-%m-%d %H:%M")
    except Exception:
        print(f"Unrecognized format: '{end_time}'")
        return end_time

def process_auction_file(infile, output_rows, source):
    with open(infile, newline='', encoding='utf-8-sig') as f_in:
        reader = csv.DictReader(f_in)
        for row in reader:
            row = {k.strip(): v.strip() for k, v in row.items()}
            domain_name = row.get('Domain', '')
            main_part = domain_name.split('.')[0] if '.' in domain_name else domain_name
            tld = domain_name.split('.')[-1] if '.' in domain_name else ''
            is_idn_str = "Yes" if is_idn(domain_name) else "No"
            length = len(main_part)
            end_time = row.get('End Time', '')
            auction_end_time_utc = format_end_time_to_utc(end_time)
            appraisal_value = row.get('Appraisal', '')
            link = f"https://www.dynadot.com/domain/search?rscreg=inteldomains&domain={domain_name}"
            source = "Dynadot Auctions"
            out_row = {
                "DOMAIN": domain_name,
                "TLD": tld,
                "DROPDATE": auction_end_time_utc,
                "APPRAISAL": appraisal_value,
                "LENGTH": length,
                "SOURCE": source,
                "LINK": link,
                "TYPE": "Dynadot auction"
            }
            output_rows.append(out_row)

all_rows = []

# Process auctions.csv
auctions_file = os.path.join(folder, 'auctions.csv')
if os.path.isfile(auctions_file):
    process_auction_file(auctions_file, all_rows, "Dynadot_auctions")
    print(f'Processed {auctions_file} → merged output')

# Process lastchance_auction.csv
lastchance_file = os.path.join(folder, 'lastchance_auction.csv')
if os.path.isfile(lastchance_file):
    process_auction_file(lastchance_file, all_rows, "Dynadot_lastchance_auction")
    print(f'Processed {lastchance_file} → merged output')

# Write combined CSV
output_fields = ["DOMAIN", "TLD", "DROPDATE", "LENGTH", "LINK", "SOURCE", "APPRAISAL", "TYPE"]

with open(combined_outfile, 'w', newline='', encoding='utf-8') as f_out:
    writer = csv.DictWriter(f_out, fieldnames=output_fields)
    writer.writeheader()
    for row in all_rows:
        writer.writerow(row)

print(f'Final output written to {combined_outfile} with {len(all_rows)} total rows.')
