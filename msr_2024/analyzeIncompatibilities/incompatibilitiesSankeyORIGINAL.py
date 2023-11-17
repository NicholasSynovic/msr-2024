import pandas as pd
import plotly.graph_objects as go
import re
import json
import sys

# licenses in sankey 'other' due to being less than the filter count
df = pd.read_csv('hf_other.csv', header=None)
hf_other = df.values.tolist()[0]
df = pd.read_csv('gh_other.csv', header=None)
gh_other = df.values.tolist()[0]

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

SankeyRelations = {}
""" Sankey Relations
{
    hf_license1: {
        gh_license1: {
            count: number
            color: rgba
        },
        ...
    },
    ...
}
"""
opacity = 0.025
red =  f"rgba(255,0,0,{opacity})"
blue = f"rgba(0,0,255,{opacity})"
grey = f"rgba(110,110,110,{opacity+.01})"
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
    gh_licenses = GH_license_dict[gh_repo_name]
    if type(gh_licenses) is type(None):
        gh_licenses = ["no license"]
    
    # process current HF Licenses 
    # to filter out 'other', srt 'no license', 
    # and process found aliases
    if gh_licenses is None or not gh_licenses:
        for l in gh_licenses:
            if pd.notna(l):
                gh_licenses = l
    if not pd.notna(hf_license) or hf_license == "unlicense":
        hf_license = "no license"
    elif hf_license=="other" or hf_license=='unknown' or hf_license=='unknown-license-reference' or hf_license=='warranty-disclaimer' or hf_license=='generic-cla' or hf_license=='commercial-license' or hf_license=='other-permissive' or hf_license=='other-copyleft':
        hf_license = "other"
    elif hf_license in aliases.keys():
        hf_license = aliases[hf_license]
    
    # check if HF license is filtered to other by the set other count
    hf_license_alt = hf_license
    if(hf_license in hf_other):
        hf_license_alt = "other"
    
    # process data for Sankey Diagram
    # first need to see if the current HF license has been added as a source yet
    if(hf_license_alt not in SankeyRelations.keys()):
        SankeyRelations[hf_license_alt] = dict()
    for l in gh_licenses:
        color = blue
        # process current GH license to filter 'other', set 
        # 'no license', process found aliases, and set color path
        # for better displaying on diagram
        if(hf_license == "other"):
            color = grey
        if(l=="unlicense"):
            l = "no license"
        if(l=="other" or l=='unknown' or l=='unknown-license-reference' or l=='warranty-disclaimer' or l=='generic-cla' or l=='commercial-license' or l=='other-permissive' or l=='other-copyleft'):
            color = grey
            l = "other"
        if(l in aliases.keys()):
            l = aliases[l]
        if(l != "other" and hf_license != "other" and l not in knownMapping[hf_license]): 
            color = grey
            
        if(color != grey and l in incompatibleMapping[hf_license]):
            color = red
            
        if(l in gh_other):
            l = "other"
            
        # if(color == grey or l=="no license" or hf_license=="no license"):
        #     continue
        # Now need to see if the current GH license has been added as a sink yet
        if(l not in SankeyRelations[hf_license_alt].keys()):
            SankeyRelations[hf_license_alt][l] = {"count":0, "color":color}
                
        SankeyRelations[hf_license_alt][l]["count"] += 1
        

# process SankeyRelations to display the Sankey Diagram
allLicenses = [] #initialized here so they appear at the top of the Sankey
sourceIDXs = []
targetIDXs = []
colors = []
counts = []

for hf_l in SankeyRelations.keys():
    source_i = len(allLicenses)
    allLicenses.append(hf_l)
    for gh_l in SankeyRelations[hf_l].keys():
        target_i = len(allLicenses)
        allLicenses.append(gh_l)
        sourceIDXs.append(source_i)
        targetIDXs.append(target_i)
        colors.append(SankeyRelations[hf_l][gh_l]["color"])
        counts.append(SankeyRelations[hf_l][gh_l]["count"])
        



# Set up the Sankey diagram
fig = go.Figure(data=[go.Sankey(
    arrangement="snap",
    node=dict(
        pad=70,
        thickness=25,
        line=dict(color='black', width=0.6),
        label=allLicenses,
        # x=x_pos
    ),
    link=dict(
        source=sourceIDXs,
        target=targetIDXs,
        color=colors,
        value=counts,
    )
)])

# Customize layout
fig.update_layout(title_text="HF to GH License Compatibilities", font_size=30)
fig.update_yaxes(ticklabelposition = "outside")
# Show the figure
fig.show()