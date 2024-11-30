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
    Create an OpenAI Assistant for schedule management.
    """
    assistant = client.beta.assistants.create(
        name="Schedule Manager",
        instructions=(
            "You are an assistant that helps manage and modify weekly schedules based on user input. "
            "You can read, interpret, update, and always return a CSV file containing schedule information "
            "based solely on user requests, without re-querying any external sources. "
            "The CSV file will not have headers and will have the following structure: "
            "- The first column: Name of the event "
            "- The second column: Date (start) "
            "- The third column: Date (end) "
            "- The fourth column: Location "
            "- The fifth column: Notes "
            "Given a CSV file with current schedule data and a user's natural language request, "
            "provide the necessary updates to the schedule and present the updated CSV for download. "
            "Steps: "
            "1. Accept the CSV data and read the content. "
            "2. Interpret the user's request and apply the necessary changes to the schedule. "
            "3. Save the modified data into a new CSV file called 'new_schedule.csv'. "
            "4. Allow the user to download this updated CSV file. "
            "Output Format: "
            "Respond with the updated CSV data formatted as a downloadable link named 'new_schedule.csv'. "
            "Notes: "
            "Ensure that the modification process is clearly communicated to the user, and that any errors during "
            "manipulation are presented with clear instructions on how to correct them. "
            "Never re-query or retrieve new schedule data from other sources; only use the provided CSV for modifications."
        ),
        tools=[{"type": "code_interpreter"}],
        model="gpt-4-turbo"
    )
    return assistant


def process_schedule_request(query):
    """
    Process a schedule modification request
    """
    assistant = None

    # Create the file resource
    file = client.files.create(
        file=open("example_schedule.csv", "rb"),
        purpose='assistants'
    )

    try:
        # Create assistant without the file
        assistant = create_schedule_assistant()

        # Create a thread
        thread = client.beta.threads.create()

        # Send the message to the thread with the file attached
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=query,
            attachments=[{"tools": [{"type": "code_interpreter"}],"file_id": file.id}]
        )

        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )

        # Wait for run completion
        while run.status != "completed":
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            time.sleep(1)

        # Retrieve messages


    finally:
        # Clean up resources
        if assistant is not None:
            client.beta.assistants.delete(assistant.id)
        client.files.delete(file.id)

# Example usage
if __name__ == "__main__":

    file = client.files.content("file-CxDD6Qf4tCpefa7FBVbE53")
    content = file.content.decode("utf-8")
    with open("updated_schedule.csv", "a") as file:  # Using "a" mode to append content
        file.write(content)