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
projects.columns = ["ProjectId", "ProjectName"]

# Get list of repositories for each project, then get commits for each repository. 
def get_repositories(org, project, headers):
    url = f"https://dev.azure.com/{org}/{project}/_apis/git/repositories?api-version=7.1"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch repositories for '{project}':", response.status_code, response.text)
        return []
    return response.json().get('value', [])

# To get all pull requests for each repository 
def get_pull_requests(org, project, repo_id, headers):
    url = f"https://dev.azure.com/{org}/{project}/_apis/git/repositories/{repo_id}/pullrequests?searchCriteria.status=all&api-version=7.1"
    response = requests.get(url, headers=headers)
    print(response)
    if response.status_code != 200:
        print(f"Failed to fetch pull_requests for repository '{repo_id}':", response.status_code, response.text)
        return []
    return response.json().get('value', [])

all_pull_requests = []
for _, project in projects.iterrows():  
    project_name = project["ProjectName"]
    repositories = get_repositories(organization, project_name, headers)
    for repo in repositories:
        print(f"Fetching repositories for project: {project_name}")
        repo_id = repo["id"]
        repo_name = repo["name"]
        pull_requests = get_pull_requests(organization, project_name, repo_id, headers)

        for pull_request in pull_requests:
            
            all_pull_requests.append({
                "ProjectName": project_name,
                "RepositoryId": repo_id,
                "RepositoryName": repo_name,
                "PullRequestId": pull_request.get("pullRequestId"),
                "Title": pull_request.get("title"),
                "Status": pull_request.get("status"),
                "CreatedDate": pull_request.get("createdDate"),
                "ClosedDate": pull_request.get("closedDate"),
                "MergeStatus": pull_request.get("mergeStatus"),
                "IsDraft": pull_request.get("isDraft"),
                "CodeReviewId": pull_request.get("codeReviewId"),
                "CreatedBy": pull_request.get("createdBy", {}).get("displayName"),
            })
        
pull_requests_df = pd.DataFrame(all_pull_requests)
pull_requests_df
print(pull_requests_df.head())
