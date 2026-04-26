import os
import csv
import glob
from datetime import datetime

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
    Convert input date strings to 'MMM/DD/YY HH:MM' format.
    Handles ISO8601 ('2025-10-02T16:00:00Z'), 'MM/DD/YYYY', 'MM/DD/YY', etc.
    """
    dropdate = dropdate.strip()
    formats = [
        "%Y-%m-%dT%H:%M:%SZ",     # ISO format, UTC Z
        "%Y-%m-%dT%H:%M:%S",      # ISO format, no Z
        "%Y-%m-%d %H:%M:%S",      # ISO format, space separator
        "%Y-%m-%d",               # ISO date only
        "%m/%d/%Y",               # MM/DD/YYYY
        "%m/%d/%y",               # MM/DD/YY
        "%m-%d-%Y",               # MM-DD-YYYY
        "%m-%d-%y",               # MM-DD-YY
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(dropdate, fmt)
            return dt.strftime("%b/%d/%y %H:%M")
        except ValueError:
            continue
    # If matches ISO + time but with milliseconds/other quirks
    try:
        # Remove fractional seconds if present
        if 'T' in dropdate and '.' in dropdate:
            base = dropdate.split('.')[0]
            if base.endswith('Z'):
                base = base[:-1]
            dt = datetime.strptime(base, "%Y-%m-%dT%H:%M:%S")
            return dt.strftime("%b/%d/%y %H:%M")
    except Exception:
        pass
    print(f"Unrecognized date format: {dropdate}")
    return dropdate  # If unrecognized, return as is


def process_namesilo_export(infile, outfile):
    output_fields = ["DOMAIN", "TLD", "DROPDATE", "LENGTH", "LINK", "SOURCE", "TYPE", "APPRAISAL"]

    with open(infile, newline='', encoding='utf-8-sig') as f_in:
        reader = csv.DictReader(f_in)
        rows = [row for row in reader]  # DictReader automatically skips the first header row

    with open(outfile, 'w', newline='', encoding='utf-8') as f_out:
        writer = csv.DictWriter(f_out, fieldnames=output_fields)
        writer.writeheader()
        for row in rows:
            domain_name = row["Domain"]
            domain_parts = domain_name.split('.')
            main_part = domain_parts[0] if domain_parts else domain_name
            tld = domain_parts[-1] if len(domain_parts) > 1 else ""
            length = len(main_part)
            dropdate = format_dropdate(row["Auction End"])
            link = f"https://www.dynadot.com/domain/search?rscreg=inteldomains&domain={domain_name}"
            is_idn_str = "Yes" if is_idn(domain_name) else "No"
            source = "Namesilo"
            out_row = {
                "DOMAIN": domain_name,
                "TLD": tld,
                "DROPDATE": dropdate,
                "LENGTH": length,
                "LINK": link,
                "SOURCE": source,
                "TYPE": "Namesilo backorder",
                "APPRAISAL": ""
            }
            writer.writerow(out_row)
    # Print number of records
    input_count = count_csv_rows(infile)
    output_count = count_csv_rows(outfile)
    print(f'Total records in input file: {input_count}')
    print(f'Total records in output file: {output_count}')

folder_path = '/Users/dhayalmani/Downloads/Data/backorder/'
pattern = os.path.join(folder_path, 'namesilo_export*.csv')
csv_files = glob.glob(pattern)

for infile in csv_files:
    outfile = os.path.join(folder_path, 'processed_' + os.path.basename(infile))
    process_namesilo_export(infile, outfile)
    print(f'Processed {infile} → {outfile}')
