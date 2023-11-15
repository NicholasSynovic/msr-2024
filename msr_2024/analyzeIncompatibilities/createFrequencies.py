import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re
import json
import sys
import ast

# Load data from hf_gh_licenses.json
df = pd.read_excel("../../../repo_license_downstream_hf_no_filter.xlsx")

# Load data from the GH JSON file as text
with open("all_gh_licenses.json", 'r', encoding='utf-8') as f:
    GH_data = f.read()

# Attempt to load the JSON data as a Python dictionary
try:
    GH_license_dict = json.loads(GH_data)
except json.JSONDecodeError as e:
    # If decoding fails, set the value to None
    print(f"Error decoding 'all_gh_licenses.json': {e}")
    exit()


aliases = {
    "bsd-new": "bsd-3-clause",
    "bsd-modified": "bsd-3-clause",
    "bsd-simplified": "bsd-2-clause",
}

# known relationships from HF to GH licenses
knownMapping = { 
    "apache-2.0": ["bsd-3-clause", "agpl-3.0", "cc0-1.0", "mit", "gpl-3.0", "no license", "apache-2.0", "cc-by-sa-4.0", 'proprietary-license', 'python'],
    "mit": ["mit", "no license", "apache-2.0", "cc-by-sa-4.0", 'proprietary-license', 'cc-by-4.0', 'cc-by-nc-4.0'],
    "bigscience-bloom-rail-1.0": ["apache-2.0", "bigscience-bloom-rail-1.0"],
    "cc-by-4.0": ["no license", 'cc-by-4.0'],
    "afl-3.0": ["no license"],
    "gpl-3.0": ["gpl-3.0", "no license", 'lgpl-3.0', 'agpl-3.0 WITH agpl-generic-additional-terms', 'cc-by-sa-2.5', 'gpl-2.0', 'gpl-3.0-plus', 'cc-by-4.0', 'cc-by-sa-4.0', 'cc-by-nc-sa-4.0', 'cc0-1.0', 'apache-2.0', 'cecill-c', 'bsd-3-clause', 'mit', 'cc-by-nc-4.0', 'gpl-1.0-plus', 'gpl-2.0-plus', 'proprietary-license'],
    "gpl-2.0": ["gpl-2.0", "no license", "gpl-3.0", 'mpl-2.0', 'mit'],
    "cc-by-nc-sa-4.0": ["no license"],
    "cc-by-nc-4.0": ["no license"],
    "no license": ["mit", "gpl-3.0", "no license", "apache-2.0", 'cc-by-sa-4.0', 'proprietary-license', 'cc-by-nc-4.0', 'cc-by-nc-sa-4.0', 'cc-by-4.0'],
    "agpl-3.0":["agpl-3.0"],
    "bsd-3-clause":["bsd-3-clause"],
    'cc0-1.0':['cc0-1.0'],
    'cc-by-sa-4.0':['cc-by-sa-4.0'],
    'bsd-2-clause':["bsd-2-clause"],
    'mpl-2.0':[],
    'mit-0':['mit-0'],
    'lgpl-3.0':['no license', 'lgpl-3.0', 'lgpl-3.0-plus', 'other-permissive', 'gpl-3.0'],
    'lgpl-2.1':['gpl-1.0-plus', 'lgpl-2.1'],
    'epl-2.0':['epl-2.0'],
    'isc':[],
    'wtfpl':[],
    'upl-1.0':[],
    'bsd-3-clause-clear':[],
    'bsl-1.0':[],
    'osl-3.0':[]
}
allHFlicenses = list(knownMapping.keys()) 
unkownMappings = {} # this will be filled in with the unknown mappings from HF to GH licenses, and printed out at the end of the script

# this maps HF licenses to INCOMPATIBLE GH licenses as relevent to the sankey diagram (more incompatibilities are present, but only certain ones are relevent to the trained PTM only sankey diagram)
incompatibleMapping = { 
    "apache-2.0": [],
    "mit": [],
    "bigscience-bloom-rail-1.0": ["apache-2.0"],
    "cc-by-4.0": [],
    "afl-3.0": [],
    "gpl-3.0": ["no license", 'cc-by-sa-2.5', 'gpl-2.0', 'gpl-3.0-plus', 'cc-by-4.0', 'cc-by-sa-4.0', 'cc-by-nc-sa-4.0', 'cc0-1.0', 'apache-2.0', 'cecill-c', 'bsd-3-clause', 'mit', 'cc-by-nc-4.0', 'gpl-1.0-plus', 'gpl-2.0-plus', 'proprietary-license'],
    "gpl-2.0": ["no license", "gpl-3.0"],
    "agpl-3.0": ["no license"],
    "cc-by-nc-sa-4.0": ["no license"],
    "cc-by-nc-4.0": [],
    "no license": [],
    "bsd-3-clause": [],
    'mpl-2.0': ["mit"],
    'mit-0': [],
    'lgpl-3.0': ['no license', 'other-permissive'],
    'lgpl-3.0-plus': ['no license', 'other-permissive'],
    'lgpl-2.1': [],
    'cc0-1.0': [],
    'cc-by-sa-4.0': [],
    'bsd-2-clause': [],
    'epl-2.0': [],
    
}


