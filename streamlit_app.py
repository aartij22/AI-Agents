import streamlit_app as st
from api.summariser_custom_tool import generate_summary
from llama_stack_client import Agent, LlamaStackClient
from llama_stack_client.types.tool_group import McpEndpoint

def api_calling(user_prompt):
    response_stream = st.session_state.agent.create_turn(
        messages=[{"role": "user", "content": user_prompt}],
        session_id=st.session_state.session_id,
        stream=False
    )
    return response_stream

# --- Initialization ---
st.set_page_config(page_title="PIA Agent", page_icon="🤖")
st.title("🤖 PIA Agent")

# --- Session state ---
if "client" not in st.session_state:
    st.session_state.client = LlamaStackClient(base_url="http://localhost:8321")
    st.session_state.client.toolgroups.register(
        toolgroup_id="mcp::gdrive",
        provider_id="model-context-protocol",
        mcp_endpoint=McpEndpoint(uri="http://0.0.0.0:3001/sse"),
    )

if "agent" not in st.session_state:
    st.session_state.agent = Agent(
        st.session_state.client,
        model="llama3.2:3b",
        instructions="You are a helpful assistant that can use tools to answer questions.",
        tools=["mcp::gdrive", generate_summary],
        enable_session_persistence=True
    )

if "session_id" not in st.session_state:
    st.session_state.session_id = st.session_state.agent.create_session("session")

if 'user_input' not in st.session_state:
    st.session_state['user_input'] = []

if 'agent_response' not in st.session_state:
    st.session_state['agent_response'] = []

# --- Sidebar or Top Button for New Chat ---
if st.button("Start New Chat"):
    st.session_state.session_id = st.session_state.agent.create_session("session")
    st.session_state.user_input = []
    st.session_state.agent_response = []
    st.rerun()

# --- Display past messages with chat_message (not streamlit_chat.message) ---
for i in range(len(st.session_state['user_input'])):
    with st.chat_message("user"):
        st.markdown(st.session_state["user_input"][i])
    with st.chat_message("assistant"):
        st.markdown(st.session_state['agent_response'][i])

# --- Chat input ---
user_input = st.chat_input("Ask your question")

if user_input:
    # Show user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get and show response
    output = api_calling(user_prompt=user_input)

    # Save conversation
    st.session_state.user_input.append(user_input)
    st.session_state.agent_response.append(output.output_message.content)

    # Show assistant message
    with st.chat_message("assistant"):
        st.markdown(output.output_message.content)

        # display the inference or tool used in the background
        with st.expander("Tools used"):
            st.markdown(output.steps[0])