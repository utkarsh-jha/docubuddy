# Conda Environment Setup

To set up a Python environment using conda for running the Flask server and hooks:

1. Install [Anaconda](https://www.anaconda.com/products/distribution) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html) if you haven't already.
2. Create and activate a new environment:
    ```bash
    conda create -n docupilot python=3.10
    conda activate docupilot
    ```
3. Install required dependencies (adjust the path as needed):
    ```bash
    pip install -r ../Service/requirements.txt
    ```
4. Run the Flask server as described in the Usage section.

# .githooks Folder

This folder contains custom Git hooks and supporting scripts for automating code review and patching workflows.

## Structure

- **Driver/docupilot_githook.sh**: Main post-commit hook script. Sends changed files to a Flask server (`/docufy` endpoint) and updates files with the server's response.
- **Service/docupilot_api.py**: Example Flask server implementation for handling `/docufy` requests.
- **Test/README.md**: Documentation for the test server and endpoints.

## Usage

1. Ensure the Flask server is running (see Test/README.md for details).
2. Install the post-commit hook:
    - Copy `Driver/docupilot_githook.sh` to your repo's `.git/hooks/post-commit` and make it executable:
      ```bash
      cp .githooks/Driver/docu-githook.sh .git/hooks/post-commit
      chmod +x .git/hooks/post-commit
      ```
3. Commit changes as usual. After each commit, the hook will:
    - Detect changed files
    - Send them to the Flask server
    - Overwrite files with the server's response if provided

## .env file
If needed, create a `.env` file with the following (for OpenAI integration or prompts):
```bash
MODEL_ENDPOINT=
MODEL_VERSION=
MODEL_NAME=
API_KEY=
```