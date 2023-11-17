import pandas as pd
import plotly.graph_objects as go
import re
import json
import sys

# licenses in sankey 'other' due to count being <=3
hf_other = ['bigcode-openrail-m', 'bigscience-bloom-rail-1.0', 'cc-by-4.0', 'bsd', 'afl-3.0', 'gpl-3.0', 'cc-by-sa-3.0', 'agpl-3.0', 'deepfloyd-if-license', 'bigscience-openrail-m', 'cc', 'lgpl-lr', 'cc-by-nc-sa-3.0', 'cc-by-2.0', 'gpl', 'cc-by-nc-nd-4.0', ]
gh_other = ['bsd-2-clause', 'amazon-sl', 'free-unknown', 'commons-clause', 'gpl-2.0', 'apache-2.0 WITH llvm-exception', 'gpl-2.0 WITH classpath-exception-2.0', 'cddl-1.1', 'boost-1.0', 'cc-by-sa-3.0', 'stable-diffusion-2022-08-22', 'mpl-2.0', 'gpl-1.0-plus', 'gpl-2.0-plus', 'philippe-de-muyter', 'gpl-3.0 WITH gpl-generic-additional-terms', 'gpl-3.0-plus', 'agpl-3.0-plus', 'cc-by-3.0-us', 'apple-excl', 'lgpl-2.1', 'epl-2.0', 'historical', 'secret-labs-2011', 'psf-3.7.2', 'python', 'bsl-1.1', 'cc-by-3.0', 'cc-by-sa-2.0', 'public-domain', 'cc-by-nc-nd-4.0', 'upl-1.0', 'bsd-2-clause-views', 'mit-0', 'lgpl-3.0', 'us-govt-public-domain', 'lgpl-2.0-plus', 'hippocratic-1.2', 'hippocratic-1.1', 'gcc-exception-3.1', 'fsf-unlimited', 'bsd-source-code', 'issl-2018', 'protobuf', 'bsd-ack', 'gpl-2.0-plus WITH libtool-exception-2.0', 'unicode', 'intel-bsd', 'uoi-ncsa', 'minpack', 'zlib', 'isc', 'bsd-3-clause-open-mpi', 'naist-2003', 'hs-regexp', 'gpl-3.0-plus WITH gcc-exception-3.1', 'lgpl-2.1-plus', 'x11', 'libpng', 'clear-bsd', 'mit-old-style', 'lgpl-3.0-plus', 'x11-fsf', 'x11-xconsortium', 'gfdl-1.1-plus', 'cc-by-nc-sa-2.0', 'cc-by-nc-sa-3.0', 'elastic-license-v2', 'unixcrypt', 'cc-by-nc-2.0', 'gtpl-v3', 'cc-by-nc-3.0', 'openssl-ssleay', 'w3c-03-bsd-license', 'bsd-zero', 'x11-lucent', 'python-cwi', 'cc-by-2.5', 'zpl-2.1', 'mit-old-style-no-advert', 'json', 'odc-by-1.0', 'unknown-spdx', 'agpl-3.0 WITH agpl-generic-additional-terms', 'bsd-original', 'bsd-original-uc', 'ncgl-uk-2.0', 'cc-by-2.0', 'ibmpl-1.0', 'dco-1.1', 'mpl-1.0', 'robert-hubley', 'x11-tiff', 'wtfpl-2.0', 'mpl-1.1', 'ofl-1.1', 'cdla-permissive-2.0', 'mongodb-sspl-1.0', 'cecill-b', 'cecill-b-en', 'bsd-plus-patent', 'arm-llvm-sga', 'freetype-patent', 'anti-capitalist-1.4', 'freetype', 'apple-attribution-1997', 'cc-by-sa-2.5', 'cdla-permissive-1.0', 'llama-license-2023', 'sata', 'gpl-1.0', 'libpbm', 'bsd-1-clause', 'bsd-plus-mod-notice', 'eupl-1.2', 'cc-by-nc-sa-2.5', ]

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

