from logging.config import dictConfig
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import os 
import logging

from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.function_call_behavior import FunctionCallBehavior
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions.kernel_arguments import KernelArguments

from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)
#from .lights_plugin import LightsPlugin
from .azure_plugin import AzurePlugin

from .log_config import log_config

dictConfig(log_config)
logger = logging.getLogger("api-logger")

kernel = Kernel()
kernel.add_service(AzureChatCompletion(
    deployment_name=os.environ.get('OPENAI_DEPLOYMENT'),
    api_key=os.environ.get('OPENAI_API_KEY'),
    base_url=os.environ.get('OPENAI_BASE_URL'),
))
chat_completion : AzureChatCompletion = kernel.get_service(type=ChatCompletionClientBase)

kernel.add_plugin(
    AzurePlugin(),
    plugin_name="Azure",
)

execution_settings = AzureChatPromptExecutionSettings(tool_choice="auto")
execution_settings.function_call_behavior = FunctionCallBehavior.EnableFunctions(auto_invoke=True, filters={})

history = ChatHistory()
history.add_system_message("You are an Azure assistant named Labby. Your goal is to assist in saving money and setting up lab environments.")
history.add_system_message("Welcome, I am Labby! How can I help you today?")

app = FastAPI()

origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/echo")
def echo(data: dict):
    return {"echo": data}




@app.post("/chat")
async def chat(data: dict):
    logger.info(f"Chat request: {data}")
    history.add_user_message(data.get("question"))

    # Get the response from the AI
    result_arr = (await chat_completion.get_chat_message_contents(
        chat_history=history,
        settings=execution_settings,
        kernel=kernel,
        arguments=KernelArguments(),
    ))
    logger.info(f"Chat response arr: {result_arr}")
    history.add_message(result_arr[0])
    logger.info(f"Chat response: {result}")
    return {"result": f"{result}"}