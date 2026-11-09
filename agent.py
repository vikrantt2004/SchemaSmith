import os
import sys

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.mcp import MCPAdapter

from app.tools import validate_sql

load_dotenv()

# Windows and Linux/macOS launch commands
if sys.platform == "win32":
    command = "cmd.exe"
    args = [
        "/c",
        "npx",
        "-y",
        "@microsoft/postgres-mcp",
        "run"
    ]
else:
    command = "npx"
    args = [
        "-y",
        "@microsoft/postgres-mcp",
        "run"
    ]

MCP_CONFIG = {
    "mcpServers": {
        "postgres": {
            "command": command,
            "args": args,
            "transport": "stdio"
        }
    }
}


SYSTEM_PROMPT = """
You are SchemaSmith, an AI database schema design agent.

Your job is to convert natural-language application requirements
into well-designed PostgreSQL database schemas.

Follow this workflow:

1. Understand the user's application requirements.
2. Identify entities, attributes, and relationships.
3. Consider primary keys, foreign keys, constraints,
   normalization, and data types.
4. Use PostgreSQL MCP tools when database inspection is required.
5. If inspecting the database, first list connection profiles
   and connect using the profile named schemasmith_local.
6. Generate PostgreSQL-compatible CREATE TABLE statements.
7. Call validate_sql to check the generated SQL syntax.
8. If validation fails, correct the SQL and validate again.
9. Present the final SQL with an explanation of the schema.

IMPORTANT:
- Do not invent database inspection results.
- Do not execute database modifications.
- Do not call any write or destructive database tools.
- Only generate and validate SQL in this version.
- Explain important design decisions.
"""


def get_agent(mcp_tools):

    model = ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        temperature=0
    )

    # Allow only connection, inspection and read-only tools.
    allowed_tools = {
        "postgres_mcp_list_connection_profiles",
        "postgres_mcp_connect",
        "postgres_mcp_disconnect",
        "postgres_mcp_list_databases",
        "postgres_mcp_db_context",
        "postgres_mcp_query"
    }

    database_tools = [
        tool for tool in mcp_tools
        if tool.name in allowed_tools
    ]

    # Display the actual tools discovered from Microsoft MCP.
    print("\nMicrosoft PostgreSQL MCP tools discovered:")
    for tool in mcp_tools:
        print("-", tool.name)

    all_tools = database_tools + [validate_sql]

    agent = create_agent(
        model=model,
        tools=all_tools,
        system_prompt=SYSTEM_PROMPT
    )

    return agent


async def run_agent(requirements):

    async with MCPAdapter(MCP_CONFIG) as adapter:

        # Discover tools from Microsoft's PostgreSQL MCP server.
        mcp_tools = await adapter.list_tools()

        agent = get_agent(mcp_tools)

        result = await agent.ainvoke({
            "messages": [
                {
                    "role": "user",
                    "content": requirements
                }
            ]
        })

        return result