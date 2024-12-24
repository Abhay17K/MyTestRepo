##########################################################################################
#  Author: Hari Hara Sarma                                                               #
#                                                                                        #
#  Script to clone the GIT Repository at specific location                               #
#                                                                                        #
#  Usage:                                                                                #
#  -----                                                                                 #
#  python globalGitConnect.py                                                            #
#           <GIT_URL> <BRANCH> <DEV_CONFG_PATH> [PAT_TOKEN]                              #
#                                                                                        #
#                                                                                        #
# NOTE: Here PAT is the "Personal Access Token" gerated from GIT API                     #
##########################################################################################
 
 
########################## IMPORT PACKAGES#######################################    
import os
import re
import sys
import json
import time
import random
import string
import logging
import subprocess

from tkinter import TclError, Toplevel, Tk
from common import ContentLogger
from tkinter.filedialog import askdirectory
##################################################################################
def generate_random_key():
    letters_and_digits = string.ascii_uppercase + string.digits
    random_let_digit = [random.choice(letters_and_digits) for i in range(4)]
    random_string_and_digits = ''.join(random_let_digit)
    return random_string_and_digits 


def cloneRepo(remote_url, path_to_download):
    try:
        logging.info(f"Cloning the Repo at {path_to_download}")
        content_logger.log("info", f"Cloning the Repo at {path_to_download}")
        repo = git.Repo.clone_from(remote_url, path_to_download)
        logging.info(f"\nRepository cloned to {path_to_download} successfully.\n")
        content_logger.log("info", f"Repository cloned to {path_to_download} successfully.")

    except Exception as e:
        print(json.dumps({"ERROR": f"Unable to clone the repository", "REASON": str(e)}))
        logging.info(f"\nUnable to clone the repository {str(e)}.\nCheck the GIT URL and Personal Access Token and try again..\n")
        content_logger.log("error", f"Unable to clone the repository {str(e)}. Check the GIT URL and Personal Access Token and try again..")
        sys.exit(1)
    
    return repo


def checkout_to(repo, branch):
    try:
        logging.info(f"\nChecking out to the branch {branch}..\n")
        content_logger.log("info", f"Checking out to the branch {branch}..")
        repo.git.checkout(branch)
    except Exception as e:
        print(json.dumps({"ERROR": f"Unable to checkout to the branch  - {branch}", "REASON": str(e)}))
        logging.info(f"\nUnable to checkout to the branch - {branch}\nREASON: {str(e)}")
        content_logger.log("error", f"Unable to checkout to the branch - {branch}\nREASON: {str(e)}")
        sys.exit(1)


def git_pull(repo, branch=None):
    try:
        logging.info("\nTaking pull from the Git Repo..")
        content_logger.log("info", "Taking pull from the Git Repo..")
        if branch:
            repo.remotes.origin.pull(branch)
        else:
            repo.git.pull()
    except Exception as e:
        print(json.dumps({"ERROR": f"Unable to take the pull.", "REASON": str(e)}))
        logging.info(f'\nUnable to take the pull.\nREASON: {str(e)}')
        content_logger.log("error", f'Unable to take the pull.\nREASON: {str(e)}', )
        sys.exit(1)


def create_branch(repo, feature_branch):
    try:
        logging.info(f"Creating the feature branch {feature_branch}..\n")
        content_logger.log("info", f"Creating the feature branch {feature_branch}..")
        feature_branch_ref = repo.create_head(feature_branch)
       
    except Exception as e:
        print(json.dumps({"ERROR": f"Unable to create the feature branch - {feature_branch}", "REASON": str(e)}))
        logging.info(f"\nError: Unable to create the feature branch {feature_branch}.\nREASON: {str(e)}")
        content_logger.log("error", f"Error: Unable to create the feature branch {feature_branch}.\nREASON: {str(e)}")
        sys.exit(1)


def add_path_into_dev_config(path_, data, repo_owner, repo_name, branch):
    path_ = os.path.abspath(path_)
    data.append(f"\nGLOBAL_GIT_CONNECT_PATH_{repo_owner}_{repo_name}_{branch} = {path_}\n")
 
    with open(dev_config_path, 'w') as fp:
        fp.writelines(data)


def update_path_in_dev_config(path_, data, index, repo_owner, repo_name, branch):
    path_ = os.path.abspath(path_)
    data[index] = f"GLOBAL_GIT_CONNECT_PATH_{repo_owner}_{repo_name}_{branch} = {path_}\n"

    with open(dev_config_path, 'w') as fp:
        fp.writelines(data)

 
def browse_path(initial_folder=None):
    try:
        # Create a root Tkinter window (hidden)
        root = Tk()
        root.withdraw()  # Hide the main window
        # Disable interaction with the rest of the system
        root.attributes("-topmost", True)
        # Open the directory selection dialog
        if initial_folder:
            path = askdirectory(parent=root, title="Select Folder", initialdir=initial_folder)
        else:
            path = askdirectory(parent=root, title="Select Folder")  # Show dialog box and return the path
        # Destroy the root window once done
        root.destroy()

        return path
    except TclError as e:
        # Handle cases where the window fails to open properly
        print(json.dumps({"ERROR": "Path selection window could not be opened.", "REASON": str(e)}))
        logging.info("Path selection window could not be opened. REASON: Another Tkinter instance might be running.")
        content_logger.log("error", "Path selection window could not be opened. REASON: Another Tkinter instance might be running.")
        sys.exit(1)
         
 
def read_or_update_dev_config_file(git_url, dev_config_path, repo_name, repo_owner):
    status = False
    # Read the dev_config_ini file content.
    fp = open(dev_config_path)
    data = fp.readlines()
    fp.close()
        
    for index, line in enumerate(data):
        # Look for the "GLOBAL_GIT_CONNECT_PATH" in row
        if f"GLOBAL_GIT_CONNECT_PATH" in line:
            status = True
            break
    # If "GLOBAL_GIT_CONNECT_PATH" available, then get the PATH.
    if status:
        try:
            key, path_ = [i.strip() for i in line.split('=')]
        except:
            key = path_ = ''

        if f'_{repo_owner}_' in key and f'_{repo_name}_' in key:
          #  print('Repo Owner and Repo name are same')
            if key.endswith(branch):
                if os.path.exists(path_):
                    content_logger.log("info","Select the path to clone the project.")
                    logging.info("Select the path to clone the project.")
                    new_path = browse_path(path_)
                    content_logger.log("info", f"Cloning the project at : {new_path}")
                    logging.info(f"Cloning the project at : {new_path}")
                    if not new_path:
                        content_logger.log("error", "No path selected. REASON: User has not selected any folder path.")
                        logging.info("No path selected. REASON: User has not selected any folder path.")
                        print(json.dumps({"ERROR": "No path selected.", "REASON": "User has not selected any folder path."}))
                        sys.exit(1)
                    if os.path.abspath(os.path.join(new_path, repo_name)) == os.path.abspath(path_) or os.path.abspath(path_) in os.path.abspath(os.path.abspath(new_path)):
                        content_logger.log("warning", "You have selected same Path.")
                        logging.info("You have selected same Path.")
                        global warning
                        warning = f"You have selected same Path - {path_}"
                       # print(json.dumps({"WARNING": "You have selected same Path."}))
                        return path_
                    new_path = os.path.join(new_path, repo_name)
                    
                    if not new_path or os.path.exists(new_path):
                        print(json.dumps({"ERROR": "Invalid path or no path selected.", "REASON": "User has selected invalid folder path or no folder selected."}))
                        logging.info("Invalid path or no path selected.\nREASON: \nUser has selected invalid folder path or no folder selected.")
                        content_logger.log("error", "Invalid path or no path selected.\nREASON: \nUser has selected invalid folder path or no folder selected.")
                        sys.exit(1)

                    update_path_in_dev_config(new_path, data, index, repo_owner, repo_name, branch)
                    return new_path
            else:
                if os.path.exists(path_):
                   # print("Branch is diffenrent")
                    update_path_in_dev_config(path_, data, index, repo_owner, repo_name, branch)
                    return path_

        # If invalid PATH found, Then prompt the user to select the PATH.
        path_ = browse_path()
        path_ = os.path.join(path_, repo_name)
        
        if not path_:
            print(json.dumps({"ERROR": "Invalid path or no path selected.", "REASON": "User has selected invalid folder path or no folder selected."}))
            logging.error("Invalid path or no path selected.\nREASON:\nUser has selected invalid folder path or no folder selected.")
            content_logger.log("error", "Invalid path or no path selected. REASON: User has selected invalid folder path or no folder selected.")
            sys.exit(1)

        update_path_in_dev_config(path_, data, index, repo_owner, repo_name, branch)
    
    # If "GLOBAL_GIT_CONNECT_PATH" is not available, then prompt the user for the PATH.
    else:
        path_ = browse_path()
        path_ = os.path.join(path_, repo_name)
        
        if not path_:
            print(json.dumps({"ERROR": "Invalid path or no path selected.", "REASON": "User has selected invalid folder path or no folder selected"}))
            logging.error("Invalid path or no path selected.\nREASON:\nUser has selected invalid folder path or no folder selected")
            content_logger.log("error", "Invalid path or no path selected. REASON: User has selected invalid folder path or no folder selected")
            sys.exit(1)
        
        add_path_into_dev_config(path_, data, repo_owner, repo_name, branch)
    
    return path_


def cloneGitRepo(git_url, branch, dev_config_path, pat_token):
    try:
        _, repo_owner, repo_name = re.search(r"https://(.*?)/(.*?)/(.*)", git_url).groups()
        repo_name = repo_name.split('.')[0]
        content_logger.log("info", f"Git Repo Owner: {repo_owner}, Git Repo Name: {repo_name}")
        logging.info( f"Git Repo Owner: {repo_owner}, Git Repo Name: {repo_name}")
    except Exception as e:
        logging.info("Invalid GIT URL.\nREASON:\nGiven GIT URL is invalid")
        content_logger.log("error", "Invalid GIT URL. REASON: Given GIT URL is invalid")
        print(json.dumps({"ERROR": f"Invalid GIT URL.", "REASON": "Given GIT URL is invalid."}))
        sys.exit(1)

    # Read the TARGET_FOLDER_PATH from dev_config_ini file.
    path_to_download = read_or_update_dev_config_file(git_url, dev_config_path, repo_name, repo_owner)
    git_url = git_url.replace(r"https://", '')
    remote_url = f"https://{pat_token}@{git_url}"
 
    logging.info(f"\nChecking for the existence of Target Directory - {path_to_download}\n")
    content_logger.log("info", f"Checking for the existence of Target Directory - {path_to_download}")
 
    if not os.path.exists(path_to_download):
        logging.info(f"\n{path_to_download} is not available.\n")
        content_logger.log("info", f"{path_to_download} is not available.")
        logging.info(f"\nStarted the cloning of {git_url} ....\n")
        content_logger.log("info", f"Started the cloning of {git_url} ....")
        # Cloning the repository
        repo = cloneRepo(remote_url, path_to_download)
    else:
        # print({"WARNING": f"Git Repo {repo_name} is already exists at {path_to_download}."})
        logging.info(f"\nWARNING: Git Repo {repo_name} is already exists at {path_to_download}. Intialiazing the REPO.")
        content_logger.log("info", f"WARNING: Git Repo {repo_name} is already exists at {path_to_download}. Intialiazing the REPO.")
        global warning
        warning = f"Git Repo {repo_name} is already exists at {path_to_download}"
        # Initializing the GIT REPO
        repo = git.Repo.init(path_to_download)
        # Stash the local changes
        repo.git.stash('save')

    # Checkout to specific branch
    checkout_to(repo, branch)
   
    # Taking the pull
    git_pull(repo, branch)
    
    # Creating feature branch
    create_branch(repo, feature_branch)

    # Chechout to feature branch 
    checkout_to(repo, feature_branch)

    # Take pull again.
    git_pull(repo, branch)
    return path_to_download
   
 
if __name__ == "__main__":
    warning = None
    try:
        import git
    except:
        subprocess.run("pip install -q gitpython", check=True)
        time.sleep(1.0)
        import git

    try:
        log_file = "./../../../Config/globalGitConnectionStatus.txt"
        content_log = "./../../../Logs/system/globalGitConnect.log"
        os.makedirs("./../../../Logs/system/", exist_ok=True)
        
        for file_ in [log_file, content_log]:
            if os.path.exists(file_):
                os.remove(file_)
                
        logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(message)s')
        content_logger = ContentLogger(content_log)

    except Exception as e:
        logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(message)s')
        content_logger = ContentLogger(content_log)

        content_logger.log("error", f"Selection window is allready opened: {e}")
        logging.error(f"Error: Selection window is allready opened. REASON: {e}")
        print(json.dumps({"ERROR": f"Selection window is allready opened","REASON": f"{e}"}))
        sys.exit(1)

    params = sys.argv
   
    if len(params) == 5:
        _, git_url, branch, dev_config_path, pat_token = params
    elif len(params) == 4:
        _, git_url, branch, dev_config_path = params
        pat_token = ''
    else:
        print(json.dumps({"ERROR": "Invalid arguments", "REASON": "Script needs exactly four arguments. i.e., <GIT_URL> <BRANCH> <DEV_CONFG_PATH> [PAT_TOKEN]"}))
        logging.info("Invalid arguments, \nREASON:\nScript needs exactly four arguments. i.e., <GIT_URL> <BRANCH> <DEV_CONFG_PATH> [PAT_TOKEN]")
        content_logger.log("error", "Invalid arguments, REASON: Script needs exactly four arguments. i.e., <GIT_URL> <BRANCH> <DEV_CONFG_PATH> [PAT_TOKEN]")
        sys.exit(1)

    if not os.path.exists(dev_config_path):
        print(json.dumps({"ERROR": f"Invalid DEV_CONFIG_FILE", "REASON": f"No Dev_CONFIG_FILE available at {dev_config_path}"}))
        logging.info(f"ERROR: Invalid DEV_CONFIG_FILE\nREASON:\nNo Dev_CONFIG_FILE available at {dev_config_path}")
        content_logger.log("error", f"ERROR: Invalid DEV_CONFIG_FILE\nREASON:\nNo Dev_CONFIG_FILE available at {dev_config_path}")
        sys.exit(1)
    
    random_key = generate_random_key()
    feature_branch = f"feature_{branch}_{random_key}"
    path_to_download = cloneGitRepo(git_url, branch, dev_config_path, pat_token)
    
    print(json.dumps({'SUCCESS': f"Created feature branch {feature_branch} from the branch {branch}",
        "GIT_REPO_LOC": path_to_download, "WARNING": warning}))
    logging.info('\nSUCCESS')
    content_logger.log("info", 'SUCCESS')
       