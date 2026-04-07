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
def get_list_of_builds(org, project, headers):
    url = f"https://dev.azure.com/{org}/{project}/_apis/build/builds?api-version=7.1"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch builds for '{project}':", response.status_code, response.text)
        return []
    return response.json().get('value', [])

all_builds = []
for project in projects["ProjectName"]:
    builds = get_list_of_builds(organization, project, headers)
    for build in builds:
        build_id = build["id"]
        
        all_builds.append({
            "ProjectName": project,
            "BuildId": build_id,
            "BuildMessage": build.get("triggerInfo", {}).get("ci.message"),
            "BuildNumber": build.get("buildNumber"),
            "Status": build.get("status"),
            "Result": build.get("result"),
            "QueueTime": build.get("queueTime"),
            "StartTime": build.get("startTime"),
            "FinishTime": build.get("finishTime"),
            "BuildNumberRevision": build.get("buildNumberRevision"),
            "priority": build.get("priority"),
            "Reason": build.get("reason"),
            "RequestedForBuild": build.get("requestedFor", {}).get("displayName"),
            "LastChangedDate": build.get("lastChangedDate"),
            "SourceBranch": build.get("sourceBranch"),
            "SourceVersion": build.get("sourceVersion"),
            "RequestedBy": build.get("requestedBy", {}).get("displayName"),
            "RepositoryName": build.get("repository", {}).get("name"),
            "RepositoryId": build.get("repository", {}).get("id"),
            "TriggeredByBuild": build.get("triggeredByBuild"),
        })

builds_df = pd.DataFrame(all_builds)
builds_df
print(builds_df)