# license type maping of HG licenses
licenseTypeMapping = {
    "Permissive": ["apache-2.0", "mit", "bsd-3-clause", 'bsd-2-clause', 'mit-0', 'other-permissive', 'python'],
    "Weak Copyleft": ['mpl-2.0', 'cecill-c', 'epl-2.0', 'lgpl-2.1', 'lgpl-2.0', 'lgpl-3.0', 'lgpl-3.0-plus'],
    "Strong Copyleft": ["gpl-3.0", "cc-by-sa-4.0", "agpl-3.0", "gpl-2.0", 'cc-by-sa-2.5', 'gpl-2.0', 'gpl-3.0-plus', 'cc-by-nc-sa-4.0', 'gpl-1.0-plus', 'gpl-2.0-plus', 'agpl-3.0 WITH agpl-generic-additional-terms'],
    "No License": ["no license"],
    "Public Domain": ["cc0-1.0", 'cc-by-4.0', 'cc-by-nc-4.0'],
    "Proprietary License": ["proprietary-license"],
}
licenseTypes = list(licenseTypeMapping.keys())

# Create a function to extract the repository name from a GitHub URL so all_gh_licenses.json can be queried
def extract_repo_name(url):
    # Unescape forward slashes
    url = url.replace(r"\/", "/")
    
    # Use regular expression to extract repo name
    match = re.search(r"github\.com\/([^\/]+\/[^\/]+)$", url)
    
    if match:
        return match.group(1)
    else:
        return None

incompatibilityFrequencies = [0, 0, 0, 0, 0, 0]
totalFrequencies = [0, 0, 0, 0, 0, 0]
other_count = 0
unkownrelations = 0
gh_repos_not_found = []
no_gh_repo_cnt = 0
for j, row in df.iloc[1:].iterrows():  # Starting from the second row to exclude column titles
    # display count
    counter_str = f"\rProcessed {j}/{df.shape[0]-1} relations"
    sys.stdout.write(counter_str)
    sys.stdout.flush()
    
    # begin analysis
    if(not pd.notna(row['license'])):
        hf_license = "no license"
    else:
        dictionary_value = ast.literal_eval(row['license'])
        hf_license = dictionary_value["key"]
    if(not pd.notna(row['github_url'])):
        no_gh_repo_cnt += 1
        continue    
    gh_repo_name = extract_repo_name(row['github_url'])
    if gh_repo_name not in GH_license_dict.keys():
        gh_repos_not_found.append(gh_repo_name)
        continue
    gh_license = GH_license_dict[gh_repo_name]
    
    if type(gh_license) is type(None):
        gh_license = ["no license"]
    if gh_license is None or not gh_license:
        for l in gh_license:
            if pd.notna(l):
                gh_license = l
    if not pd.notna(hf_license) or hf_license == "unlicense":
        hf_license = "no license"
        
    if hf_license=="other" or hf_license=='unknown-license-reference' or hf_license=='warranty-disclaimer' or hf_license=='generic-cla' or hf_license=='commercial-license':
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
        if(l=="other" or l=="unlicense" or l=='unknown-license-reference' or l=='warranty-disclaimer' or l=='generic-cla' or l=='commercial-license'):
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
print("unkown relations", unkownrelations)
print("unkown relations", 100*unkownrelations/(df.shape[0]-1))
print("no gh repo count: ", no_gh_repo_cnt) # 0.0000000
print("GH repos not found: ", set(gh_repos_not_found))
print("unkown mappings HF->GH: ", unkownMappings)
# Create an array of indices for the license types
indices = np.arange(len(licenseTypes))

# Set the width of the bars
bar_width = 0.4

# Create a horizontal bar chart for incompatibility frequencies
plt.barh(indices, incompatibilityFrequencies, bar_width, color="darkred", label="Number of Incompatibilities")

# Create a horizontal bar chart for total frequencies
plt.barh(indices + bar_width, totalFrequencies, bar_width, color="lightblue", label="Total Licenses")

# Add labels and title
plt.xlabel("Frequencies")
plt.ylabel("GH License Type")
plt.title("GH License Types vs. License Incompatibility Frequencies Relative to Total Frequency of GH License Type")

# Display the chart with a legend
plt.yticks(indices + bar_width / 2, licenseTypes)  # Set the y-tick labels
plt.legend()

for i, (total, incompatibility) in enumerate(zip(totalFrequencies, incompatibilityFrequencies)):
    plt.text(total, i + bar_width / 2, str(total), va="center")
    plt.text(incompatibility, i - bar_width / 2, str(incompatibility), va="center")

plt.show()