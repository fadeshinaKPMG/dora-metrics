import base64
import requests
import pandas as pd

ORGANIZATION = "DigitalFactoryOrganisation"
PAT = "4XfMeCrdBmD7CDFKEbfNMwUdoIgAJSWqjYAh0xNBa9nnCCZCAKVgJQQJ99CDACAAAAAm7ZkMAAASAZDO3o9R"

auth = base64.b64encode(f":{PAT}".encode()).decode()
HEADERS = {
    "Authorization": f"Basic {auth}",
    "Content-Type": "application/json"
}


def get_projects():
    url = f"https://dev.azure.com/{ORGANIZATION}/_apis/projects?api-version=7.1-preview.4"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print("Failed to fetch projects:", response.status_code, response.text)
        return []
    return response.json().get("value", [])


def get_pipelines(project):
    url = f"https://dev.azure.com/{ORGANIZATION}/{project}/_apis/pipelines?api-version=7.1"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to fetch pipelines for '{project}':", response.status_code, response.text)
        return []
    return response.json().get("value", [])


def get_pipeline_runs(project, pipeline_id, pipeline_name):
    url = f"https://dev.azure.com/{ORGANIZATION}/{project}/_apis/pipelines/{pipeline_id}/runs?api-version=7.1"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to fetch runs for pipeline '{pipeline_name}':", response.status_code, response.text)
        return []
    runs = response.json().get("value", [])
    rows = []
    for run in runs:
        rows.append({
            "ProjectName": project,
            "PipelineId": pipeline_id,
            "PipelineName": pipeline_name,
            "RunId": run.get("id"),
            "RunName": run.get("name"),
            "Result": run.get("result"),
            "CreatedDate": run.get("createdDate"),
            "FinishedDate": run.get("finishedDate"),
        })
    return rows


def fetch_all_pipeline_runs():
    projects = get_projects()
    all_runs = []
    for project in projects:
        project_name = project["name"]
        pipelines = get_pipelines(project_name)
        for pipeline in pipelines:
            all_runs.extend(get_pipeline_runs(project_name, pipeline["id"], pipeline["name"]))
    df = pd.DataFrame(all_runs)
    if not df.empty:
        df["CreatedDate"] = pd.to_datetime(df["CreatedDate"])
        df["FinishedDate"] = pd.to_datetime(df["FinishedDate"])
    return df
