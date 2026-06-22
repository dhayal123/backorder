import os
import csv
import glob
from collections import defaultdict

folder_path = '/Users/dhayalmani/Downloads/Data/backorder/'

preferred_patterns = [
    'processed_closeouts-*.csv',
    'processed_Namecheap_a.csv',
    'processed_Dropping_Domains*.csv',
    'processed_Dropcatch_a.csv',
    'processed_Dynadot_a.csv',
    'processed_dynadot*.csv',
    'processed_gd_auctions_export_*.csv',
    'processed_namesilo_export.csv',
    'processed_sedo_expiring-domains-auctions*.csv',
    'processed_name_expiring_domains*.csv',
    'processed_Namejet.csv',
    'processed_Namejet_a.csv',   
    'processed_sav.csv',
    'Processedautomatticlist.csv',
    'Processedbluehostlist.csv',
    'Processednetworksolutionslist.csv',
    'Processedoneandoneinternetlist.csv',
]

headers = ["DOMAIN", "TLD", "DROPDATE", "LENGTH", "LINK", "SOURCE", "TYPE", "APPRAISAL"]

output_file = os.path.join(folder_path, 'blueorgreenbackorder.csv')
duplicates_file = os.path.join(folder_path, 'Duplicates.csv')

ordered_files = []
for pattern in preferred_patterns:
    matching = glob.glob(os.path.join(folder_path, pattern))
    ordered_files.extend(sorted(matching))

all_rows = []
records_per_file = {}
files_processed = 0
files_failed = 0

# Step 1: combine all rows from all files
for infile in ordered_files:
    try:
        with open(infile, newline='', encoding='utf-8-sig') as fin:
            reader = csv.DictReader(fin)
            rows_in_file = 0

            for row in reader:
                normalized_row = {
                    "DOMAIN": (row.get("DOMAIN") or "").strip(),
                    "TLD": (row.get("TLD") or "").strip(),
                    "DROPDATE": (row.get("DROPDATE") or "").strip(),
                    "LENGTH": (row.get("LENGTH") or "").strip(),
                    "LINK": (row.get("LINK") or "").strip(),
                    "SOURCE": (row.get("SOURCE") or "").strip(),
                    "TYPE": (row.get("TYPE") or "").strip(),
                    "APPRAISAL":(row.get("APPRAISAL") or "").strip(),
                }

                if normalized_row["DOMAIN"]:
                    normalized_row["_domain_key"] = normalized_row["DOMAIN"].lower()
                    normalized_row["_source_file"] = os.path.basename(infile)
                    all_rows.append(normalized_row)
                    rows_in_file += 1

            records_per_file[os.path.basename(infile)] = rows_in_file
            files_processed += 1

    except Exception as e:
        print(f"Failed to process: {infile} ({e})")
        files_failed += 1

# Step 2: group by domain
grouped = defaultdict(list)
for row in all_rows:
    grouped[row["_domain_key"]].append(row)

# Step 3: split unique vs duplicates
unique_rows = []
duplicate_rows = []

for domain_key, rows in grouped.items():
    unique_rows.append(rows[0])          # keep first occurrence
    if len(rows) > 1:
        duplicate_rows.extend(rows[1:])  # remaining occurrences go to duplicates

# Step 4: write unique output
with open(output_file, 'w', newline='', encoding='utf-8-sig') as fout:
    writer = csv.DictWriter(fout, fieldnames=headers, extrasaction='ignore')
    writer.writeheader()
    for row in unique_rows:
        writer.writerow(row)

# Step 5: write duplicates output
with open(duplicates_file, 'w', newline='', encoding='utf-8-sig') as df:
    dup_writer = csv.DictWriter(df, fieldnames=headers, extrasaction='ignore')
    dup_writer.writeheader()
    for row in duplicate_rows:
        dup_writer.writerow(row)

print(f"Total files processed: {files_processed}")
print(f"Total files failed: {files_failed}")
print("Number of records processed from each file:")
for fname, count in records_per_file.items():
    print(f"  {fname}: {count}")

print(f"Total combined input rows: {len(all_rows)}")
print(f"Total unique records in output file ({os.path.basename(output_file)}): {len(unique_rows)}")
print(f"Total duplicate records in '{os.path.basename(duplicates_file)}': {len(duplicate_rows)}")

if len(all_rows) == len(unique_rows) + len(duplicate_rows):
    print("Record count check passed: combined input records match unique + duplicates.")
else:
    print("Record count WARNING: combined input does NOT match unique + duplicates.")