import requests
import pandas as pd
import base64

# Azure DevOps credentials
organization = "DigitalFactoryOrganisation"
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

# To get all commits for each repository 
def get_commits(org, project, repo_id, headers):
    url = f"https://dev.azure.com/{org}/{project}/_apis/git/repositories/{repo_id}/commits?api-version=7.1"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch commits for repository '{repo_id}':", response.status_code, response.text)
        return []
    return response.json().get('value', [])

all_commits = []
for _, project in projects.iterrows():  
    project_name = project["ProjectName"]
    print(f"Fetching repositories for project: {project_name}")
    repositories = get_repositories(organization, project_name, headers)
    for repo in repositories:
        repo_id = repo["id"]
        repo_name = repo["name"]
        commits = get_commits(organization, project_name, repo_id, headers)
        for commit in commits:

            all_commits.append({
                "ProjectName": project_name,
                "RepositoryId": repo_id,
                "RepositoryName": repo_name,
                "CommitId": commit.get("commitId"),
                "Author": commit.get("author", {}).get("name"),
                "Date": commit.get("author", {}).get("date"),
                "Comment": commit.get("comment"),
                "Additions": commit.get("changeCounts", {}).get("Add"),
                "Deletions": commit.get("changeCounts", {}).get("Delete"),
                "Editions": commit.get("changeCounts", {}).get("Edit"),
            })
        
commits_df = pd.DataFrame(all_commits)
commits_df
