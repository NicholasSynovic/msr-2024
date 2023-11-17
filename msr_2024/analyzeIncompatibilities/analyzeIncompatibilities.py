import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
import json
import sys

# file paths for hf license -> gh license relations
hf_license_to_gh_repo_csv = "mapping.csv"
gh_repo_url_col = 0
hf_license_col = 3

gh_repo_to_gh_license_json = "all_gh_licenses.json"

# Load data from hf_gh_licenses.json
df = pd.read_csv(hf_license_to_gh_repo_csv, header=None)

# Load data from the GH JSON file as text
with open(gh_repo_to_gh_license_json, 'r', encoding='utf-8') as f:
    GH_data = f.read()

# Attempt to load the JSON data as a Python dictionary
try:
    GH_license_dict = json.loads(GH_data)
except json.JSONDecodeError as e:
    # If decoding fails, set the value to None
    print(f"Error decoding {gh_repo_to_gh_license_json}: {e}")
    exit()

# known aliases in analyzed data
aliases = {
    "bsd-new": "bsd-3-clause",
    "bsd-modified": "bsd-3-clause",
    "bsd-simplified": "bsd-2-clause",
    'openrail++':'openrail',
    
}

# known relationships from HF to GH licenses in analyzed data
# these are in no particular order
knownMapping = { 
    "apache-2.0": ["bsd-3-clause", "agpl-3.0", "cc0-1.0", "mit", "gpl-3.0", "no license", "apache-2.0", "cc-by-sa-4.0", 'proprietary-license', 'python', 'cc-by-nc-sa-4.0', 'cecill-c', 'cc-by-4.0', 'cc-by-nc-4.0', 'gpl-1.0-plus', 'gpl-3.0-plus', 'agpl-3.0-plus', 'bsd-2-clause', 'mit-0', 'lgpl-3.0', 'mpl-2.0', 'gpl-2.0'],
    "mit": ["mit", "no license", "apache-2.0", "cc-by-sa-4.0", 'proprietary-license', 'cc-by-4.0', 'cc-by-nc-4.0', 'bsd-3-clause', 'bsd-2-clause', 'agpl-3.0', 'gpl-3.0', 'cc0-1.0', 'gpl-2.0', 'cc-by-nc-sa-4.0', 'mpl-2.0'],
    "bigscience-bloom-rail-1.0": ["apache-2.0", "bigscience-bloom-rail-1.0", 'no license', 'mit', 'gpl-3.0', 'cc-by-sa-4.0', 'cc-by-nc-sa-4.0', 'cc-by-4.0', 'gpl-2.0', 'bsd-3-clause', 'agpl-3.0'],
    "cc-by-4.0": ["no license", 'cc-by-4.0', 'mit', 'bsd-3-clause', 'proprietary-license', 'apache-2.0', 'cc-by-nc-sa-4.0'],
    "afl-3.0": ["no license"],
    "gpl-3.0": ["gpl-3.0", "no license", 'lgpl-3.0', 'agpl-3.0 WITH agpl-generic-additional-terms', 'cc-by-sa-2.5', 'gpl-2.0', 'gpl-3.0-plus', 'cc-by-4.0', 'cc-by-sa-4.0', 'cc-by-nc-sa-4.0', 'cc0-1.0', 'apache-2.0', 'cecill-c', 'bsd-3-clause', 'mit', 'cc-by-nc-4.0', 'gpl-1.0-plus', 'gpl-2.0-plus', 'proprietary-license', 'agpl-3.0', 'cc-by-sa-3.0'],
    "gpl-2.0": ["gpl-2.0", "no license", "gpl-3.0", 'mpl-2.0', 'mit'],
    "cc-by-nc-sa-4.0": ["no license", 'mit', 'apache-2.0', 'cc-by-4.0', 'cc-by-sa-3.0', 'gpl-3.0', 'bsd-3-clause', 'cc0-1.0', 'proprietary-license', 'cecill-c', 'cc-by-nc-sa-4.0', 'json', 'cc-by-nc-nd-4.0', 'cc-by-sa-4.0'],
    "cc-by-nc-4.0": ["no license", 'mit', 'apache-2.0'],
    "no license": ["mit", "gpl-3.0", "no license", "apache-2.0", 'cc-by-sa-4.0', 'proprietary-license', 'cc-by-nc-4.0', 'cc-by-nc-sa-4.0', 'cc-by-4.0'],
    "agpl-3.0":["agpl-3.0", 'mit', 'cc-by-sa-4.0', 'cc-by-nc-sa-4.0', 'cc-by-nc-sa-3.0', 'no license', 'odc-by-1.0', 'apache-2.0'],
    "bsd-3-clause":["bsd-3-clause", 'mit', 'apache-2.0', 'no license', ],
    'cc0-1.0':['cc0-1.0'],
    'cc-by-sa-4.0':['cc-by-sa-4.0',  'gpl-3.0', 'cc-by-sa-3.0','apache-2.0', 'no license', 'mit', 'agpl-3.0', 'bsd-2-clause', 'cc-by-nc-4.0', 'proprietary-license', 'cc-by-nc-sa-4.0', 'cc0-1.0', 'mpl-2.0'],
    'bsd-2-clause':["bsd-2-clause"],
    'mpl-2.0':[],
    'mit-0':['mit-0'],
    'lgpl-3.0':['no license', 'lgpl-3.0', 'lgpl-3.0-plus', 'gpl-3.0'],
    'lgpl-2.1':['gpl-1.0-plus', 'lgpl-2.1'],
    'epl-2.0':['epl-2.0'],
    'isc':[],
    'wtfpl':[],
    'upl-1.0':[],
    'bsd-3-clause-clear':[],
    'bsl-1.0':[],
    'osl-3.0':[],
    'bsd':[], # not a license, counting number of relations (counted 2, not significant) with this instance in data (is the license publisher, not the license) 
    'cc-by-sa-3.0':[],
    'deepfloyd-if-license':[],
    'openrail':['no license', 'proprietary-license', 'cc-by-nc-nd-4.0', 'cc-by-nc-4.0', 'apache-2.0', 'cc0-1.0', 'gpl-3.0', 'gpl-1.0-plus', 'mit', 'bsd-3-clause', 'lgpl-2.1', 'agpl-3.0', 'cecill-c'],
    'bigcode-openrail-m':[],
    'creativeml-openrail-m':['cc-by-nc-4.0', 'cc-by-nc-sa-4.0', 'cc-by-nc-nd-4.0', 'cc0-1.0', 'no license', 'apache-2.0', 'mit', 'apache-2.0 WITH llvm-exception', 'agpl-3.0', 'gpl-3.0', 'bsd-3-clause', 'bsd-2-clause', 'agpl-3.0-plus', 'mit-0', 'gpl-1.0-plus'],
    'bigscience-openrail-m':['mit'],
    'cc':[], # not a license, counting number of relations (counted 1, not significant) with this instance in data (is the license publisher, not the license)
    'lgpl-lr':[],
    'cc-by-nc-sa-3.0':[],
    'cc-by-2.0':[],
    'gpl':[], # not a license, counting number of relations (counted 1, not significant) with this instance in data (is the license publisher, not the license)
    'cc-by-nc-nd-4.0':[]    
}
allHFlicenses = list(knownMapping.keys()) 
unkownMappings = {} # this will be filled in with the unknown mappings from HF to GH licenses, and printed out at the end of the script

