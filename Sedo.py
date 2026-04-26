import os
import csv
import glob
from datetime import datetime


def is_idn(domain):
    """Return True if domain contains non-ASCII characters (IDN), else False."""
    return any(ord(c) > 127 for c in domain)


def count_csv_rows(filepath):
    with open(filepath, newline='', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        next(reader, None)  # Skip header row
        return sum(1 for row in reader)


def format_dropdate(dropdate):
    """
    Convert input date strings to 'MMM/DD/YY HH:MM' format.
    Handles ISO8601 ('2025-10-02T16:00:00Z'), 'MM/DD/YYYY', 'MM/DD/YY', etc.
    """
    dropdate = (dropdate or "").strip()
    formats = [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%m/%d/%y",
        "%m-%d-%Y",
        "%m-%d-%y",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(dropdate, fmt)
            return dt.strftime("%b/%d/%y %H:%M")
        except ValueError:
            continue

    try:
        if 'T' in dropdate and '.' in dropdate:
            base = dropdate.split('.')[0]
            if base.endswith('Z'):
                base = base[:-1]
            dt = datetime.strptime(base, "%Y-%m-%dT%H:%M:%S")
            return dt.strftime("%b/%d/%y %H:%M")
    except Exception:
        pass

    print(f"Unrecognized date format: {dropdate}")
    return dropdate


def process_sedo_auctions(infile, outfile):
    output_fields = ["DOMAIN", "TLD", "DROPDATE", "LENGTH", "LINK", "SOURCE", "APPRAISAL", "TYPE"]

    with open(infile, newline='', encoding='utf-8-sig') as f_in, \
         open(outfile, 'w', newline='', encoding='utf-8-sig') as f_out:

        reader = csv.DictReader(f_in)
        writer = csv.DictWriter(f_out, fieldnames=output_fields)
        writer.writeheader()

        for row in reader:
            row = {k.strip(): (v.strip() if v else "") for k, v in row.items()}

            domain_name = row.get("Domain Ace", "")
            tld = row.get("Tld", "")
            dropdate = format_dropdate(row.get("Auction End Date", ""))

            main_part = domain_name.split('.')[0] if '.' in domain_name else domain_name
            length = len(main_part)
            link = f"https://sedo.com/checkdomainoffer.php?language=us&domain={domain_name}&&campaignId=335550"
            source = "Sedo"

            out_row = {
                "DOMAIN": domain_name,
                "TLD": tld,
                "DROPDATE": dropdate,
                "LENGTH": length,
                "LINK": link,
                "SOURCE": source,
                "APPRAISAL": "",
                "TYPE": "Sedo auction"
            }
            writer.writerow(out_row)

    input_count = count_csv_rows(infile)
    output_count = count_csv_rows(outfile)
    print(f'Total records in input file: {input_count}')
    print(f'Total records in output file: {output_count}')


folder_path = '/Users/dhayalmani/Downloads/Data/backorder/'
pattern = os.path.join(folder_path, 'expiring-domains-auctions*.csv')
csv_files = glob.glob(pattern)

for infile in csv_files:
    outfile = os.path.join(folder_path, 'processed_sedo_' + os.path.basename(infile))
    process_sedo_auctions(infile, outfile)
    print(f'Processed {infile} -> {outfile}')