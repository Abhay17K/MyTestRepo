##########################################################################################
#  Author: Abhay Khanna                                                                  #
#                                                                                        #
#  Script to get the issue details and the first comment from a Jira issue URL           #
#                                                                                        #
#  Usage:                                                                                #
#  -----                                                                                 #
#  python fetchJiraIssue.py <JIRA_ISSUE_URL> <EMAIL> <API_TOKEN>                         #
#                                                                                        #
# NOTE: Jira API uses email and API Token for authentication                             #
##########################################################################################
 
########################## IMPORT PACKAGES #######################################    
import os
import re
import sys
import subprocess
import time
import json
from common  import ContentLogger
try:
    import requests 
except:
    subprocess.run("pip install -q requests", check=True)
    time.sleep(5.0)
    import requests

import logging
import warnings
warnings.filterwarnings("ignore")
##################################################################################
 
def getIssueDetailsFromJira(jira_issue_url, email, api_token):
    try:
        # Extract the Jira base URL and the issue key from the URL
        jira_base_url, issue_key = re.search(r"(https://[a-zA-Z0-9_\-\.]+)/(browse/)?([A-Z0-9\-]+)", jira_issue_url).groups()[0], re.search(r"(https://[a-zA-Z0-9_\-\.]+)/(browse/)?([A-Z0-9\-]+)", jira_issue_url).groups()[-1]
    except:
        print({'ERROR': {'message': "Invalid Jira issue URL."}})
        logging.info("Invalid Jira issue URL.\n\nDONE!")
        content_logger.log("error","Invalid Jira issue URL.\n\nDONE!")
        sys.exit(1)
 
    # API endpoint for the specific Jira issue
    issue_url = f"{jira_base_url}/rest/api/2/issue/{issue_key}"
    comment_url = f"{jira_base_url}/rest/api/2/issue/{issue_key}/comment"
 
    # Jira API uses Basic Authentication (email and API token)
    auth = (email, api_token)
    # Get the issue details
    issue_response = requests.get(issue_url, auth=auth, headers={"Accept": "application/json"}, verify=False)
    if issue_response.status_code != 200:
        logging.info(f"Unable to get the issue details from JIRA\n")
        logging.info(f'Error: {issue_response.status_code} - {issue_response.text} \n\nDONE!')
        
        content_logger.log("info", f"Unable to get the issue details from JIRA\n")
        content_logger.log("info", f'Error: {issue_response.status_code} - {issue_response.text} \n\nDONE!')
 
        error_data = json.loads(issue_response.text)
        message = error_data.get("errorMessage") or error_data.get("errorMessages") or error_data.get("Unable to get the issue details from JIRA")
        print({'ERROR' : {"message": message}})
        sys.exit(1)
 
    issue = issue_response.json()
 
    # Get the first comment
    comments_response = requests.get(comment_url, auth=auth, headers={"Accept": "application/json"}, verify=False)
    if comments_response.status_code == 200:
        comments = comments_response.json().get('comments', [])
        first_comment = comments[0]['body'] if comments else "No comments available."
    else:
        first_comment = "Unable to fetch comments."
 
    logging.info(f"Issue Title : {issue['fields']['summary']}\n")
    logging.info(f"Issue Description : \n{issue['fields']['description']}\n")
    
    content_logger.log("info", f"Issue Title : {issue['fields']['summary']}\n")
    content_logger.log("info", f"Issue Description : \n{issue['fields']['description']}\n")
    
 
    result = {
        "Title": issue['fields']['summary'],
        "Description": issue['fields']['description'],
    }
    return result
 
if __name__ == "__main__":
    params = sys.argv

    log_file = "./../../../Data/DefectFixIssueDetails/jiraIssueDetails.txt"
    content_log = "./../../../Logs/system/fetchJiraIssues.log"
    os.makedirs("./../../../Logs/system/", exist_ok=True)
    
    for file_ in [log_file, content_log]:
        if os.path.exists(file_):
            os.remove(file_)

    logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(message)s')
    content_logger = ContentLogger(content_log)

    if len(params) == 4:
        _, jira_issue_url, email, api_token = params
    else:
        print({'ERROR': {'message': "Script needs exactly three arguments. i.e., <JIRA_ISSUE_URL> <EMAIL> <API_TOKEN>"}})
        logging.info("Script needs exactly three arguments. i.e., <JIRA_ISSUE_URL> <EMAIL> <API_TOKEN>")
        content_logger.log("error", "Script needs exactly three arguments. i.e., <JIRA_ISSUE_URL> <EMAIL> <API_TOKEN>")
        sys.exit(1)
    
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    issue_details = getIssueDetailsFromJira(jira_issue_url, email, api_token)
    print({'SUCCESS': "Jira Issue fetched successfully."})
    content_logger.log("info", "Jira Issue fetched successfully.")
    logging.info('\nDONE!')
