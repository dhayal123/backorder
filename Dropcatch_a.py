import csv
import glob
import os
import zipfile
import io

zip_pattern = "/Users/dhayalmani/Downloads/Data/backorder/Auction_Domains_AllAuctions*.csv.zip"
csv_pattern = "/Users/dhayalmani/Downloads/Data/backorder/Auction_Domains_AllAuction*.csv"
output_csv = "/Users/dhayalmani/Downloads/Data/backorder/processed_Dropcatch_a.csv"

output_fields = ["DOMAIN", "TLD", "DROPDATE", "LENGTH", "LINK", "SOURCE", "APPRAISAL", "TYPE"]

def is_idn(domain):
    return any(ord(c) > 127 for c in domain)

# Unzip all matching zip files
for zip_file in glob.glob(zip_pattern):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(os.path.dirname(zip_file))
    print(f"Unzipped {zip_file}")

all_rows = []

for csv_file in glob.glob(csv_pattern):
    with open(csv_file, newline='', encoding='utf-8-sig') as f_in:
        lines = list(csv.reader(f_in))
        # Skip first row if it contains the warning
        if lines and "generated every 15 minutes" in lines[0][0]:
            header = lines[1]
            data_rows = lines[2:]
        else:
            header = lines[0]
            data_rows = lines[1:]
        # Convert all rows to comma-separated values (if not already strings)
        data_text = '\n'.join([','.join(row) for row in data_rows])
        reader = csv.DictReader(io.StringIO(data_text), fieldnames=header)
        for row in reader:
            domain = row.get("Domain", "").strip()
            if not domain:
                continue
            tld = domain.split('.')[-1] if '.' in domain else ''
            main_part = domain.split('.')[0] if '.' in domain else domain
            dropdate_raw = row.get("Auction End", "").strip()
            dropdate = f"{dropdate_raw} 19:00 UTC" if dropdate_raw else ""
            length = len(main_part)
            link = f"https://www.dropcatch.com/domain/{domain}"
            is_idn_str = "Yes" if is_idn(domain) else "No"
            source = "DropCatch Auctions"
            appraisal = "NA"
            out_row = {
                "DOMAIN": domain,
                "TLD": tld,
                "DROPDATE": dropdate,
                "LENGTH": length,
                "LINK": link,
                "SOURCE": source,
                "APPRAISAL": appraisal,
                "TYPE": "Dropcatch auction"
            }
            all_rows.append(out_row)
    print(f'Processed {csv_file} → merged output')

if all_rows:
    with open(output_csv, 'w', newline='', encoding='utf-8') as f_out:
        writer = csv.DictWriter(f_out, fieldnames=output_fields)
        writer.writeheader()
        for row in all_rows:
            writer.writerow(row)
    print(f"Final output written to {output_csv} with {len(all_rows)} total rows.")
else:
    print("No rows with domain values found! Check the column headers in your input files.")
