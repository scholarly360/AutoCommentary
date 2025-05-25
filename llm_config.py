from openai import OpenAI


from dotenv import load_dotenv
load_dotenv() 
client = OpenAI()
def llm_generate_summary(func_string):
    """
    This function generates a summary of a Python function using OpenAI's GPT-4o-mini model.
    It analyzes the provided function and returns a concise description of its purpose and behavior.
    """
    # Define the function to be analyzed

    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
        "role": "system",
        "content": [
            {
            "type": "text",
            "text": "Analyze this python function and generate a summary "
            }
        ]
        },
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": func_string
            }
        ]
        }
    ],
    response_format={
        "type": "text"
    },
    temperature=1,
    max_completion_tokens=2048,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )
    return(response.choices[0].message.content)