# this maps HF licenses to INCOMPATIBLE GH licenses as relevent to the sankey diagram (more incompatibilities are present, but only certain ones are relevent to the trained PTM only sankey diagram)
incompatibleMapping = { 
    "apache-2.0": [],
    "mit": [],
    "bigscience-bloom-rail-1.0": ["apache-2.0", 'mit', 'gpl-3.0', 'cc-by-sa-4.0', 'cc-by-nc-sa-4.0', 'cc-by-4.0', 'gpl-2.0', 'bsd-3-clause', 'agpl-3.0'],
    "cc-by-4.0": ['cc-by-nc-sa-4.0'],
    "afl-3.0": [],
    "gpl-3.0": ["no license", 'cc-by-sa-2.5', 'gpl-2.0', 'gpl-3.0-plus', 'cc-by-4.0', 'cc-by-sa-4.0', 'cc-by-nc-sa-4.0', 'cc0-1.0', 'apache-2.0', 'cecill-c', 'bsd-3-clause', 'mit', 'cc-by-nc-4.0', 'gpl-1.0-plus', 'gpl-2.0-plus', 'proprietary-license', 'cc-by-sa-3.0'],
    "gpl-2.0": ["no license", "gpl-3.0"],
    "agpl-3.0": ["no license", 'mit', 'cc-by-sa-4.0', 'cc-by-nc-sa-4.0', 'cc-by-nc-sa-3.0', 'no license', 'odc-by-1.0', 'apache-2.0'],
    "agpl-3.0-plus": ["no license", 'mit', 'cc-by-sa-4.0', 'cc-by-nc-sa-4.0', 'cc-by-nc-sa-3.0', 'no license', 'odc-by-1.0', 'apache-2.0'],
    "cc-by-nc-sa-4.0": ["no license", 'mit', 'apache-2.0', 'cc-by-4.0', 'cc-by-sa-3.0', 'gpl-3.0', 'bsd-3-clause', 'cc0-1.0', 'proprietary-license', 'cecill-c', 'json', 'cc-by-nc-nd-4.0', 'cc-by-sa-4.0'],
    "cc-by-nc-4.0": ['mit', 'apache-2.0'],
    "no license": [],
    "bsd-3-clause": [],
    'mpl-2.0': ["mit"],
    'mit-0': [],
    'lgpl-3.0': ['no license'],
    'lgpl-3.0-plus': ['no license'],
    'lgpl-2.1': [],
    'cc0-1.0': [],
    'cc-by-sa-4.0': ['cc-by-sa-3.0','apache-2.0', 'no license', 'mit', 'agpl-3.0', 'bsd-2-clause', 'cc-by-nc-4.0', 'proprietary-license', 'cc-by-nc-sa-4.0', 'cc0-1.0', 'mpl-2.0'],
    'bsd-2-clause': [],
    'epl-2.0': [],
    'bigscience-openrail-m':['mit'],
    'openrail': ['apache-2.0', 'cc0-1.0', 'gpl-3.0', 'gpl-1.0-plus', 'mit', 'bsd-3-clause', 'lgpl-2.1', 'agpl-3.0', 'cecill-c'],
    'creativeml-openrail-m':['cc0-1.0', 'no license', 'apache-2.0', 'mit', 'apache-2.0 WITH llvm-exception', 'agpl-3.0', 'gpl-3.0', 'bsd-3-clause', 'bsd-2-clause', 'agpl-3.0-plus', 'mit-0', 'gpl-1.0-plus'],
}


