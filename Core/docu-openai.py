import os

from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

# openai/deployments/gpt-4.5-preview-kusto/chat/completions?api-version=2025-01-01-preview
client = AzureOpenAI(
    azure_endpoint=os.getenv("MODEL_ENDPOINT"),
    api_version=os.getenv("MODEL_VERSION"),
    api_key=os.getenv("API_KEY"),
)

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
