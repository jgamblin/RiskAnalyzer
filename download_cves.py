import requests
import pandas as pd
import json
import csv
import random
import os
import time
import glob
import numpy as np

# URL to download the NVD CVE dataset
url = "http://nvd.handsonhacking.org/nvd.jsonl"
local_filename = 'nvd.jsonl'

# Check if the file exists and is under 24 hours old
if os.path.exists(local_filename):
    file_age = time.time() - os.path.getmtime(local_filename)
    if file_age < 86400:  # 24 hours in seconds
        print("Using existing dataset (under 24 hours old).")
    else:
        print("Dataset is older than 24 hours. Downloading a new copy...")
        response = requests.get(url)
        with open(local_filename, 'wb') as f:
            f.write(response.content)
        print("Download complete.")
else:
    print("Downloading dataset...")
    response = requests.get(url)
    with open(local_filename, 'wb') as f:
        f.write(response.content)
    print("Download complete.")

def get_nested_value(entry, keys, default='Missing_Data'):
    try:
        for key in keys:
            entry = entry[key]
        return entry
    except (KeyError, IndexError):
        return default

def clean_description(description):
    # Remove commas and any other characters that might cause issues
    description = description.replace(',', '').replace('\n', ' ').replace('\r', ' ').replace('"', '')
    # Drop descriptions with over 200 words
    if len(description.split()) > 200:
        return ''
    return description

row_accumulator = []
for filename in glob.glob('nvd.jsonl'):
    with open(filename, 'r', encoding='utf-8') as f:
        nvd_data = json.load(f)
        for entry in nvd_data:
            new_row = {
                'CVE': get_nested_value(entry, ['cve', 'id']),
                'Published': get_nested_value(entry, ['cve', 'published']),
                'CVSS3_BaseScore': get_nested_value(entry, ['cve', 'metrics', 'cvssMetricV30', 0, 'cvssData', 'baseScore'], '0.0'),
                'CVSS31_BaseScore': get_nested_value(entry, ['cve', 'metrics', 'cvssMetricV31', 0, 'cvssData', 'baseScore'], '0.0'),
                'CWE': get_nested_value(entry, ['cve', 'weaknesses', 0, 'description', 0, 'value']),
                'Description': clean_description(get_nested_value(entry, ['cve', 'descriptions', 0, 'value'], '')),
                'Assigner': get_nested_value(entry, ['cve', 'sourceIdentifier']),
                'Tag': get_nested_value(entry, ['cve', 'cveTags', 0, 'tags'], np.nan),
                'Status': get_nested_value(entry, ['cve', 'vulnStatus'], '')
            }
            if new_row['Description']:  # Only add rows with valid descriptions
                row_accumulator.append(new_row)

nvd = pd.DataFrame(row_accumulator)
nvd = nvd[~nvd.Status.str.contains('Rejected')]
nvd['Published'] = pd.to_datetime(nvd['Published'])
nvd = nvd[nvd['Published'] >= '2022-01-01']
nvd = nvd.sort_values(by=['Published'])
nvd = nvd.reset_index(drop=True)
nvd['CVSS3_BaseScore'] = pd.to_numeric(nvd['CVSS3_BaseScore'])
nvd['CVSS31_BaseScore'] = pd.to_numeric(nvd['CVSS31_BaseScore'])
nvd['CVSS3_BaseScore'] = nvd['CVSS3_BaseScore'].replace(0, np.nan)
nvd['CVSS31_BaseScore'] = nvd['CVSS31_BaseScore'].replace(0, np.nan)

# Combine CVSS3_BaseScore and CVSS31_BaseScore, keeping CVSS31_BaseScore if both exist
nvd['CVSS3_BaseScore'] = nvd['CVSS31_BaseScore'].combine_first(nvd['CVSS3_BaseScore'])

# Drop the CVSS31_BaseScore column as it's now combined into CVSS3_BaseScore
nvd = nvd.drop(columns=['CVSS31_BaseScore'])

# Filter CVEs
print("Filtering CVEs...")
filtered_cves = nvd[
    (nvd['CVSS3_BaseScore'] >= 1.0) &
    (~nvd['CWE'].str.startswith('NVD')) &
    (nvd['CWE'] != '')
]

# Check if there are enough CVEs to sample from
if len(filtered_cves) < 500:
    raise ValueError("Not enough CVEs to sample 500. Only found {}".format(len(filtered_cves)))

# Select 500 random CVEs
print("Selecting 500 random CVEs...")
selected_cves = filtered_cves.sample(n=500)

# Save to CSV
print("Saving to CSV...")
selected_cves.to_csv('cves.csv', columns=['CVE', 'Description', 'CVSS3_BaseScore', 'CWE'], index=False)

print("Process complete. CSV file created as 'cves.csv'.")
