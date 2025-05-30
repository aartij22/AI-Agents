# 🧠 AI agent using LLama Stack

This project provides a lightweight setup to run a local agent using the [Llama3.2 3B](https://ollama.com/library/llama3) model via [Ollama](https://ollama.com), integrated with custom MCP servers and function tools and an interactive interface through Streamlit.

---

## 🚀 Features

- Run LLM inference locally using Ollama
- Custom MCP server (e.g., Google Drive) and tool integration
- Interactive front-end with Streamlit

---

## 📦 Step 1: Installation and Setup

### 1.1 Install Ollama

Follow instructions from the [Ollama website](https://ollama.com) to install Ollama for your system.

Then download and run the model:

```bash
ollama pull llama3.2:3b
ollama run llama3.2:3b --keepalive 60m
```

### 1.2 Set Up Python Environment
Create a virtual environment and install dependencies using uv (or pip as an alternative):

```bash
python3 -m venv agent_venv
source agent_venv/bin/activate

pip install uv
uv pip install -r requirements.txt
```
📄 requirements.txt contains all necessary Python dependencies.

## 🦙 Step 2: Run Llama Stack
To start the Llama Stack (based on the Ollama and venv template):

```bash
INFERENCE_MODEL=llama3.2:3b uv run --with llama-stack llama stack build --template ollama --image-type venv --run
```
This runs a development LLM server using the specified model. For other methods, refer [here](https://llama-stack.readthedocs.io/en/latest/getting_started/detailed_tutorial.html).

## 🛠️ Step 3: Start MCP Server
### 🔑 Authentication & Setup
Follow the `Getting Started` and `Authentication` instructions in the official [GDrive MCP repository](https://github.com/modelcontextprotocol/servers-archived/blob/main/src/gdrive/README.md).

Once authentication is complete, start the custom MCP server:

```bash
python3 gdrive_tools.py
```
## 🛠️ Step 4: Add Your Custom Function Tool
Create your own custom tool functions and register them with the agent. Refer to the example provided in api/summariser_custom_tool.py.

## 🎛️ Step 5: Run the Streamlit App
Use the following command to start the web UI:

```bash
streamlit run streamlit_app.py
```
This provides a user-friendly interface to interact with the agent locally.

## ✅ Next Steps
- Add additional tools for your use case.
- Try complex use cases using bigger models
- Integrate memory and shields.
- Deploy with containerization or cloud runtimes.
