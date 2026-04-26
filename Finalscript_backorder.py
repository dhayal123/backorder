import subprocess

scripts = [
    '/Users/dhayalmani/Downloads/IntelDomains Code/backorder/Namecheap.py',
    '/Users/dhayalmani/Downloads/IntelDomains Code/backorder/Namecheap_a.py',
    '/Users/dhayalmani/Downloads/IntelDomains Code/backorder/Dropcatch.py',
    '/Users/dhayalmani/Downloads/IntelDomains Code/backorder/Dropcatch_a.py',
    '/Users/dhayalmani/Downloads/IntelDomains Code/backorder/Dynadot.py',
    '/Users/dhayalmani/Downloads/IntelDomains Code/backorder/Dynadot_a.py',
    '/Users/dhayalmani/Downloads/IntelDomains Code/backorder/Godaddy_a.py',
    '/Users/dhayalmani/Downloads/IntelDomains Code/backorder/Name.py',
    '/Users/dhayalmani/Downloads/IntelDomains Code/backorder/Namesilo.py',
    '/Users/dhayalmani/Downloads/IntelDomains Code/backorder/Namesilo_a.py',
    '/Users/dhayalmani/Downloads/IntelDomains Code/backorder/Sedo.py',
    '/Users/dhayalmani/Downloads/IntelDomains Code/backorder/Namejet.py',   
    '/Users/dhayalmani/Downloads/IntelDomains Code/backorder/Namejet_a.py',
    '/Users/dhayalmani/Downloads/IntelDomains Code/backorder/Sav_a.py',
    '/Users/dhayalmani/Downloads/IntelDomains Code/backorder/Automaticlist.py',
    '/Users/dhayalmani/Downloads/IntelDomains Code/backorder/Bluehost.py',
    '/Users/dhayalmani/Downloads/IntelDomains Code/backorder/Networksolutions.py',
    '/Users/dhayalmani/Downloads/IntelDomains Code/backorder/Oneandoneinternetlist.py',
    '/Users/dhayalmani/Downloads/IntelDomains Code/backorder/Finaloutput.py',
    '/Users/dhayalmani/Downloads/IntelDomains Code/backorder/wordsegment_backorder.py'
    # Add more script file names as needed
]

for script in scripts:
    print(f"Running {script} ...")
    result = subprocess.run(['/Library/Frameworks/Python.framework/Versions/3.10/bin/python3', script], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"Error in {script}:\n{result.stderr}")
        break  # Optional: stop on first failure
    print(f"{script} finished.\n")
print("All scripts executed.")
