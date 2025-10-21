import google.generativeai as genai
import json
import re
import docx
from io import BytesIO

def get_gemini_response(resume_content):
    """
    Sends resume content to the Gemini API and gets the extracted information in JSON format.
    """
    # ==============================================================================
    # IMPORTANT: INSERT YOUR API KEY HERE
    # ==============================================================================
    GEMINI_API_KEY = "AIzaSyCUUhK6bngglPni-WOPCmTINAetFiisbnk"
    # ==============================================================================

    genai.configure(api_key=GEMINI_API_KEY)

    model = genai.GenerativeModel('gemini-2.5-flash') # Or your preferred model

    prompt = f"""
    You are an expert at extracting candidate information from resumes.
    Below is text extracted from a resume. Your task is to extract the details and present them in a structured JSON array.
    Each element in the array should represent a single candidate.

    Here are the required fields:
    1. first_name: The candidate's first name. Usually found at/near the beginning of the resume, as a header. 
    2. last_name: The candidate's last name. Usually found at/near the beginning of the resume, as part of the header. 
    3. address: Where they live. Try and look for a Canadian or American address (e.g., 640 Pepperloaf Crescent, Winnipeg, MB R3R 1E8)
    4. date_of_birth: The candidate's date of birth (e.g., 'Jan 01, 1990') should be written in YYYY-MM-DD format. If not available, use an empty string.
    5. diploma: what they studied for their diploma (if applicable) (e.g., 'Diploma in Data Science and Machine Learning'). 
    6. diploma_school:  The school they studied in for their diploma (e.g., 'Red River College'). Usually found next to the course they studied for their diploma (e.g., 'Diploma in Welding')
    7. degree: The highest degree or primary field of study mentioned (e.g., 'Bsc. Computer Science', 'BA Philosophy' etc.).
    8. degree_school: The school they studied in for their degree (e.g., 'University of Nairobi'). Usually found next to the course they studied for their degree (e.g., 'BA Psychology')

    Please ensure the output is a single JSON array of objects, with no additional text or formatting outside of the JSON.
    If the resume contains information for only one person, the array should contain a single object.

    Resume Content:
    {resume_content}
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"An error occurred with the Gemini API: {e}")
        return None

def process_resume(resume_file):
    """
    Processes an uploaded resume file, extracts information using Gemini,
    and returns it as a dictionary and the raw text.
    """
    try:
        if resume_file.name.endswith('.docx'):
            # For .docx files, read the content into a BytesIO object
            # and then process with the docx library.
            doc = docx.Document(BytesIO(resume_file.read()))
            resume_content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        else:
            # For other file types, assume they can be decoded as text.
            resume_content = resume_file.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error reading file: {e}")
        return None, None

    gemini_output = get_gemini_response(resume_content)

    if gemini_output:
        # Use regex to find the JSON block, making it robust against surrounding text
        match = re.search(r'```json\s*([\s\S]*?)\s*```|(\[[\s\S]*\])', gemini_output)
        
        if match:
            # Prioritize the content within ```json ... ```, otherwise, take the first JSON-like structure
            json_str = match.group(1) if match.group(1) else match.group(2)
            try:
                # The extracted text is already a string, so we load it into a Python object
                parsed_data = json.loads(json_str)
                # We return the parsed data and the original gemini_output to be displayed
                return parsed_data, gemini_output
            except json.JSONDecodeError as e:
                print(f"Failed to decode JSON from Gemini response: {e}")
                # Return the raw output for debugging purposes
                return None, gemini_output
        else:
            print("No JSON block found in the Gemini response.")
            return None, gemini_output # Return raw output if no JSON is found

    return None, None


if __name__ == "__main__":
    pass