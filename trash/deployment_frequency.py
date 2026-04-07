import requests
import base64
import pandas as pd

# ── Auth ──────────────────────────────────────────────────────────────────────
ORGANIZATION = "DigitalFactoryOrganisation"
PAT = "4XfMeCrdBmD7CDFKEbfNMwUdoIgAJSWqjYAh0xNBa9nnCCZCAKVgJQQJ99CDACAAAAAm7ZkMAAASAZDO3o9R"
auth = base64.b64encode(f":{PAT}".encode()).decode()
headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}

# ── Fetch data ────────────────────────────────────────────────────────────────
def get_projects():
    url = f"https://dev.azure.com/{ORGANIZATION}/_apis/projects?api-version=7.1-preview.4"
    r = requests.get(url, headers=headers)
    return r.json().get("value", []) if r.status_code == 200 else []

def get_pipelines(project):
    url = f"https://dev.azure.com/{ORGANIZATION}/{project}/_apis/pipelines?api-version=7.1"
    r = requests.get(url, headers=headers)
    return r.json().get("value", []) if r.status_code == 200 else []

def get_pipeline_runs(project, pipeline_id, pipeline_name):
    url = f"https://dev.azure.com/{ORGANIZATION}/{project}/_apis/pipelines/{pipeline_id}/runs?api-version=7.1"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return []
    rows = []
    for run in r.json().get("value", []):
        rows.append({
            "ProjectName": project,
            "PipelineId": pipeline_id,
            "PipelineName": pipeline_name,
            "Result": run.get("result"),
            "CreatedDate": run.get("createdDate"),
        })
    return rows


all_runs = []
for project in get_projects():
    for pipeline in get_pipelines(project["name"]):
        all_runs.extend(get_pipeline_runs(project["name"], pipeline["id"], pipeline["name"]))

df = pd.DataFrame(all_runs)
df["CreatedDate"] = pd.to_datetime(df["CreatedDate"])

succeeded = df[df["Result"] == "succeeded"].copy()

deployment_frequency = (
    succeeded
    .groupby(["ProjectName", succeeded["CreatedDate"].dt.to_period("M")])
    .size()
    .reset_index(name="DeploymentCount")
)
deployment_frequency.columns = ["ProjectName", "Month", "DeploymentCount"]
deployment_frequency["Month"] = deployment_frequency["Month"].astype(str)

deployment_frequency
