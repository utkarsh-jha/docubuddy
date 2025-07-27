
import os
import json
from dotenv import load_dotenv
from openai import AzureOpenAI
import difflib

load_dotenv()

model_name = os.getenv("MODEL_NAME")
# https://llmfordocubuddy.openai.azure.com/openai/deployments/gpt-4.1/chat/completions?api-version=2025-01-01-preview
client = AzureOpenAI(
    azure_endpoint=os.getenv("MODEL_ENDPOINT"),
    api_version=os.getenv("MODEL_VERSION"),
    api_key=os.getenv("API_KEY"),
)

def infer_docs_from_llm(file_name, file_content, diff_str):
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

    

    print(f"Processing documentation for: {file_name}")

    # Prepare the content for LLM analysis
    file_changes_text = f"File: {file_name}\n\n"


    # Create the prompt for GPT-4
    prompt = f"""
        You are a code documentation expert. Analyze the following code changes and the complete file content to generate a patch file that adds, removes, or updates the input file with documentation ONLY.

        IMPORTANT INSTRUCTIONS:
        1. For ADDED code (lines starting with +): If it lacks documentation, insert appropriate docstrings, comments, or type hints.
        2. For REMOVED code (lines starting with -): If any related docstrings or comments exist, remove them accordingly.
        3. Do NOT change or add executable code or logic, only add or modify documentations as a comment (docstrings, comments, type hints).
        4. Follow the docstring format and indentation and language specific documentation standards.
        5. Maintain valid File syntax at all times.
        6. The output must be the same file with updated documentation and virtually no code changes, keep all the existing files verbatim.
        7. Use the complete file content as context to understand the code structure and existing documentation patterns.
        8. From the file get the file extension and use it to determine the language for docstring format. 
        9. Do not add any markdown or other things in the source file
        FILE NAME:
        {file_name}
        
        COMPLETE FILE CONTENT:
        ```
        {file_content}
        ```

        CODE CHANGES TO ANALYZE:
        {diff_str}

        Based on the complete file content and the specific changes shown above, generate documentation improvements.
        Respond with updated file with documentation enhancements, no explanations also make sure the code contents should exactly match the existing file.
        Ignore the changes which does not represent any logic changes and wont contribute to the functionality of the code (like spaces and formatting) for documentation generation but keep them in the final code.
        Strictly do not change any code line at all at any cost
        It is very important that you dont add any executable code or logic, only add or modify documentations as a comment (docstrings, comments, type hints).
        
        thanks for being a good bot, do not hallucinate or make up any information, just use the provided file content and documentation changes.
        """


    try:
        response = client.chat.completions.create(
            model=model_name, 
            messages=[
                {
                    "role": "system",
                    "content": '''You are an expert code documentation assistant. Help improve code documentation without changing functionality or any code. and give me the updated code file as response.
                    Follow PEP 257 for docstring format and indentation. Maintain valid file syntax at all times.''',
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=2000,
        )

        suggestion = response.choices[0].message.content
        return suggestion

    except Exception as e:
        print(f"Error getting documentation suggestions for {file_name}: {e}")
        return
