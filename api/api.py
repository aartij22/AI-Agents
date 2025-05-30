from termcolor import cprint
from llama_stack_client import Agent, LlamaStackClient
from api.summariser_custom_tool import summarize_context
from llama_stack_client.types.tool_group import McpEndpoint
from llama_stack_client.lib.agents.event_logger import EventLogger

client = LlamaStackClient(base_url="http://localhost:8321")

# register the mcp servers
client.toolgroups.register(
    toolgroup_id="mcp::gdrive",
    provider_id="model-context-protocol",
    mcp_endpoint=McpEndpoint(uri="http://0.0.0.0:3002/sse"),
)

# Create the agent
agent = Agent(
    client,
    model="llama3.2:3b",
    instructions="""You are a helpful assistant that can use tools to answer questions.""",
    tools=[
        "mcp::gdrive",
        summarize_context,
    ],  # add tools here. could be mcp servers or functions
)

user_prompts = [
    "Read the contents of <your_file_url>",
    "Generate a summary for this.",
    "Create a Google Doc document in folder id - <your_folder_id> with the title `<your_file_title>` and add the above summary to it.",
    "Share `<your_file_title>` doc with `your_email_id`",
]

session_id = agent.create_session("demo-session")

for prompt in user_prompts:
    cprint(f"User> {prompt}", "green")
    response = agent.create_turn(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        session_id=session_id,
    )

    for log in EventLogger().log(response):
        log.print()
