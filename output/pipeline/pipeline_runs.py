import requests
import pandas as pd
import base64

# Azure DevOps credentials
organization = ""
pat = ""

# API URL for projects
projects_url = f"https://dev.azure.com/{organization}/_apis/projects?api-version=7.1-preview.4"

# Authentication headers
auth = base64.b64encode(f":{pat}".encode()).decode()
headers = {
    "Authorization": f"Basic {auth}",
    "Content-Type": "application/json"
}

# Get all projects
response = requests.get(projects_url, headers=headers)

if response.status_code != 200:
    print("Failed to fetch projects:", response.status_code, response.text)
    exit()
    
data = response.json()
projects = pd.DataFrame(data["value"])[["id", "name"]]


# Rename the columns to be more readable
projects.columns = ["ProjectId", "ProjectName"]

# Method to call pipelines API for a given project
def get_pipelines(org, project, headers):
    url = f"https://dev.azure.com/{org}/{project}/_apis/pipelines?api-version=7.1"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch pipelines for '{project}':", response.status_code, response.text)
        return []
    return response.json().get('value', [])

def get_pipeline_runs(org, project, pipeline_id, pipeline_name, headers):
    url = f"https://dev.azure.com/{org}/{project}/_apis/pipelines/{pipeline_id}/runs?api-version=7.1"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch runs for pipeline '{pipeline_name}':", response.status_code, response.text)
        return []

    runs = response.json().get('value', [])
    
    rows = []
    for run in runs:

        rows.append({
            "ProjectName": project,
            "PipelineIdInOrg": pipeline_id,
            "PipelineName": run.get("name"),
            "PipelineRunId": run.get("pipeline")["id"],
            "RunName": run.get("pipeline")["name"],
            "Result": run.get("result"),
            "RunState": run.get("state"),
            "RunRevision": run.get("pipeline")["revision"],
            "CreatedDate": run.get("createdDate"),
            "FinishedDate": run.get("finishedDate"),
        })
    return rows


all_runs = []
for project in projects["ProjectName"]:
    pipelines = get_pipelines(organization, project, headers)
    for pipeline in pipelines:
        pipeline_id = pipeline["id"]
        pipeline_name = pipeline["name"]
        all_runs.extend(get_pipeline_runs(organization, project, pipeline_id, pipeline_name, headers))


pipeline_runs_df = pd.DataFrame(all_runs)
pipeline_runs_df
print(pipeline_runs_df.head())