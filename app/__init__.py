import uuid

from dotenv import load_dotenv
# Quart
from quart import Quart
from quart import g
from quart import request

from .models.conversations import Conversation
from .models.conversations import Message
from .ollama_client import OllamaClient
from .skills.manager import SkillManager


load_dotenv()

conversations = {}
llm_client = OllamaClient.from_env()
skill_manager = SkillManager()

# TODO: refactor into skill loader

def media_key(key):
    return "Pressed next"

def run_command(command):
    return f"Ran '{command}'"

skill_manager.register_skill("media_key", media_key)
skill_manager.register_skill("run_command", run_command)


system_prompt = """
You are an assistant, who speaks in a friendly, laid-back tone. Use concise
responses, keeping them to at most a couple sentences, unless otherwise
necessary.

You are provided with several "skills" to assist with fulfilling user requests.
When a skill is required, wait before responding and call it using the
following syntax:

replace_with_skill_name(`argument 1`, `argument 2`)

Arguments must be enclosed with backticks (`). The system will then provide you
with relevant output data to write a response to the user.

Be careful when issuing skill calls; it is easy to make mistakes and malformed
calls will be ignored. Bad examples:
- media_key(next): The `next` argument was not enclosed in backticks
- run_command("echo hello"): Double-qoutes (") were used instead of backticks (`)

Available skills:

media_key(key)
Description: Control media playback on the user's system
Arguments:
- key: the key to press (play|pause|mute|stop|next|previous)
Usage Examples:
- media_key(`next`)

run_command(command)
Description: Run a command on the user's system
Arguments:
- command: The Linux shell command to run
Usage Examples:
- run_command(`cat ~/Documents/hello.txt`)
"""

app = Quart(__name__)


@app.get("/conversations")
async def list_conversations():
    return list(conversations.keys())

@app.post("/conversations")
async def create_conversation():
    conversation_id = uuid.uuid4().hex
    g.conversations[conversation_id] = Conversation()

    g.llm_client.preload()

    return { "conversation_id": conversation_id }

@app.get("/conversations/<conversation_id>")
async def list_messages(conversation_id):
    conversation = g.conversations.get(conversation_id)
    if conversation is None:
        return "", 404

    return conversation.to_dict()

@app.post("/conversations/<conversation_id>")
async def send_message(conversation_id):
    conversation = g.conversations.get(conversation_id)
    if conversation is None:
        return "", 404

    # Get user message content
    request_data = await request.get_json()
    user_message_content = request_data["content"]

    # Store user message
    user_message = Message.user(user_message_content)
    conversation.messages.append(user_message)
    print(f'User: {user_message.content}')

    # Perform chat request
    system_message = Message.system(system_prompt)
    system_conversation = [system_message, *conversation.messages]
    assistant_message_content = await g.llm_client.chat(system_conversation)
    commands = g.skill_manager.parse_skill_commands(assistant_message_content)

    # Store assistant message
    assistant_message = Message.assistant(assistant_message_content)
    conversation.messages.append(assistant_message)
    print(f'LLM: {assistant_message.content}')

    # Process commands
    if commands:
        command_response = Message.system("\n\n".join([
            f"Command: {format_command(c)}\nResult: {g.skill_manager.execute_command(c)}"
            for c in commands
        ]))
        system_conversation = [system_message, *conversation.messages, command_response]
        assistant_message_content = await g.llm_client.chat(system_conversation)

        # Store assistant message
        assistant_message = Message.assistant(assistant_message_content)
        conversation.messages.append(assistant_message)
        print(f'LLM: {assistant_message.content}')

    return {
        "message": assistant_message,
        "commands": [command.to_dict() for command in commands]
    }

def format_command(command):
    arguments_str = ", ".join([f"`{arg}`" for arg in command.arguments])
    return f"Command: {command.name}({arguments_str})"

@app.before_request
def before_request():
    g.conversations = conversations
    g.llm_client = llm_client
    g.skill_manager = skill_manager


def run():
    app.run(host="0.0.0.0", port=8000)
