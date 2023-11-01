import json
import time

from github import Github, RateLimitExceededException
from huggingface_hub.repocard import ModelCard

# In[2]:


# load results.json file
with open("usage_transformers_Trainer_transformers.json") as f:
    data = json.load(f)


# In[3]:


model_cnt = 0
gh_cnt = 0
for model in data:
    model_cnt += 1
    for gh in data[model]["usage_repository"]:
        gh_cnt += 1


# In[4]:


model_cnt, gh_cnt


# In[5]:


card = ModelCard.load("microsoft/resnet-50")
print(card.data.license)


# In[6]:


g = Github()
repo = g.get_repo("huggingface/transformers")
license = repo.get_license()
print(license.license.name)


# In[11]:


model_cnt = 0
gh_cnt = 0
no_license_hf_cnt = 0
no_license_gh_cnt = 0
hf_license = []
gh_license = []

for model in data:
    model_cnt += 1
    try:
        card = ModelCard.load(model)
        hf_license.append(card.data.license)
    except:
        print(f"{model} does not have a license")
        no_license_hf_cnt += 1
        hf_license.append(None)
    for gh in data[model]["usage_repository"]:
        gh_cnt += 1
        try:
            try:
                repo = g.get_repo(gh)
                license = repo.get_license()
                gh_license.append(license.license.name)
            except RateLimitExceededException:
                print("RateLimitExceededException")
                time.sleep(3600)
                repo = g.get_repo(gh)
                license = repo.get_license()
                gh_license.append(license.license.name)
        except:
            print(f"{gh} does not have a license")
            gh_license.append(None)
            no_license_gh_cnt += 1


# In[ ]:


import plotly.graph_objects as go

# Your given code here to populate hf_license and gh_license...

# Filter out None elements from hf_license and gh_license
filtered_hf_license = []
filtered_gh_license = []
for hf, gh in zip(hf_license, gh_license):
    if hf is not None and gh is not None:
        filtered_hf_license.append(hf)
        filtered_gh_license.append(gh)

# Get unique licenses and their indices
unique_hf_license = list(set(filtered_hf_license))
unique_gh_license = list(set(filtered_gh_license))

hf_indices = [unique_hf_license.index(lic) for lic in filtered_hf_license]
gh_indices = [unique_gh_license.index(lic) for lic in filtered_gh_license]
gh_indices = [
    i + len(unique_hf_license) for i in gh_indices
]  # offset indices for GH licenses

# Prepare data for the Sankey diagram
labels = unique_hf_license + unique_gh_license
source = hf_indices
target = gh_indices
value = [1] * len(source)  # assuming 1-1 mapping, each connection has a value of 1

# Create the Sankey diagram
fig = go.Figure(
    data=[
        go.Sankey(
            node=dict(
                pad=15, thickness=20, line=dict(color="black", width=0.5), label=labels
            ),
            link=dict(source=source, target=target, value=value),
        )
    ]
)

fig.update_layout(title_text="HF License to GH License Mapping", font_size=10)
fig.show()


# In[ ]:


# In[ ]:
