# clone_repo.py

import os
import git
from pathlib import Path
from datetime import datetime

def get_clone_path(git_url):
    repo_name = git_url.rstrip('/').split('/')[-1].replace('.git', '')
    downloads_path = Path.home() / "Downloads"
    return downloads_path / repo_name

def clone_git_repo(git_url):
    clone_path = get_clone_path(git_url)

    if clone_path.exists():
        return f"Repository already exists at: {clone_path}", str(clone_path)

    try:
        git.Repo.clone_from(git_url, clone_path)
        return f"Repository successfully cloned to: {clone_path}", str(clone_path)
    except Exception as e:
        return f"Error while cloning: {e}", None

def push_file_to_repo(git_url, file_bytes, filename, commit_message="Add file via Streamlit"):
    repo_path = get_clone_path(git_url)
    full_file_path = repo_path / filename

    try:
        # Write uploaded file to repo
        with open(full_file_path, 'wb') as f:
            f.write(file_bytes)

        # Git operations
        repo = git.Repo(repo_path)
        repo.git.add(filename)
        repo.index.commit(commit_message)
        origin = repo.remote(name='origin')
        origin.push()

        return f"✅ File `{filename}` pushed successfully with commit message: '{commit_message}'"
    except Exception as e:
        return f"❌ Failed to push file: {e}"
        
        
        # app.py

import streamlit as st
from clone_repo import clone_git_repo, push_file_to_repo

st.set_page_config(page_title="Git Repo Cloner + Pusher", page_icon="🛠️")
st.title("🛠️ Git Repository Cloner & File Pusher")

git_url = st.text_input("📝 Git Repository URL", placeholder="https://github.com/user/repo.git")

if st.button("🚀 Clone Repository"):
    if git_url:
        result, path = clone_git_repo(git_url)
        if "successfully" in result.lower():
            st.success(result)
        elif "already exists" in result.lower():
            st.info(result)
        else:
            st.error(result)
    else:
        st.warning("Please enter a valid Git URL.")

st.markdown("---")

st.subheader("📤 Upload and Push a File to the Repository")

uploaded_file = st.file_uploader("Choose a file to push", type=None)

commit_msg = st.text_input("💬 Commit message", value="Add file via Streamlit")

if st.button("⬆️ Push File to Repo"):
    if not git_url:
        st.warning("Please enter a Git URL above and clone it first.")
    elif uploaded_file is None:
        st.warning("Please upload a file to push.")
    else:
        result = push_file_to_repo(
            git_url,
            file_bytes=uploaded_file.read(),
            filename=uploaded_file.name,
            commit_message=commit_msg
        )
        if result.startswith("✅"):
            st.success(result)
        else:
            st.error(result)