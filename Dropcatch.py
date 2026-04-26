import csv
import os
import glob
from datetime import datetime
import zipfile

folder = '/Users/dhayalmani/Downloads/Data/backorder/'  # Change as needed
pattern = os.path.join(folder, 'Dropping_Domains_All*.csv.zip')

for zip_path in glob.glob(pattern):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(folder)

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
    Convert dropdate from CSV (various formats) to 'Oct/02/25 13:44'
    """
    dropdate = dropdate.strip()
    # Try possible formats, in most common order
    for fmt in ["%m/%d/%Y", "%m/%d/%y", "%m-%d-%Y", "%m-%d-%y", "%Y-%m-%d"]:
        try:
            dt = datetime.strptime(dropdate, fmt)
            return dt.strftime("%b/%d/%y") + " 13:44"
        except ValueError:
            continue
    print(f"Unrecognized date format: {dropdate}")
    return dropdate  # Could not parse


def process_dropcatch_domains(file_in, file_out):
    dropcatch_fields = ["Domain", "TLD", "Type", "Drop Date"]
    output_fields = ["DOMAIN", "TLD", "DROPDATE", "LENGTH", "LINK", "SOURCE", "TYPE", "APPRAISAL"]

    with open(file_in, newline='', encoding='utf-8') as f_in:
        reader = csv.DictReader(f_in)
        rows = [row for row in reader]

    with open(file_out, 'w', encoding='utf-8-sig', newline='') as f_out:
        writer = csv.DictWriter(f_out, fieldnames=output_fields)
        writer.writeheader()
        for row in rows:
            row = {k.strip(): v for k, v in row.items()}
            domain = row['Domain']
            tld = row['TLD']
            dropdate = format_dropdate(row['Drop Date'])
            domain_main = domain.split('.')[0] if '.' in domain else domain
            length = len(domain_main)
            link = f"https://www.dropcatch.com/domain/{domain}"
            is_idn_str = "Yes" if is_idn(domain) else "No"
            source = "Dropcatch"
            output_row = {
                "DOMAIN": domain,
                "TLD": tld,
                "DROPDATE": dropdate,
                "LENGTH": length,
                "LINK": link,
                "SOURCE": source,
                "TYPE": "Dropcatch backorder",
                "APPRAISAL": ""
            }
            writer.writerow(output_row)

    # Record counts
    input_count = count_csv_rows(file_in)
    output_count = count_csv_rows(file_out)
    print(f'Total records in input file: {input_count}')
    print(f'Total records in output file: {output_count}')

folder_path = '/Users/dhayalmani/Downloads/Data/backorder/'
pattern = os.path.join(folder_path, 'Dropping_Domains_All*.csv')
csv_files = glob.glob(pattern)

for infile in csv_files:
    outfile = os.path.join(folder_path, 'processed_' + os.path.basename(infile))
    process_dropcatch_domains(infile, outfile)
    print(f'Processed {infile} → {outfile}')
