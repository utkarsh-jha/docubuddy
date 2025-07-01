import subprocess
import os
from openai import AzureOpenAI

# openai/deployments/gpt-4.5-preview-kusto/chat/completions?api-version=2025-01-01-preview
client = AzureOpenAI(
    azure_endpoint="https://ai-rmaguyhub553390411579.openai.azure.com/",
    api_version="2025-01-01-preview",
    api_key="",
)

# Will generate docs for only python files
directory_filter = ["src"]


def compare_commits(previous_head, current_head):
    """
    Compare two commits and return a list of differences as structured JSON.
    """
    try:
        diff_output = subprocess.check_output(
            ["git", "diff", previous_head, current_head], universal_newlines=True
        )
        diff = []
        current_file = None

        for line in diff_output.splitlines():
            if line.startswith("diff --git"):
                file_name = line.split(" ")[-1].replace("b/", "")
                # Check if file is in any of the filtered directories
                if any(
                    not directory_filter or
                    len(directory_filter) == 0 or
                    file_name.startswith(folder + "/")
                    or file_name.startswith(folder + "\\")
                    for folder in directory_filter
                ):
                    current_file = {"file": file_name, "changes": []}
                    diff.append(current_file)
                else:
                    current_file = None  # Skip this file
            elif line.startswith("@@"):
                if current_file:  # Only process if we're tracking this file
                    parts = line.split(" ")
                    old_range = parts[1]
                    new_range = parts[2]
                    current_file["changes"].append(
                        {"old_range": old_range, "new_range": new_range, "content": []}
                    )
            elif line.strip() == "\\ No newline at end of file":
                if (
                    current_file and current_file["changes"]
                ):  # Only process if we're tracking this file
                    current_file["changes"][-1]["note"] = "No newline at end of file"
            else:
                if current_file and current_file["changes"]:
                    current_file["changes"][-1]["content"].append(line)
        return diff

    except subprocess.CalledProcessError as e:
        print(f"Error getting diff: {e}")
        return []


def infer_docs_from_llm(diff_map):
    """
    Send diff information to Azure OpenAI GPT-4 to get documentation suggestions.

    Args:
        diff_map: List of file changes from compare_commits function

    Returns:
        dict: Documentation suggestions for each file
    """
    # Initialize Azure OpenAI client
    # client = AzureOpenAI(
    #     api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    #     api_version="2024-02-01",
    #     azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    # )

    documentation_suggestions = {}

    for file_entry in diff_map:
        file_name = file_entry["file"]
        changes = file_entry["changes"]

        # Skip if no changes
        if not changes:
            continue

        print(f"Processing documentation for: {file_name}")

        # Read the current file content to provide context
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                current_file_content = f.read()
        except FileNotFoundError:
            print(f"Warning: Could not read file {file_name}, skipping...")
            continue
        except Exception as e:
            print(f"Warning: Error reading file {file_name}: {e}, skipping...")
            continue

        # Prepare the content for LLM analysis
        file_changes_text = f"File: {file_name}\n\n"

        for change in changes:
            file_changes_text += (
                f"Change in lines {change['old_range']} -> {change['new_range']}:\n"
            )
            for content_line in change["content"]:
                file_changes_text += f"{content_line}\n"
            file_changes_text += "\n"

        # Create the prompt for GPT-4
        prompt = f"""
            You are a code documentation expert. Analyze the following code changes and the complete file content to generate a patch file that adds, removes, or updates documentation ONLY.

            IMPORTANT INSTRUCTIONS:
            1. For ADDED code (lines starting with +): If it lacks documentation, insert appropriate docstrings, comments, or type hints.
            2. For REMOVED code (lines starting with -): If any related docstrings or comments exist, remove them accordingly.
            3. Do NOT change or add executable code or logic—only modify documentation (docstrings, comments, type hints).
            4. Follow PEP 257 for docstring format and indentation.
            5. Maintain valid Python syntax at all times.
            6. The output must be a valid unified diff (patch file) that can be applied using `git apply` or `patch`.
            7. If no documentation changes are needed, return an empty diff.
            8. Use the complete file content as context to understand the code structure and existing documentation patterns.

            COMPLETE FILE CONTENT:
            ```python
            {current_file_content}
            ```

            CODE CHANGES TO ANALYZE:
            {file_changes_text}

            Based on the complete file content and the specific changes shown above, generate documentation improvements.
            Respond ONLY with the patch file content, no explanations.
            """


        try:
            response = client.chat.completions.create(
                model="gpt-4.5-preview-kusto",  # Use your Azure OpenAI deployment name
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert code documentation assistant. Help improve code documentation without changing functionality. and give me the updated code file as repsponse",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=2000,
            )

            suggestion = response.choices[0].message.content
            documentation_suggestions[file_name] = suggestion

            print(f"Documentation suggestions for {file_name}:")
            print(suggestion)
            print("-" * 80)

        except Exception as e:
            print(f"Error getting documentation suggestions for {file_name}: {e}")
            documentation_suggestions[file_name] = f"Error: {str(e)}"

    return documentation_suggestions


