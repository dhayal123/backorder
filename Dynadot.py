import os
import csv
import glob
from datetime import datetime


def is_idn(domain):
    return any(ord(char) > 127 for char in domain)


def extract_date(end_time):
    return end_time.split()[0] if end_time else ""


def count_csv_rows(filepath):
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)  # Skip header
        return sum(1 for row in reader)


def format_dropdate(dropdate):
    """
    Convert 'YYYY/MM/DD HH:MM Timezone' to 'MMM/DD/YY HH:MM'
    """
    try:
        parts = dropdate.strip().split()
        if len(parts) < 2:
            return dropdate
        date_part = parts[0]
        time_part = parts[1]
        dt_str = f"{date_part} {time_part}"
        dt = datetime.strptime(dt_str, "%Y/%m/%d %H:%M")
        return dt.strftime("%b/%d/%y %H:%M")
    except ValueError:
        print(f"Unrecognized format: '{dropdate}'")
        return dropdate


def process_dynadot_closeout(infile, outfile):
    output_fields = ["DOMAIN", "TLD", "DROPDATE", "LENGTH", "LINK", "SOURCE", "TYPE", "APPRAISAL"]

    with open(infile, newline='', encoding='utf-8-sig') as f_in:
        reader = csv.DictReader(f_in)

        with open(outfile, 'w', newline='', encoding='utf-8') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=output_fields)
            writer.writeheader()

            for row in reader:
                row = {k.strip(): v for k, v in row.items()}
                domain_name = row['Domain']
                domain_parts = domain_name.split('.')
                main_part = domain_parts[0]
                tld = domain_parts[-1]
                end_time = row.get('End Time', '').strip()
                dropdate = format_dropdate(end_time)
                length = len(main_part)
                link = f"https://www.dynadot.com/domain/search?rscreg=inteldomains&domain={domain_name}"
                is_idn_str = "Yes" if is_idn(domain_name) else "No"
                source = "Dynadot"
                appraisal = row.get('Dynappraisal', '').strip()

                out_row = {
                    "DOMAIN": domain_name,
                    "TLD": tld,
                    "DROPDATE": dropdate,
                    "LENGTH": length,
                    "LINK": link,
                    "SOURCE": source,
                    "TYPE": "Dynadot backorder",
                    "APPRAISAL": appraisal
                }
                writer.writerow(out_row)

    input_count = count_csv_rows(infile)
    output_count = count_csv_rows(outfile)
    print(f'Total records in input file: {input_count}')
    print(f'Total records in output file: {output_count}')


folder_path = '/Users/dhayalmani/Downloads/Data/backorder/'
pattern = os.path.join(folder_path, 'closeout.csv')
csv_files = glob.glob(pattern)

for infile in csv_files:
    outfile = os.path.join(folder_path, 'processed_dynadot_' + os.path.basename(infile))
    process_dynadot_closeout(infile, outfile)
    print(f'Processed {infile} → {outfile}')