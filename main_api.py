from flask import Flask, request
from langchain_groq import ChatGroq
import requests
import json
from agent_state import State
from utils import createMeetAgent,DeleteMeetAgent,RescheduleMeetAgent
from main_ai_workflow import AgentWorkFlow
from chat_bot_node import ChatBot
from validate_agent_node import ValidateInfoAgent
import os
# creating a Flask app
app = Flask(__name__)

os.environ["GROQ_API_KEY"] = instructions = open(
    "secrets.txt", "r", encoding="utf-8"
).read()

# instructions = open("scripts/instrucao_dif.txt", "r", encoding="utf-8").read()
instructions = open(
    "scripts/malu_prompt_4.txt", "r", encoding="utf-8"
).read()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    max_tokens=5000,
    timeout=None,
    streaming=False,
    max_retries=1,
)

llm_s = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    max_tokens=5000,
    timeout=None,
    streaming=False,
    max_retries=1,
)

chatbot = ChatBot(instructions=instructions,llm=llm,db_path="sqlite:///sqlite.db")
validate_agent = ValidateInfoAgent(llm=llm_s,db_path="sqlite.db")

agent_workflow = AgentWorkFlow(state=State,
                      chatbot=chatbot,
                      validate_agent=validate_agent,
                      create_meet=createMeetAgent(),
                      delete_meet=DeleteMeetAgent(),
                      reschedule_meet=RescheduleMeetAgent())

graph = agent_workflow.build_graph()
                      

with open('wpp_conn_key.json', 'r') as file:
    wpp_creds = json.load(file)


def send_msg(url, token, number, msg_text):

    payload = json.dumps(
        {
            "phoneNumber": number,
            "text": msg_text,
        }
    )

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    data = requests.post(
        url=url,
        data=payload,
        headers=headers,
    )

    print(data)


@app.route("/", methods=["POST"])
def home():
    if request.method == "POST":
        response = request.json
        ai_message = "teste"
        return ai_message


@app.route("/maik", methods=["GET", "POST"])
def maik_response():
    if request.method == "POST":
        print(request.json)
        data = dict(request.json)
        client_msg = data["messageText"]["text"]
        number = data["recipient"]["id"]
        state = {
            "message": client_msg,
            "answer": "",
            "user_id":number,
            "flag_use_tool": False,  # Valor padrão para flag_use_tool
            "tool_type": "",         # Pode ser ajustado dependendo da ferramenta
            "valid_params": False,   # Pode ser alterado para True conforme necessário
        }
        result = graph.invoke(input=state)

        if not state['flag_use_tool']:
            send_msg(
                url=wpp_creds["url"], token=wpp_creds["token"], number=number, msg_text=str(result.get('answer'))
            )
            return str(result.get('answer')["output"])
        
        elif state['tool_type'] == 'reschedule_meet':
            send_msg(
                url=wpp_creds["url"], token=wpp_creds["token"], number=number, msg_text="Reagendando reunião"
            )

        elif state['tool_type'] == "create_meet":
            send_msg(
                url=wpp_creds["url"], token=wpp_creds["token"], number=number, msg_text="Criando reunião"
            )

        elif state['tool_type'] == 'delete_meet':
            send_msg(
                url=wpp_creds["url"], token=wpp_creds["token"], number=number, msg_text="Deletando reunião."
            )
    return "ok"


if __name__ == "__main__":
    app.run(debug=True)
