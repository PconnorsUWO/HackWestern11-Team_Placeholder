from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OpenAI.api_key = OPENAI_API_KEY
client = OpenAI()


# Upload a file with an "assistants" purpose
file = client.files.create(
  file=open("mydata.csv", "rb"),
  purpose='assistants'
)


completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "I am going to pass you"},
        {
            "role": "user",
            "content": "Write a haiku about recursion in programming."
        }
    ]
)

print(completion.choices[0].message.content)
