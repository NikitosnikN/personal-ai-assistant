# Architecture Documentation - Personal AI Assistant

## Overview
This project is a hierarchical multi-agent system designed to act as a personal assistant. It orchestrates multiple specialized sub-agents to handle various tasks such as email management, calendar scheduling, to-do list tracking, Slack communication, and web research. The system is built using **LangGraph** and **LangChain** and communicates with the user via **Telegram**, **Slack**, or **WhatsApp**.

## Core Components

### 1. Agents Architecture
The system follows a **Supervisor/Worker** pattern where a `Manager Agent` oversees several `Worker Agents`.

- **Manager Agent (`manager_agent`)**:
  - **Role**: Executive Personal Assistant.
  - **Responsibilities**: Analyzes user input, delegates tasks to appropriate sub-agents, verifies their output, and reports back to the user.
  - **Tools**: `SendMessage` (dynamically created to route messages to sub-agents).
  - **Memory**: Uses SQLite (`db/checkpoints.sqlite`) to maintain conversation state and context via `SqliteSaver`.

- **Worker Agents**:
  Each worker agent is a specialized agent with specific tools and responsibilities.
  - **Email Agent (`email_agent`)**:
    - **Tools**: `read_emails`, `send_email`, `find_contact_email`.
    - **Role**: Manages Gmail interactions.
  - **Calendar Agent (`calendar_agent`)**:
    - **Tools**: `get_calendar_events`, `add_event_to_calendar`, `find_contact_email`.
    - **Role**: Manages Google Calendar events.
  - **Notion Agent (`notion_agent`)**:
    - **Tools**: `get_my_todo_list`, `add_task_in_todo_list`.
    - **Role**: Manages Notion to-do lists.
  - **Slack Agent (`slack_agent`)**:
    - **Tools**: `get_slack_messages`, `send_slack_message`.
    - **Role**: Reads and sends Slack messages.
  - **Researcher Agent (`researcher_agent`)**:
    - **Tools**: `search_web`, `scrape_website_to_markdown`, `search_linkedin_tool`.
    - **Role**: Performs web research using Tavily and scrapes data.

### 2. Infrastructure & Frameworks
- **LangGraph**: Used for defining the agent workflow and state management.
- **LangChain**: Provides the base `create_react_agent` and LLM integration.
- **LLM Provider**: Configurable via environment variables (supports OpenAI, Anthropic, Google, Groq, OpenRouter).
- **Database**: SQLite is used for checkpointing agent state (memory).
- **Communication Channels**:
  - **Telegram**: Polling-based implementation in `app.py`.
    - **Security**: Implements a whitelist of allowed usernames configurable via `TELEGRAM_ALLOWED_USERS`.
  - **WhatsApp**: Webhook-based implementation using FastAPI in `app_whatsapp.py` (via Twilio).
  - **Slack**: SDK integration.

### 3. File Structure
- `app.py`: Main entry point for Telegram/Slack bot. Initializes the `PersonalAssistant` and runs the polling loop.
- `app_whatsapp.py`: FastAPI server for handling WhatsApp webhooks.
- `src/agents/`:
  - `personal_assistant.py`: Initializes the agent hierarchy and orchestrator.
  - `base/agent.py`: Wrapper around `create_react_agent`.
  - `base/agents_orchestrator.py`: Manages message routing between agents.
- `src/tools/`: Contains tool implementations for each service (Gmail, Calendar, Notion, etc.).
- `src/prompts/`: Contains system prompts defining the behavior of each agent.
- `src/utils.py`: Helper functions for authentication and LLM setup.

## Data Flow
1. **User Input**: Message received via Telegram/Slack/WhatsApp.
2. **Manager Processing**: `manager_agent` receives the message.
3. **Delegation**: Manager decides which sub-agent(s) to call and uses `SendMessage` tool.
4. **Execution**: Sub-agent executes the task using its specific tools (e.g., Google API, Notion API).
5. **Response**: Sub-agent returns result to Manager.
6. **Final Reply**: Manager synthesizes the results and sends a response back to the user.

## Extension Guide
To add a new capability:
1. **Create Tool**: Add new tool functions in `src/tools/`.
2. **Create Prompt**: Define the agent's persona in `src/prompts/`.
3. **Register Agent**: Add the new agent to `PersonalAssistant` class in `src/agents/personal_assistant.py`.
4. **Update Manager**: Ensure the manager knows about the new agent (handled dynamically by `AgentsOrchestrator`, but check `sub_agents` list).
