from typing import Literal
from langgraph.types import Command
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field
from typing import List
import re
import json
from get_date import GetDate
import sqlite3
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.schema import Document
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains.question_answering import load_qa_chain


class ClientInfo(BaseModel):
    name: str = Field(description='Nome completo do cliente')
    email: str = Field(description='Email do cliente')
    tipo_corte: str = Field(description='Se será corte de cabelo, barba ou ambos')
    dia: str = Field(description='Dia do serviço')
    horario: str = Field(description='Horário do serviço')


class ValidateInfoAgent:
    def __init__(self, llm,db_path):
        self.llm = llm
        self.db_path = db_path
        self.text = ""
        pass

    def get_text(self,state):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        rows = cur.execute('SELECT message FROM message_store where session_id = {}'.format(state["user_id"]) ).fetchall()
        conn.close()
        for row in rows:
            self.text = self.text + "\n " + str(json.loads(row[0]).get("type")) + " : " + str(json.loads(row[0]).get("data").get("content"))

    def sum_text(self):
        # Use HuggingFaceEmbeddings to generate embeddings
        modelo_embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        # Create a document from the text
        doc = Document(page_content=self.text, metadata={})

        # Create the FAISS vector store
        vectorstore = FAISS.from_documents([doc], embedding=modelo_embeddings)

        # Load the QA chain
        qa_chain = load_qa_chain(self.llm, chain_type="map_reduce")

        # Create a RetrievalQA object by passing both the vector store and the QA chain
        qa = RetrievalQA(combine_documents_chain=qa_chain, retriever=vectorstore.as_retriever())

        # Ask a question

        prompt = """
                <Role>
                Você é um leitor com mais de 10 anos de experiencia
                <Role/>
                <Instructions>
                Seu trabalho é todos os parametros da forma correta.
                **Nunca invente parametros**
                **Nunca preencha os parametros que não estiverem no texto**
                **Responda em pt-BR**
                **Sua resposta deve conter apenas o nome, email, tipo de corte, dia, horario
                <Instructions/>
                """
        
        pergunta = "me diga apenas o Nome, Email, Tipo do corte, Dia e Horario"
        resposta = qa.run(prompt)

        return resposta
    
    def call_chat(self,state):

        self.get_text(state=state) 

        sum_text = self.sum_text()  
        print(sum_text)   

        prompt = """
                <Role>
                Você é um leitor com mais de 10 anos de experiencia
                <Role/>
                <Instructions>
                Seu trabalho é ler {input} e preencher todos os parametros da forma correta.
                **Nunca invente parametros**
                **Nunca preencha os parametros que não estiverem no texto**
                **Responda em pt-BR**
                <Instructions/>
                """

        # adicionar no chat promptTemplate tools
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    prompt,
                ),
                ("human", "{input}"),
            ]
        )


        new_llm = self.llm.with_structured_output(ClientInfo)
        chain = prompt | new_llm 
        answer =  chain.invoke(sum_text)

        answer.horario = GetDate().extrair_hora(answer.horario)
        answer.dia = GetDate().proximo_dia(answer.dia)

        valid_parameters = {"name":False,"email":False,"tipo_corte":False,"dia":False,"horario":False}
        if state["flag_use_tool"]:

            if not any(str.isdigit(c) for c in answer.name):
                valid_parameters.update({"name":True})

            regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

            if re.fullmatch(regex, answer.email):
                valid_parameters.update({"email":True})

            if not any(str.isdigit(c) for c in answer.tipo_corte):
                valid_parameters.update({"tipo_corte":True})
            
            if str.isdigit(str(answer.dia)):
                valid_parameters.update({"dia":True})

            if str.isdigit(str(answer.horario)):
                valid_parameters.update({"horario":True})

            if all(value == True for value in valid_parameters.values()):
                print("VALID")
                return {"answer":"VALID","valid_params":True}
            
            elif not all(value == True for value in valid_parameters.values()):
                print("NOT_VALID")
                #print(answer)
                return {"answer":"NOT_VALID","valid_params":False}


        