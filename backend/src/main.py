from logging.config import dictConfig
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import os 
import logging

from typing import Annotated

import tiktoken

from .log_config import log_config
from .azure_plugin import AzurePlugin

from semantic_kernel.agents.chat_completion_agent import ChatCompletionAgent
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.contents.utils.author_role import AuthorRole
# from semantic_kernel.filters.filter_types import FilterTypes
# from semantic_kernel.filters.prompts.prompt_render_context import PromptRenderContext
# from semantic_kernel.functions.kernel_function_decorator import kernel_function

from semantic_kernel.kernel import Kernel





dictConfig(log_config)
logger = logging.getLogger("api-logger")

def num_tokens_from_string(string: str, encoding_name: str ='cl100k_base') -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

# A helper method to invoke the agent with the user input
async def invoke_agent(agent: ChatCompletionAgent, input: str, chat: ChatHistory, streaming=False) -> any:
    """Invoke the agent with the user input."""
    chat.add_user_message(input)

    full_prompt = chat.to_prompt()
    print(f"System> current full prompt: {full_prompt}")
    tokens = num_tokens_from_string(full_prompt)
    print(f"System> current full prompt tokens: {tokens}")
    while(tokens > 2048 and len(chat.messages) > 1):
        print(f"removing a message...")
        chat.remove_message(chat.messages[1])
        full_prompt = chat.to_prompt()
        print(f"System> current full prompt: {full_prompt}")
        tokens = num_tokens_from_string(full_prompt)
        print(f"System> current full prompt tokens: {tokens}")

    if (tokens > 2048) and len(chat.messages) == 1:
        raise Exception("The prompt is too long and cannot be processed")

    print(f"# {AuthorRole.USER}: '{input}'")

    if streaming:
        contents = []
        content_name = ""
        async for content in agent.invoke_stream(chat):
            content_name = content.name
            contents.append(content)
        message_content = "".join([content.content for content in contents])
        print(f"# {content.role} - {content_name or '*'}: '{message_content}'")
        chat.add_assistant_message(message_content)
    else:
        async for content in agent.invoke(chat):
            print(f"# {content.role} - {content.name or '*'}: '{content.content}'")
        chat.add_message(content)

    return content


history = ChatHistory()
history.add_system_message("You are an Azure assistant named Labby. Your goal is to assist in saving money and setting up lab environments.")
history.add_system_message("Welcome, I am Labby! How can I help you today?")
kernel = Kernel()

service_id = "agent"
kernel.add_service(AzureChatCompletion(service_id=service_id))

settings = kernel.get_prompt_execution_settings_from_service_id(service_id=service_id)
# Configure the function choice behavior to auto invoke kernel functions
settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

kernel.add_plugin(plugin=AzurePlugin(), plugin_name="azure")

agent = ChatCompletionAgent(
    service_id="agent", kernel=kernel, name="Azure-Assistant", instructions="You are an assistant AI that helps find information about Azure resources", execution_settings=settings
)


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

@app.post("/resetchat")
async def resetchat():
    global history
    history = ChatHistory()
    history.add_system_message("You are an Azure assistant named Labby. Your goal is to assist in saving money and setting up lab environments.")
    history.add_system_message("Welcome, I am Labby! How can I help you today?")
    return {"result": "Chat history has been reset."}

@app.post("/chat")
async def chat(data: dict):
    logger.info(f"Chat request: {data}")
    question = data.get("question")

    # Get the response from the AI
    result = await invoke_agent(agent, question, history)
    logger.info(f"Chat response: {result}")
    return {"result": f"{result}"}