from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langgraph.types import Command
from langgraph.prebuilt import InjectedState, ToolNode
from typing import Annotated
from langchain.agents import (
    AgentExecutor,
    create_react_agent,
    create_tool_calling_agent
)
from langchain_core.tools import StructuredTool

class ChatBot:
    def __init__(self, instructions, llm, db_path) -> None:
        self.instructions = instructions
        self.llm = llm
        self.db_path = db_path
        self.flag_tool = False
        self.tool_type = ""
        pass

    def create_meet(self):
        """Use this every time you need to create a meeting"""

        print("chamou a func create")

        self.flag_tool = True
        self.tool_type = "create_meet"
        
    
    def delete_meet(self):
        """Use this every time you need to delete a meeting"""

        print("Chamou a func delete")

        self.flag_tool = True
        self.tool_type = "delete_meet"
    
    
    def reschedule_meet(self):
        """Use this every time you need to reschedule a meeting"""

        print("chamou a func reschedule")

        self.flag_tool = True
        self.tool_type = "reschedule_meet"
        

    def call_chat(self, state):
        
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",self.instructions
                ),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}"),
                MessagesPlaceholder("agent_scratchpad"),
            ]
        )
        runnable = prompt | self.llm

        pass_create_meet_tool = StructuredTool.from_function(
                name="meet_create_event",
                func=self.create_meet,
                description="Use this tool when you need to create a meeting")
    
        pass_delete_meet_tool = StructuredTool.from_function(
                name="meet_delete_event",
                func=self.delete_meet,
                description="Use this tool when you need to create a meeting")
        
        pass_reschedule_meet_tool = StructuredTool.from_function(
                name="meet_reschedule_event",
                func=self.reschedule_meet,
                description="Use this tool when you need to create a meeting")

        tools = [pass_create_meet_tool,pass_delete_meet_tool,pass_reschedule_meet_tool]
        tool_names = [tool.name for tool in tools]
        
        #agent = create_react_agent(self.llm, tools, prompt)
        agent = create_tool_calling_agent(llm=self.llm, tools=tools, prompt=prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools)

        with_message_history = RunnableWithMessageHistory(
            agent_executor,
            lambda: SQLChatMessageHistory(session_id=state["user_id"], connection=self.db_path),
            input_messages_key="input",
            history_messages_key="history",
        )

        message = state['message']

        answer = with_message_history.invoke(
            {
                "input": message,
                "tool_names": tool_names,
                "tools": tools
            },
            config={"configurable": {"session_id": state["user_id"]}},
        )
        
        print("State in chatbot: ",state)
        if self.flag_tool:
            previus_state = {"message": message, "answer": answer,"flag_use_tool":self.flag_tool,"tool_type":self.tool_type}
            self.flag_tool = False
            self.tool_type = ""
            return previus_state
        
        return {"message": message, "answer": answer,"flag_use_tool":self.flag_tool,"tool_type":self.tool_type}