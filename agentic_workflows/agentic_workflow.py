from langgraph.types import Command
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict, Literal
import uuid
import re


class MessageState(TypedDict):
    messages: str

def get_content(data):
    print("data: "+data)
    return data

def agent_1(state: MessageState) -> Command[Literal["agent_2","agent_3",END]]:
    print("agent 1")
    return Command(
        goto="agent_2",
        update={"messages":"agent 1 completed"}
    )

def agent_2(state: MessageState) -> Command[Literal["agent_1","agent_3",END]]:
    print("agent 2")
    content = get_content(state["messages"])
    if "Continue" == content:
        state["messages"] = "Stop" 
        return Command(
            goto="agent_3",
            update={"messages":"Stop"}
        )
    else:
        return Command(
            goto="agent_3",
            update={"messages":"agent 2 completed"}
        )

def agent_3(state: MessageState) -> Command[Literal["agent_1","agent_3",END]]:
    print("agent 3")
    content = get_content(state["messages"])
    if "Stop" == content:
        return Command(
            goto=END ,
            update={"messages":"agent 3 completed"}
        )
    else:
        state["messages"] = "Continue"
        return Command(
            goto="agent_2",
            update={"messages":"Continue"}
        )

builder = StateGraph(MessageState)
builder.add_node(agent_1)
builder.add_node(agent_2)
builder.add_node(agent_3)

builder.add_edge(START, "agent_1")
builder.add_edge("agent_3",END)

network = builder.compile()
config = {
    "configuration":{
        "thread_id": uuid.uuid4()
    }
}
state = MessageState(messages=[""])
for chunk in network.stream(state,config):
    print(chunk)
    print("=========")