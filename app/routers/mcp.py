from fastapi import APIRouter, Query
from langgraph.prebuilt import create_react_agent
import loguru
from app.tools.validate_aadhar import validate_aadhar_number

# Create agent
agent = create_react_agent(
    model="gpt-4",
    tools=[validate_aadhar_number],
    prompt="You are a helpful assistant",
    debug=True
)

router = APIRouter(tags=["Application"])

@router.get("/")
async def get_status(input: str = Query(...)):
    try:
        input_message = {"role": "user", "content": input}
        response = agent.invoke({"messages": [input_message]})
        # Safely extract content from last AI message
        messages = response.get("messages", [])
        final_message = next(
            (m.content for m in reversed(messages) if hasattr(m, "content") and m.content),
            "No valid response"
        )

        loguru.logger.info(f'Agent response: {final_message}')

        return {"message": final_message}
    except Exception as e:
        return {"error": str(e)}
