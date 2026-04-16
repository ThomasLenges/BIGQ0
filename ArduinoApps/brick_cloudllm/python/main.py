# === 1. BASIC CONVERSATION ===

APP NEEDS TO UPDATE WITH CORRECT KEY TO WORK!IN APP.YAML

import os
from arduino.app_bricks.cloud_llm import CloudLLM, CloudModel
from arduino.app_utils import App

# Initialize the Brick (API key is loaded from configuration)
llm = CloudLLM(
    model=CloudModel.OPENAI_GPT,
    system_prompt="You are a helpful assistant for an IoT device."
)

def simple_chat():
    # Send a prompt and print the response
    response = llm.chat("What is the capital of Italy?")
    print(f"AI: {response}")

# Run the application
App.run(simple_chat)

