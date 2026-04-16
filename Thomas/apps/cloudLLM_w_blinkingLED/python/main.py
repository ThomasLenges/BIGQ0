# === 1. BASIC CONVERSATION ===

import os
from bricks.cloud_llm.cloud_llm import CloudLLM
from bricks.cloud_llm.models import CloudModel
from arduino.app_utils import App

# Initialize the Brick (API key is loaded from configuration)
llm = CloudLLM(
    api_key="YourKey",
    model=CloudModel.OPENAI_GPT,
    system_prompt="You are a helpful assistant for an IoT device."
)

def simple_chat():
    # Send a prompt and print the response
    response = llm.chat("What is the model version I am talking to?")
    print(f"AI: {response}")

# Run the application
App.run(simple_chat)