unkownrelations = 0
allLicenses = []
sourceIDXs = []
targetIDXs = []
sankeySourceIdxs = {}
sankeyTargetIdxs = {}
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
    gh_license = GH_license_dict[gh_repo_name]
    
    # process current GH and HF Licenses 
    # to filter out 'other', process 'no license', 
    # and process found aliases
    if type(gh_license) is type(None):
        gh_license = ["no license"]
    if gh_license is None or not gh_license:
        for l in gh_license:
            if pd.notna(l):
                gh_license = l
    if not pd.notna(hf_license) or hf_license == "unlicense":
        hf_license = "no license"
        
    if hf_license=="other" or hf_license=='unknown' or hf_license=='unknown-license-reference' or hf_license=='warranty-disclaimer' or hf_license=='generic-cla' or hf_license=='commercial-license' or hf_license=='other-permissive' or hf_license=='other-copyleft':
        hf_license = "other"
    if hf_license in aliases.keys():
        hf_license = aliases[hf_license]
    
    # check if HF license is known
    if(hf_license not in allHFlicenses):
        unkownrelations += 1
        if(hf_license not in unkownMappings.keys()):
            unkownMappings[hf_license] = set()
        (unkownMappings[hf_license].add(l) for l in gh_license)
    if(hf_license in hf_other):
        hf_license = "other"
    
    # process data for Sankey Diagram
    # first need to see if the current HF license has been added as a source yet
    if(hf_license not in sankeySourceIdxs.keys()):
        sankeySourceIdxs[hf_license] = len(allLicenses)
        allLicenses.append(hf_license)
    sourceIDX = sankeySourceIdxs[hf_license]
    for l in gh_license:
        # process current GH license to filter out 'other,
        # process 'no license', and process found aliases
        if(l=="unlicense"):
            l = "no license"
        if(l=="other" or l=='unknown' or l=='unknown-license-reference' or l=='warranty-disclaimer' or l=='generic-cla' or l=='commercial-license' or l=='other-permissive' or l=='other-copyleft'):
            l = "other"
        if(l in aliases.keys()):
            l = aliases[l]
        if(l != "other" and hf_license != "other" and l not in knownMapping[hf_license]):
            unkownrelations += 1
            if(hf_license not in unkownMappings.keys()):
                unkownMappings[hf_license] = dict()
                unkownMappings[hf_license][l] = 1
            elif(l not in unkownMappings[hf_license].keys()):
                unkownMappings[hf_license][l] = 1
            else:
                unkownMappings[hf_license][l] += 1
        if(l in gh_other):
            l = "other"
        # Now need to see if the current GH license has been added as a sink yet
        if(l not in sankeyTargetIdxs.keys()):
            sankeyTargetIdxs[l] = len(allLicenses)
            allLicenses.append(l)
        sinkIDX = sankeyTargetIdxs[l]
        
        sourceIDXs.append(sourceIDX)
        targetIDXs.append(sinkIDX)
        
        # same as trained PTM only filter
        # incompatible_licenses = incompatibleMapping[hf_license]
        # i=0
        # try:
        #     while l not in licenseTypeMapping[licenseTypes[i]]:
        #         i+=1
        #     totalFrequencies[i] += 1
        #     if l in incompatible_licenses:
        #         incompatibilityFrequencies[i] += 1
        # except IndexError:
        #     print("\nINDEX ERROR")
        #     print("Index: ", i)
        #     print("IndexError: ", l)
        #     exit()
    


# display incompatibility frequencies
print()
print("unkown relations count:", unkownrelations)
print("unkown relations percent:", 100*unkownrelations/(df.shape[0]-1))
print("unkown mappings HF->GH: ", unkownMappings)

# Set up the Sankey diagram
fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color='black', width=0.5),
        label=allLicenses
    ),
    link=dict(
        source=sourceIDXs,
        target=targetIDXs,
        value=([1]*len(sourceIDXs)),
    )
)])

# Customize layout
fig.update_layout(title_text="Basic Sankey Diagram", font_size=10)

# Show the figure
fig.show()