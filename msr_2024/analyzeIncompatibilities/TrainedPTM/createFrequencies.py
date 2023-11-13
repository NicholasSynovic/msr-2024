import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

""" this works for the trained PTM only dataset: hf_gh_licenses.json """

# Load your data from hf_gh_licenses.json
df = pd.read_json("hf_gh_licenses.json").T

allGHLicenses = ["bsd-3-clause", "agpl-3.0", "cc0-1.0", "mit", "gpl-3.0", "no license", "apache-2.0", "cc-by-sa-4.0"]
# gh licenses ive need to check: bsd-3-clause, cc0-1.0, mit, no license, apache-2.0, cc-by-sa-4.0 
# this maps HF licenses to INCOMPATIBLE GH licenses
# incompatibleMapping = {
#     "apache-2.0": [],
#     "mit": [],
#     "bigscience-bloom-rail-1.0": [allGHLicenses[0-5], allGHLicenses[6-8]], # incompatible with all GH licenses, since RAIL puts limitations on use of the work and derived works 
#     "cc-by-4.0": [],
#     "afl-3.0": ["gpl-3.0", "agpl-3.0"],
#     "gpl-3.0": [allGHLicenses[0], allGHLicenses[2:4], allGHLicenses[5:8]], # only compatible with itself and agpl-3.0
#     "cc-by-nc-sa-4.0": [allGHLicenses[0], allGHLicenses[2:4], allGHLicenses[5:8]], # incompatible with all GH expect for gpl-3.0 and agpl-3.0 by extension
#     "cc-by-nc-4.0": ["gpl-3.0"],
#     "no license": [] # HF's "no license" is compatible with all GH licenses
# }

# this maps HF licenses to INCOMPATIBLE GH licenses as relevent to the sankey diagram (more incompatibilities are present, but only certain ones are relevent to the trained PTM only sankey diagram)
incompatibleMapping = { 
    "apache-2.0": [],
    "mit": [],
    "bigscience-bloom-rail-1.0": ["apache-2.0"],
    "cc-by-4.0": [],
    "afl-3.0": [],
    "gpl-3.0": ["no license"],
    "cc-by-nc-sa-4.0": ["no license"],
    "cc-by-nc-4.0": [],
    "no license": []
}


# license type maping of HG licenses
licenseTypeMapping = {
    "Permissive": ["apache-2.0", "mit", "bsd-3-clause"],
    "Weak Copyleft": [],
    "Strong Copyleft": ["gpl-3.0", "cc-by-sa-4.0", "agpl-3.0"],
    "No License": ["no license"],
    "Public Domain": ["cc0-1.0"],
}
licenseTypes = list(licenseTypeMapping.keys())
incompatibilityFrequencies = [0, 0, 0, 0, 0]
totalFrequencies = [0, 0, 0, 0, 0]
print(licenseTypes)
for _, row in df.iterrows():
    hf_license = row["HF License"]
    gh_license = row["GH License"]
    
    if not pd.notna(gh_license):
        gh_license = "no license"
    if not pd.notna(hf_license):
        hf_license = "no license"
        
    if hf_license=="other" or gh_license=="other":
        continue
    
    incompatible_licenses = incompatibleMapping[hf_license]
    i=0
    while gh_license not in licenseTypeMapping[licenseTypes[i]]:
        i+=1
    totalFrequencies[i] += 1
    if gh_license in incompatible_licenses:
        incompatibilityFrequencies[i] += 1

# display incompatibility frequencies


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

# /////////////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////////

# Replace NaN values with "No License" in both "HF License" and "GH License" columns
df["HF License"].fillna("No License", inplace=True)
df["GH License"].fillna("No License", inplace=True)

# Create frequency counts for HF licenses
hf_license_counts = df["HF License"].value_counts()

# Create frequency counts for GH licenses
gh_license_counts = df["GH License"].value_counts()

# Set up the figure and axes for subplots
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Create a bar plot for HF licenses
hf_bar_plot = sns.barplot(x=hf_license_counts.values, y=hf_license_counts.index, ax=axes[0])
sns.barplot(x=hf_license_counts.values, y=hf_license_counts.index, ax=axes[0])
axes[0].set_title("HF License Frequency")
axes[0].set_xlabel("Count")
axes[0].set_ylabel("License")

# Add number labels at the end of each bar for HF licenses
for i, count in enumerate(hf_license_counts.values):
    hf_bar_plot.text(count, i, str(count), va="center")

# Create a bar plot for GH licenses
gh_bar_plot = sns.barplot(x=gh_license_counts.values, y=gh_license_counts.index, ax=axes[1])
sns.barplot(x=gh_license_counts.values, y=gh_license_counts.index, ax=axes[1])
axes[1].set_title("GH License Frequency")
axes[1].set_xlabel("Count")
axes[1].set_ylabel("License")

# Add number labels at the end of each bar for GH licenses
for i, count in enumerate(gh_license_counts.values):
    gh_bar_plot.text(count, i, str(count), va="center")

# Adjust layout to prevent overlap
plt.tight_layout()

# Display the plots
plt.show()
