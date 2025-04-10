from langgraph.types import Command
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict, Literal
import uuid
import re
from google import genai

client = genai.Client(api_key="")

response = client.models.generate_content(
    model="gemini-2.0-flash", contents="Explain how AI works in a few words"
)

class MessageState(TypedDict):
    essay: str
    score: str
    messages: str

def get_content(data):
    print("======util======")
    print("before:"+data)
    decoded_text = bytes(data, "utf-8").decode("unicode_escape")
    return decoded_text


def essay_writer(state: MessageState) -> Command[Literal["essay_scorer",END]]:
    print("essay_writer")

    response = client.models.generate_content(
        model="gemini-2.0-flash", contents="Write an essay of 100 words about AI your essay should container lot technical details on how AI works"
    )
    #print("essay: "+str(response.text))
    state["essay"] = str(response.text)
    return Command(
        goto="essay_scorer",
        update={"essay":str(response.text)}
    )

def essay_scorer(state: MessageState) -> Command[Literal["essay_decision_maker",END]]:
    print("essay_scorer")

    essay = get_content(state["essay"])    

    response = client.models.generate_content(
        model="gemini-2.0-flash", contents="Score the given essay below on scale of 1 to 50 based on how good information is and how good the language. Your response should only include number from 1 to 50 nothing else should in response \n Essay: \n"+essay
    )
    #print("score"+str(response.text))
    state["score"] = str(response.text)

    return Command(
            goto="essay_decision_maker",
            update={"score":str(response.text)}
    )

def essay_decision_maker(state: MessageState) -> Command[Literal["essay_writer",END]]:
    print("essay_decision_maker")
    content = get_content(state["score"])
    print("score: "+content)
    score = int(get_content(state["score"]))
    if score > 25:
        return Command(
            goto=END ,
            update={"messages":"essay_decision_maker completed"}
        )
    else:
        state["messages"] = "Continue"
        return Command(
            goto="essay_writer",
            update={"messages":"Continue"}
        )

builder = StateGraph(MessageState)
builder.add_node(essay_writer)
builder.add_node(essay_scorer)
builder.add_node(essay_decision_maker)

builder.add_edge(START, "essay_writer")
builder.add_edge("essay_decision_maker",END)

network = builder.compile()
config = {
    "configuration":{
        "thread_id": uuid.uuid4()
    }
}
state = MessageState(messages="", essay="",score="")
for chunk in network.stream(state,config):
    print(chunk)
    print("=========")