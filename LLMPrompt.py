import os
from openai import OpenAI
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def create_schedule_assistant():
    """
    Create an OpenAI Assistant for schedule management
    """
    assistant = client.beta.assistants.create(
        name="Schedule Manager",
        instructions=(
            "You are an assistant that helps manage and modify weekly schedules based on user input. "
            "You can read, interpret, and update CSV files containing schedule information. "
            "The csv file will have the name of the event in the first column, date start in the second column, "
            "date end in the third column, and Location in the fourth column and Notes in the Fifth. " 
            "Given a CSV file with current schedule data and a user's natural language request, "
            "provide the necessary updates to the schedule in CSV format."
            "Return a CSV file with the updated schedule."
        ),
        tools=[{"type": "code_interpreter"}],
        model="gpt-4-turbo"
    )
    return assistant

def process_schedule_request(query):
    """
    Process a schedule modification request and retrieve the CSV file
    """
    assistant = None
    
    # Create the file resource
    file = client.files.create(
        file=open("example_schedule.csv", "rb"),
        purpose='assistants'
    )
    
    try:
        # Create assistant
        assistant = create_schedule_assistant()
        
        # Create a thread
        thread = client.beta.threads.create()
        
        # Send the message to the thread with the file attached
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=query,
            attachments=[{
                "tools": [{"type": "code_interpreter"}],
                "file_id": file.id
            }]
        )
        
        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )
        
        # Wait for run completion
        while run.status not in ["completed", "failed"]:
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            time.sleep(1)
        
        # Check if run was successful
        if run.status == "failed":
            print(f"Run failed: {run.last_error}")
            return None
        
        # Retrieve messages
        messages = client.beta.threads.messages.list(
            thread_id=thread.id,
            order="asc"
        )
        
        # Find and download the CSV file
        for msg in messages.data:
            if msg.role == "assistant":
                for content in msg.content:
                    # Look for file attachments
                    if content.type == 'image_file' or content.type == 'file':
                        # Retrieve file details
                        file_id = (content.image_file or content.file).file_id
                        file_content = client.files.content(file_id)
                        
                        # Save the file
                        with open("updated_schedule.csv", "wb") as f:
                            f.write(file_content.read())
                        
                        print(f"CSV file saved as updated_schedule.csv")
                        return "updated_schedule.csv"
        
        print("No CSV file found in the assistant's response.")
        return None
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
    finally:
        # Clean up resources
        if assistant is not None:
            client.beta.assistants.delete(assistant.id)
        client.files.delete(file.id)

# Example usage
if __name__ == "__main__":
    query = "I want to read for an hour every day this week."
    result = process_schedule_request(query)
    
    # If a file was generated, you can now work with it
    if result:
        # Example: Print out the contents of the generated CSV
        with open(result, 'r') as f:
            print(f.read())