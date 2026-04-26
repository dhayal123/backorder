import csv

input_csv = "/Users/dhayalmani/Downloads/Data/backorder/Namecheap_Market_Sales.csv"
output_csv = "/Users/dhayalmani/Downloads/Data/backorder/processed_Namecheap_a.csv"

output_fields = ["DOMAIN", "TLD", "DROPDATE", "LENGTH", "LINK", "SOURCE", "TYPE", "APPRAISAL"]

def is_idn(domain):
    return any(ord(c) > 127 for c in domain)

with open(input_csv, newline='', encoding='utf-8-sig') as f_in, \
     open(output_csv, 'w', newline='', encoding='utf-8') as f_out:
    
    reader = csv.DictReader(f_in)
    writer = csv.DictWriter(f_out, fieldnames=output_fields)
    writer.writeheader()

    for row in reader:
        domain = row.get("name", "").strip()
        tld = domain.split('.')[-1] if '.' in domain else ''
        main_part = domain.split('.')[0] if '.' in domain else domain
        dropdate = row.get("endDate", "").strip()
        length = len(main_part)
        link = row.get("url", "").strip()
        is_idn_str = "Yes" if is_idn(domain) else "No"
        source = "Namecheap Auctions"
        appraisal = row.get("goValue","").strip()
        out_row = {
            "DOMAIN": domain,
            "TLD": tld,
            "DROPDATE": dropdate,
            "LENGTH": length,
            "LINK": link,
            "SOURCE": source,
            "TYPE": "Namecheap auction",
            "APPRAISAL":appraisal
        }

        writer.writerow(out_row)

print(f"Processed data written to {output_csv}")
