import os
import csv
import glob
from datetime import datetime
from zoneinfo import ZoneInfo


def is_idn(domain):
    """Return True if domain contains non-ASCII characters (IDN), else False."""
    return any(ord(c) > 127 for c in domain)


def count_csv_rows(filepath):
    """Count data rows in a CSV file (excluding header)."""
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)  # Skip header
        return sum(1 for row in reader)


def format_dropdate(dropdate):
    """
    Convert a 'YYYY-MM-DD HH:MM:SS +00:00' UTC date to 'MMM/DD/YY HH:MM' in US/Eastern.
    """
    dropdate = dropdate.strip()
    try:
        dt_utc = datetime.strptime(dropdate, "%Y-%m-%d %H:%M:%S %z")
        dt_et = dt_utc.astimezone(ZoneInfo("America/New_York"))
        return dt_et.strftime("%b/%d/%y %H:%M")
    except ValueError:
        print(f"Unrecognized format: '{dropdate}'")
        return dropdate


def process_name_file(infile, outfile):
    output_fields = ["DOMAIN", "TLD", "DROPDATE", "LENGTH", "LINK", "SOURCE", "TYPE", "APPRAISAL"]

    with open(infile, newline='', encoding='utf-8-sig') as f_in:
        reader = csv.DictReader(f_in)

        with open(outfile, 'w', encoding='utf-8', newline='') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=output_fields)
            writer.writeheader()

            for row in reader:
                row = {k.strip(): (v.strip() if v else "") for k, v in row.items()}

                domain_name = row.get("domain_name", "")
                tld = row.get("tld", "")
                dropdate = format_dropdate(row.get("expiring_date", ""))
                main_part = domain_name.split('.')[0] if '.' in domain_name else domain_name
                length = len(main_part)
                link = f"https://www.name.com/domain/search/{domain_name}"
                source = "Name"

                out_row = {
                    "DOMAIN": domain_name,
                    "TLD": tld,
                    "DROPDATE": dropdate,
                    "LENGTH": length,
                    "LINK": link,
                    "SOURCE": source,
                    "TYPE": "NAME auction",
                    "APPRAISAL": ""
                }
                writer.writerow(out_row)

    input_count = count_csv_rows(infile)
    output_count = count_csv_rows(outfile)
    print(f"Total records in input file: {input_count}")
    print(f"Total records in output file: {output_count}")


folder_path = '/Users/dhayalmani/Downloads/Data/backorder/'
pattern = os.path.join(folder_path, 'expiring_domains.csv')
csv_files = glob.glob(pattern)

for infile in csv_files:
    outfile = os.path.join(folder_path, 'processed_name_' + os.path.basename(infile))
    process_name_file(infile, outfile)
    print(f"Processed {infile} -> {outfile}")