def apply_documentation_patches(doc_suggestions):
    """
    Apply the documentation patches generated by the LLM to the actual files.
    
    Args:
        doc_suggestions: Dictionary with file names as keys and patch content as values
        
    Returns:
        dict: Results of patch application for each file
    """
    application_results = {}
    
    for file_name, patch_content in doc_suggestions.items():
        if patch_content.startswith("Error:"):
            application_results[file_name] = "Skipped due to LLM error"
            continue
            
        # Skip if no meaningful patch content
        if not patch_content.strip() or "no documentation changes are needed" in patch_content.lower():
            application_results[file_name] = "No documentation changes needed"
            continue
            
        print(f"Applying documentation patch for: {file_name}")
        
        try:
            # Write patch to a temporary file
            patch_file = f"{file_name}.patch"
            with open(patch_file, 'w', encoding='utf-8') as f:
                f.write(patch_content)
            
            patch_file = os.path.abspath(patch_file)
            # Try to apply the patch using git apply
            try:
                result = subprocess.run(
                    ['git', 'apply', '--check', patch_file],
                    capture_output=True,
                    text=True,
                    cwd=os.path.dirname(os.path.abspath(file_name)) if os.path.dirname(file_name) else '.',
                )
                
                if result.returncode == 0:
                    # Patch is valid, apply it
                    apply_result = subprocess.run(
                        ['git', 'apply', patch_file],
                        capture_output=True,
                        text=True,
                        cwd=os.path.dirname(os.path.abspath(file_name)) if os.path.dirname(file_name) else '.',
                    )
                    
                    if apply_result.returncode == 0:
                        application_results[file_name] = "Successfully applied documentation patch"
                        print(f"✓ Successfully applied patch for {file_name}")
                    else:
                        application_results[file_name] = f"Failed to apply patch: {apply_result.stderr}"
                        print(f"✗ Failed to apply patch for {file_name}: {apply_result.stderr}")
                else:
                    application_results[file_name] = f"Invalid patch format: {result.stderr}"
                    print(f"✗ Invalid patch for {file_name}: {result.stderr}")
                    
            except subprocess.CalledProcessError as e:
                application_results[file_name] = f"Git apply error: {e}"
                print(f"✗ Git apply error for {file_name}: {e}")
            
            # Clean up temporary patch file
            try:
                os.remove(patch_file)
            except OSError:
                pass  # Ignore cleanup errors
                
        except Exception as e:
            application_results[file_name] = f"Error creating patch file: {e}"
            # print stacktrace
            import traceback
            traceback.print_exc()
            print(f"✗ Error processing patch for {file_name}: {e}")
    
    return application_results


def create_backup_before_patches(file_list):
    """
    Create backup copies of files before applying patches.
    
    Args:
        file_list: List of file names to backup
        
    Returns:
        dict: Mapping of original files to backup file names
    """
    backup_mapping = {}
    timestamp = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip().decode('utf-8')
    
    for file_name in file_list:
        if os.path.exists(file_name):
            backup_name = f"{file_name}.backup-{timestamp}"
            try:
                import shutil
                shutil.copy2(file_name, backup_name)
                backup_mapping[file_name] = backup_name
                print(f"Created backup: {backup_name}")
            except Exception as e:
                print(f"Warning: Could not create backup for {file_name}: {e}")
    
    return backup_mapping


def main():
    # get commit at HEAD
    try:
        current_head = (
            subprocess.check_output(["git", "rev-parse", "HEAD"])
            .strip()
            .decode("utf-8")
        )
    except subprocess.CalledProcessError as e:
        print(f"Error getting HEAD commit: {e}")
        return

    # get commit at HEAD~1
    try:
        previous_head = (
            subprocess.check_output(["git", "rev-parse", "HEAD~1"])
            .strip()
            .decode("utf-8")
        )
    except subprocess.CalledProcessError as e:
        print(f"Error getting HEAD~1 commit: {e}")
        return

    # Compare the two commits
    differences = compare_commits(previous_head, current_head)

    # Get documentation suggestions from LLM
    if differences:
        print("\nGenerating documentation suggestions...")
        doc_suggestions = infer_docs_from_llm(differences)

        print("\n" + "=" * 80)
        print("DOCUMENTATION SUGGESTIONS SUMMARY")
        print("=" * 80)
        for file_name, suggestion in doc_suggestions.items():
            print(f"\n{file_name}:")
            print(suggestion)
        
        # Create backups before applying patches
        changed_files = [entry['file'] for entry in differences]
        print(f"\nCreating backups for {len(changed_files)} files...")
        # backup_mapping = create_backup_before_patches(changed_files)
        
        # Apply the documentation patches
        print(f"\nApplying documentation patches...")
        patch_results = apply_documentation_patches(doc_suggestions)
        
        print("\n" + "=" * 80)
        print("PATCH APPLICATION RESULTS")
        print("=" * 80)
        for file_name, result in patch_results.items():
            status_icon = "✓" if "Successfully" in result else "✗" if "Error" in result or "Failed" in result else "ℹ"
            print(f"{status_icon} {file_name}: {result}")
        
        # Summary
        successful_patches = sum(1 for result in patch_results.values() if "Successfully" in result)
        total_files = len(patch_results)
        print(f"\nSummary: {successful_patches}/{total_files} patches applied successfully")
        
        # if backup_mapping:
        #     print(f"Backup files created: {len(backup_mapping)}")
        #     print("You can restore from backups if needed")
            
    else:
        print("No changes found in the specified directories.")

    # Print the differences
    # print("Differences between commits:")
    # print(differences)


if __name__ == "__main__":
    # main()
    my_pathch = '''
diff --git a/src/perform_analysis.py b/src/perform_analysis.py
index e69de29..7f5c4c3 100644
--- a/src/perform_analysis.py
+++ b/src/perform_analysis.py
@@ -2,0 +3,4 @@
+
+def add(x: float, y: float) -> float:
+    """Return the sum of two numbers."""
+    return x + y
```
    '''
    print(my_pathch)
    apply_documentation_patches({"src/perform_analysis.py": my_pathch})
