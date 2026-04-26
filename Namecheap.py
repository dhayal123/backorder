import os
import csv
import glob
from datetime import datetime
from zoneinfo import ZoneInfo

def is_idn(domain):
    """Return True if domain contains non-ASCII characters (IDN), else False."""
    return any(ord(c) > 127 for c in domain)

def count_csv_rows(filepath):
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)  # Skip header row
        return sum(1 for row in reader)

def format_dropdate(dropdate):
    """
    Convert ISO UTC time (e.g., '2025-10-03T13:00:00.000Z') to 'MMM/DD/YY HH:MM' in US/Eastern.
    """
    dropdate = dropdate.strip()
    # Remove milliseconds and Z if present
    if dropdate.endswith("Z"):
        dropdate = dropdate[:-1]
    if '.' in dropdate:
        dropdate = dropdate.split('.')[0]
    try:
        dt_utc = datetime.strptime(dropdate, "%Y-%m-%dT%H:%M:%S")
        dt_et = dt_utc.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("America/New_York"))
        return dt_et.strftime("%b/%d/%y %H:%M")
    except ValueError:
        print(f"Unrecognized format: '{dropdate}'")
        return dropdate


def process_namecheap_closeouts(infile, outfile):
    output_fields = ["DOMAIN", "TLD", "DROPDATE", "LENGTH", "LINK", "SOURCE", "TYPE", "APPRAISAL"]

    with open(infile, newline='', encoding='utf-8-sig') as f_in:
        reader = csv.DictReader(f_in)
        rows = [row for row in reader]  # DictReader skips header

    with open(outfile, 'w', newline='', encoding='utf-8') as f_out:
        writer = csv.DictWriter(f_out, fieldnames=output_fields)
        writer.writeheader()
        for row in rows:
            row = {k.strip(): v for k, v in row.items()}
            domain_name = row["name"]
            domain_parts = domain_name.split('.')
            main_part = domain_parts[0] if domain_parts else domain_name
            tld = domain_parts[-1] if len(domain_parts) > 1 else ""
            length = len(main_part)
            dropdate = format_dropdate(row["end_date"])
            link = row["permalink"]
            is_idn_str = "Yes" if is_idn(domain_name) else "No"
            source = "Namecheap"

            out_row = {
                "DOMAIN": domain_name,
                "TLD": tld,
                "DROPDATE": dropdate,
                "LENGTH": length,
                "LINK": link,
                "SOURCE": source,
                "TYPE": "Namecheap backorder",
                "APPRAISAL": ""
            }
            writer.writerow(out_row)
    # Print number of records
    input_count = count_csv_rows(infile)
    output_count = count_csv_rows(outfile)
    print(f'Total records in input file: {input_count}')
    print(f'Total records in output file: {output_count}')

folder_path = '/Users/dhayalmani/Downloads/Data/backorder/'
pattern = os.path.join(folder_path, 'closeouts*.csv')
csv_files = glob.glob(pattern)

for infile in csv_files:
    outfile = os.path.join(folder_path, 'processed_' + os.path.basename(infile))
    process_namecheap_closeouts(infile, outfile)
    print(f'Processed {infile} → {outfile}')