# license type maping of HG licenses
licenseTypeMapping = {
    "Permissive": ["apache-2.0", "mit", "bsd-3-clause", 'bsd-2-clause', 'mit-0', 'python', 'odc-by-1.0', 'json', 'apache-2.0 WITH llvm-exception'],
    "Weak Copyleft": ['mpl-2.0', 'cecill-c', 'epl-2.0', 'lgpl-2.1', 'lgpl-2.0', 'lgpl-3.0', 'lgpl-3.0-plus'],
    "Strong Copyleft": ["gpl-3.0", "cc-by-sa-4.0", "agpl-3.0", 'agpl-3.0-plus', "gpl-2.0", 'cc-by-sa-2.5', 'gpl-2.0', 'gpl-3.0-plus', 'cc-by-nc-sa-4.0', 'cc-by-nc-sa-3.0', 'gpl-1.0-plus', 'gpl-2.0-plus', 'agpl-3.0 WITH agpl-generic-additional-terms', 'cc-by-sa-3.0'],
    "No License": ["no license"],
    "Public Domain": ["cc0-1.0", 'cc-by-4.0', 'cc-by-nc-4.0'],
    "Proprietary License": ["proprietary-license", 'cc-by-nc-nd-4.0'],
}
licenseTypes = list(licenseTypeMapping.keys())

# Create a function to extract the repository name from a GitHub URL so all_gh_licenses.json can be queried with {username}/{repo}
def extract_repo_name(url):
    # Unescape forward slashes
    url = url.replace(r"\/", "/")
    
    # Use regular expression to extract repo name
    match = re.search(r"github\.com[\/:](.+\/.+?)(?:\.git)?$", url)
    
    if match:
        return match.group(1)
    else:
        return None

