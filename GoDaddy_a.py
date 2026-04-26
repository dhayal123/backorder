import csv
import glob

input_pattern = "/Users/dhayalmani/Downloads/Data/backorder/gd_auctions_export*.csv"
output_csv = "/Users/dhayalmani/Downloads/Data/backorder/processed_Godaddy.csv"

output_fields = ["DOMAIN", "TLD", "DROPDATE", "LENGTH", "LINK", "SOURCE", "APPRAISAL", "TYPE"]

def is_idn(domain):
    return any(ord(c) > 127 for c in domain)

all_rows = []

for input_csv in glob.glob(input_pattern):
    with open(input_csv, newline='', encoding='utf-8-sig') as f_in:
        reader = csv.DictReader(f_in)
        for row in reader:
            domain = row.get("Domain Name", "").strip()
            item_id = row.get("ItemID", "").strip()
            tld = domain.split('.')[-1] if '.' in domain else ''
            main_part = domain.split('.')[0] if '.' in domain else domain
            dropdate = row.get("Auction End Time", "").strip()
            length = len(main_part)
            link = f"https://ie.godaddy.com/domain-auctions/{main_part}-{tld}-{item_id}"
            is_idn_str = "Yes" if is_idn(domain) else "No"
            source = "Godaddy Auctions"
            appraisal = row.get("Estimated Value", "").strip()

            out_row = {
                "DOMAIN": domain,
                "TLD": tld,
                "DROPDATE": dropdate,
                "LENGTH": length,
                "LINK": link,
                "SOURCE": source,
                "APPRAISAL": appraisal,
                "TYPE": "Godaddy auction"
            }

            all_rows.append(out_row)
    print(f'Processed {input_csv} → merged output')

with open(output_csv, 'w', newline='', encoding='utf-8') as f_out:
    writer = csv.DictWriter(f_out, fieldnames=output_fields)
    writer.writeheader()
    for row in all_rows:
        writer.writerow(row)

print(f"Final output written to {output_csv} with {len(all_rows)} total rows.")
