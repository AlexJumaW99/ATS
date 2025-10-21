import google.generativeai as genai
import pandas as pd
from io import StringIO
import json

def get_gemini_response(resume_content):
    """
    Sends resume content to the Gemini API and gets the extracted information.
    """
    # ==============================================================================
    # IMPORTANT: INSERT YOUR API KEY HERE
    # ==============================================================================
    GEMINI_API_KEY = "AIzaSyCUUhK6bngglPni-WOPCmTINAetFiisbnk"
    # ==============================================================================

    genai.configure(api_key=GEMINI_API_KEY)

    model = genai.GenerativeModel('gemini-1.5-flash') # Or your preferred model

    prompt = f"""
    Analyze the following resume content and extract the following information:
    - First Name
    - Last Name
    - Date of Birth
    - Degree

    Provide the output in a single line CSV format with the headers:
    "first_name,last_name,date_of_birth,degree"

    If any information is not found, leave the corresponding value empty.

    Resume Content:
    {resume_content}
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def process_resume(resume_file):
    """
    Processes an uploaded resume file, extracts information using Gemini,
    and returns it as a dictionary and the raw text.
    """
    resume_content = resume_file.read().decode('utf-8', errors='ignore')
    gemini_output = get_gemini_response(resume_content)

    if gemini_output:
        # Clean the output - LLMs can sometimes add extra text
        cleaned_csv = gemini_output.strip().replace("```csv", "").replace("```", "")

        # Convert CSV to a Pandas DataFrame
        csv_data = StringIO(cleaned_csv)
        df = pd.read_csv(csv_data)

        # Convert DataFrame to JSON
        json_output = df.to_json(orient='records')
        return json.loads(json_output), gemini_output
    return None, None