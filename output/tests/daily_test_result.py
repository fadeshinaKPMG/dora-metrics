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

def get_daily_test_results(org, project, pipeline_name, headers):
    url = f" https://analytics.dev.azure.com/{org}/{project}/_odata/v4.0-preview/TestResultsDaily?$filter=Pipeline/{pipeline_name}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch daily test results for pipeline '{pipeline_name}':", response.status_code, response.text)
        return []

    runs = response.json().get('value', [])
    print(runs)
    return runs
    rows = []
    # for run in runs:
    #     rows.append({
    #         "ProjectName": project,
    #         "PipelineId": pipeline_id,
    #         "PipelineName": pipeline_name,
    #         "RunId": run.get("id")
    #     })
    # return rows


daily_test_results = []
for project in projects["ProjectName"]:
    pipelines = get_pipelines(organization, project, headers)
    for pipeline in pipelines:
        pipeline_id = pipeline["id"]
        pipeline_name = pipeline["name"]
        daily_test_results.extend(get_daily_test_results(organization, project, pipeline_name, headers))

daily_test_results_df = pd.DataFrame(daily_test_results)

print(daily_test_results_df)






