import csv

input_csv = "/Users/dhayalmani/Downloads/Data/backorder/alist.csv"
output_csv = "/Users/dhayalmani/Downloads/Data/backorder/processed_Namejet_a.csv"

output_fields = ["DOMAIN", "TLD", "DROPDATE", "LENGTH", "LINK", "SOURCE", "APPRAISAL", "TYPE"]

def is_idn(domain):
    return any(ord(c) > 127 for c in domain)

def get_fuzzy(row, key_words):
    for key in row:
        # Remove spaces and compare lower-case for fuzzy matching
        if any(word.replace(' ', '').lower() in key.replace(' ', '').lower() for word in key_words):
            return row[key].strip()
    return ""

with open(input_csv, newline='', encoding='utf-8-sig') as f_in:
    lines = list(f_in)
    # Skip first 2 lines
    lines = lines[2:]
    reader = csv.DictReader(lines)
    headers = reader.fieldnames
    #print(f"Detected headers: {headers}")  # Debug: print headers for validation
    
    with open(output_csv, 'w', newline='', encoding='utf-8') as f_out:
        writer = csv.DictWriter(f_out, fieldnames=output_fields)
        writer.writeheader()
        for row in reader:
            domain = get_fuzzy(row, ["Domain name", "Domain"])
            tld = domain.split('.')[-1] if '.' in domain else ''
            main_part = domain.split('.')[0] if '.' in domain else domain
            auction_end_raw = get_fuzzy(row, ["Auction end date", "End date"])
            dropdate = f"{auction_end_raw} 16:00" if auction_end_raw else ""
            length = len(main_part)
            link = f"https://namejet.com/store/basic.action?dom={domain}"
            is_idn_str = "Yes" if is_idn(domain) else "No"
            source = "Namejet Auctions"
            appraisal = "NA"

            # For debugging: print field values if dropdate is blank
            if not auction_end_raw:
                print(f"Row with missing auction end date: {row}")

            out_row = {
                "DOMAIN": domain,
                "TLD": tld,
                "DROPDATE": dropdate,
                "LENGTH": length,
                "LINK": link,
                "SOURCE": source,
                "APPRAISAL": appraisal,
                "TYPE": "Namejet auction"
            }
            writer.writerow(out_row)

print(f"Processed data written to {output_csv}")
