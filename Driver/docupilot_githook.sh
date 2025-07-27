#!/bin/bash
set +x  # Disable command echoing (no debug output)
echo "post-commit hook started"
sleep 2 # Slight delay for commit operations to complete

# Define your API endpoint URL here
API_ENDPOINT=""
DOCUBUDDY_URL="$API_ENDPOINT"

# Check if API endpoint is set
if [ -z "$DOCUBUDDY_URL" ]; then
    echo "API_ENDPOINT is not set"
    exit 1
fi

echo "Using API endpoint: $DOCUBUDDY_URL"

# Get list of files changed in the last commit
changed_files=$(git diff --name-only HEAD~1 HEAD)

echo "Files changed in the last commit:"
for file in $changed_files; do
    echo " - $file"
done

for file in $changed_files; do
    # Skip if file was deleted or moved (doesn't exist now)
    if [ ! -f "$file" ]; then
        echo "Skipping deleted or moved file: $file"
        continue
    fi

    echo ""
    echo "Processing file: $file"

    # Create two temporary files: one for the diff, one for the full content
    diff_file=$(mktemp)
    content_file=$(mktemp)

    # Save git diff of this file between last two commits into temp diff_file
    git diff HEAD~1 HEAD -- "$file" > "$diff_file"

    # Save current full content of the file into temp content_file
    cat "$file" > "$content_file"

    # If the diff file is empty (no changes), skip this file
    if [ ! -s "$diff_file" ]; then
        echo "No diff for $file"
        # Remove temp files to avoid clutter
        rm -f "$diff_file" "$content_file"
        continue
    fi
    # Print the diff for logging/debugging
    echo "Git Diff for $file:"
    echo "----------------------------"
    cat "$diff_file"
    echo "----------------------------"

    # Send a POST request with filename, diff, and content as multipart/form-data
    PATCH=$(curl -s -X POST "$DOCUBUDDY_URL" \
        -F "filename=$file" \
        -F "diff=@$diff_file" \
        -F "content=@$content_file")

    echo "Response from server for $file:"
    echo "----------------------------"
    echo "$PATCH"
    echo "----------------------------"
    # Clean up the temp files after sending
    rm -f "$diff_file" "$content_file"

    # If a response was returned, overwrite the file with it
    if [ -n "$PATCH" ]; then
        echo "Updating file with response for $file"
        printf "%s" "$PATCH" > "$file"
    else
        echo "No response returned for $file"
    fi
done