incompatibilityFrequencies = [0] * len(licenseTypeMapping)
totalFrequencies = [0] * len(licenseTypeMapping)
other_count = 0
unkownrelations = 0
gh_repos_not_found = []
for cnt, row in df.iterrows():
    # display count
    counter_str = f"\rProcessed {cnt}/{df.shape[0]-1} relations"
    sys.stdout.write(counter_str)
    sys.stdout.flush()
    
    # get HF and GH licenses
    if(not pd.notna(row[hf_license_col])):
        hf_license = "no license"
    else:
        hf_license = row[hf_license_col].lower()
    gh_repo_name = extract_repo_name(row[gh_repo_url_col])
    if gh_repo_name not in GH_license_dict.keys():
        gh_repos_not_found.append(gh_repo_name)
        continue
    gh_license = GH_license_dict[gh_repo_name]
    
    # process current GH and HF Licenses
    if type(gh_license) is type(None):
        gh_license = ["no license"]
    if gh_license is None or not gh_license:
        for l in gh_license:
            if pd.notna(l):
                gh_license = l
    if not pd.notna(hf_license) or hf_license == "unlicense":
        hf_license = "no license"
        
    if hf_license=="other" or hf_license=='unknown' or hf_license=='unknown-license-reference' or hf_license=='warranty-disclaimer' or hf_license=='generic-cla' or hf_license=='commercial-license' or hf_license=='other-permissive' or hf_license=='other-copyleft':
        other_count += 1
        continue
    if hf_license in aliases.keys():
        hf_license = aliases[hf_license]
    
    # check if HF license is known
    if(hf_license not in allHFlicenses):
        unkownrelations += 1
        if(hf_license not in unkownMappings.keys()):
            unkownMappings[hf_license] = set()
        (unkownMappings[hf_license].add(l) for l in gh_license)
        continue
    for l in gh_license:
        if(l=="unlicense"):
            l = "no license"
        if(l=="other" or l=='unknown' or l=='unknown-license-reference' or l=='warranty-disclaimer' or l=='generic-cla' or l=='commercial-license' or l=='other-permissive' or l=='other-copyleft'):
            other_count += 1
            continue
        if(l in aliases.keys()):
            l = aliases[l]
        if(l not in knownMapping[hf_license]):
            unkownrelations += 1
            if(hf_license not in unkownMappings.keys()):
                unkownMappings[hf_license] = dict()
                unkownMappings[hf_license][l] = 1
            elif(l not in unkownMappings[hf_license].keys()):
                unkownMappings[hf_license][l] = 1
            else:
                unkownMappings[hf_license][l] += 1
            continue
        
        # same as trained PTM only filter
        incompatible_licenses = incompatibleMapping[hf_license]
        i=0
        try:
            while l not in licenseTypeMapping[licenseTypes[i]]:
                i+=1
            totalFrequencies[i] += 1
            if l in incompatible_licenses:
                incompatibilityFrequencies[i] += 1
        except IndexError:
            print("\nINDEX ERROR")
            print("Index: ", i)
            print("IndexError: ", l)
            exit()
    


# display incompatibility frequencies
print()
print("other count: ", other_count)
print("other percent: ", 100*other_count/(df.shape[0]-1))
print("unkown relations count:", unkownrelations)
print("unkown relations percent:", 100*unkownrelations/(df.shape[0]-1))
print("GH repos not found: ", set(gh_repos_not_found))
print("unkown mappings HF->GH: ", unkownMappings)
# Create an array of indices for the license types
indices = np.arange(len(licenseTypes))

# Set the width of the bars
bar_width = 0.4
label_size = 17
axes_size = 18
title_size = 20


fig, ax = plt.subplots(figsize=(8, 6))  # Adjust the values based on your requirement

# Create a horizontal bar chart for incompatibility frequencies
ax.barh(indices, incompatibilityFrequencies, bar_width, color="darkred", label="Number of Incompatibilities")

# Create a horizontal bar chart for total frequencies
ax.barh(indices + bar_width, totalFrequencies, bar_width, color="lightblue", label="Total Licenses")

# Add labels and title with increased text size
ax.set_xlabel("Frequencies", fontsize=axes_size)
ax.set_ylabel("GH License Type", fontsize=axes_size)
ax.set_title("GH License Types vs. License Incompatibility Frequencies\nRelative to Total Frequency of GH License Type", fontsize=title_size)

# Display the chart with a legend
ax.set_yticks(indices + bar_width / 2)
ax.set_yticklabels(licenseTypes, fontsize=label_size, wrap=True)  # Set the y-tick labels
ax.tick_params(axis='y', labelsize=label_size) # set fontsize for the labels (fontsize=# did not change size when passed as argument on set_yticklabels)
plt.yticks(fontsize=label_size)
plt.xticks(fontsize=label_size)
ax.legend()

for i, (total, incompatibility) in enumerate(zip(totalFrequencies, incompatibilityFrequencies)):
    ax.text(total, i + bar_width, str(total), va="center", fontsize=label_size-1)
    ax.text(incompatibility, i - 0*bar_width, str(incompatibility), va="center", fontsize=label_size-1)

plt.subplots_adjust(left=0.178)
plt.subplots_adjust(right=0.959)

ax.spines['top'].set(visible=None)
ax.spines['right'].set(visible=None)

plt.show()
