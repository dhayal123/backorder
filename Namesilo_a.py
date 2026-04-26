import csv

input_csv = "/Users/dhayalmani/Downloads/Data/backorder/namesilo_export (1).csv"
output_csv = "/Users/dhayalmani/Downloads/Data/backorder/processed_Namesilo_a.csv"

output_fields = ["DOMAIN", "TLD", "DROPDATE", "LENGTH", "LINK", "SOURCE", "APPRAISAL", "TYPE"]

def is_idn(domain):
    return any(ord(c) > 127 for c in domain)

with open(input_csv, newline='', encoding='utf-8-sig') as f_in, \
     open(output_csv, 'w', newline='', encoding='utf-8') as f_out:
    
    reader = csv.DictReader(f_in)
    writer = csv.DictWriter(f_out, fieldnames=output_fields)
    writer.writeheader()

    for row in reader:
        domain = row.get("Domain", "").strip()
        tld = domain.split('.')[-1] if '.' in domain else ''
        main_part = domain.split('.')[0] if '.' in domain else domain
        dropdate = row.get("Auction End", "").strip()
        length = len(main_part)
        link = row.get("Url", "").strip()
        is_idn_str = "Yes" if is_idn(domain) else "No"
        source = "Namesilo Auctions"

        out_row = {
            "DOMAIN": domain,
            "TLD": tld,
            "DROPDATE": dropdate,
            "LENGTH": length,
            "LINK": link,
            "SOURCE": source,
            "APPRAISAL": "",
            "TYPE": "Namesilo auction"
        }

        writer.writerow(out_row)

print(f"Processed data written to {output_csv}")
