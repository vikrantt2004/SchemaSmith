import asyncio

from app.agent import run_agent


async def main():

    print("\n========== SchemaSmith AI ==========\n")

    requirements = input(
        "Describe your application requirements:\n> "
    )

    print("\nSchemaSmith is analyzing your requirements...\n")

    result = await run_agent(requirements)

    print("\n========== AGENT RESPONSE ==========\n")

    for message in result["messages"]:

        if message.type == "ai" and message.content:
            print(message.content)


if __name__ == "__main__":
    asyncio.run(main())