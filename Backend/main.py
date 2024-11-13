import sys, getpass, os, io, re, uuid, requests, asyncio, getpass
from io import BytesIO
from pathlib import Path
import bs4, docx

from uuid import uuid4

from bs4 import BeautifulSoup
from pypdf import PdfReader
import pandas as pd


from flask import Flask, request, Blueprint
from flask_restful import Resource, Api
from flask import request, Response, jsonify, json, abort
from flask_restful import Resource, Api
from flask_cors import CORS

from langchain_core.documents import Document
from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings,
    GoogleGenerativeAI,
    ChatGoogleGenerativeAI,
)
from langchain_core.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain_google_vertexai import ChatVertexAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import (
    WebBaseLoader,
    PyPDFLoader,
    DirectoryLoader,
)
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import (
    create_history_aware_retriever,
    create_retrieval_chain,
    LLMChain,
)
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.messages import AIMessage, HumanMessage
from langchain.tools.retriever import create_retriever_tool
from langchain_core.messages import BaseMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent


from typing import Sequence
from typing_extensions import Annotated, TypedDict

from langsmith import Client
from langsmith.evaluation import evaluate


from dotenv import load_dotenv

dotenv_path = Path("./.env")
load_dotenv(dotenv_path=dotenv_path)

from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import certifi

ca = certifi.where()
USER_AGENT = os.environ.get("USER_AGENT")

"""
os.environ.get["LANGCHAIN_TRACING_V2"]
if not os.environ.get("LANGCHAIN_API_KEY"):
    print(os.environ.get("LANGCHAIN_API_KEY"))
    os.environ["LANGCHAIN_API_KEY"] = getpass.getpass()
"""

Client = MongoClient(
    os.environ.get("MONGO_DB_ATLAS_CONNECTION_STRING"),
    server_api=ServerApi("1", strict=False, deprecation_errors=True),
    connectTimeoutMS=30000,
    socketTimeoutMS=10000,
    tls=True,
    tlsCAFile=ca,
)

try:
    Client.admin.command("ping")
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


DbName = Client[f"{ os.environ.get('DB_NAME')}"]
Collection = DbName[f"{ os.environ.get('COLLECTION_NAME')}"]
AtlasVectorSearchIndexName = os.environ.get("ATLAS_VECTOR_SEARCH_INDEX_NAME")


from dotenv import load_dotenv

dotenv_path = Path("./.env")
load_dotenv(dotenv_path=dotenv_path)

app = Flask(__name__)
api_blueprint = Blueprint("api", __name__)


embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001", task_type="retrieval_document"
)
llm = GoogleGenerativeAI(
    model="models/gemini-1.5-flash", google_api_key=os.environ.get("GOOGLE_API_KEY")
)
embedding_dimensions = 768

vector_store = MongoDBAtlasVectorSearch(
    collection=Collection,
    embedding=embeddings,
    index_name=os.environ.get("ATLAS_VECTOR_SEARCH_INDEX_NAME"),
    relevance_score_fn="cosine",
)

retriever = vector_store.as_retriever()

system_prompt = (
    "You are a medical assistant for first aid and mental health related question-answering tasks. "
    "Use the following pieces of retrieved context to answer "
    "the question. If you don't know the answer, say that you "
    "don't know. Use three sentences maximum and keep the "
    "answer concise."
    "\n\n"
    "{context}"
)

contextualize_q_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."
)

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)


class Midas:
    def __init__(self):
        pass

    @api_blueprint.route("/api/v1", methods=["GET"])
    def ping():
        return jsonify(
            {"data": "Kephotho Solutions Flask API Alive And Well...... Bring It On!!!"}
        )

    @api_blueprint.route("/api/v1/pdf-file-loader", methods=["GET"])
    async def PDFFileLoader():
        documents = []
        if request.method == "GET":
            file_path = "/home/kephotho/Documents/FirstAider/PDFs/How_to_Listen_and_Support_Someone_in_Need_Well_Being_CDC.pdf"

            loader = PyPDFLoader(file_path)
            pages = []
            async for page in loader.alazy_load():
                pages.append(page)

                documents.append(
                    Document(page_content=page.page_content, metadata=page.metadata)
                )

            vector_store.add_documents(documents)

        return jsonify(response="Document is now AI ready!!!")

    @api_blueprint.route("/api/v1/pdf-docs-loader", methods=["GET"])
    def DirectoryLoader():
        if request.method == "GET":
            loader = DirectoryLoader(
                "/home/kephotho/Documents/FirstAider/PDFs",
                glob="**/*.pdf",
                # show_progress=True,
                # use_multithreading=True,
            )
            docs = loader.load()

            print(docs)

            # vector_store.add_documents(docs.page_content)

        return jsonify(response="Document is now AI ready!!!")

    @api_blueprint.route("/api/v1/web-loader", methods=["POST"])
    def WebLoader():
        if request.method == "POST":
            payload = request.form.get("link")
            print(payload)

            loader = WebBaseLoader(
                web_paths=(payload,),
                bs_kwargs=dict(parse_only=bs4.SoupStrainer()),
            )
            docs = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=200
            )
            splits = text_splitter.split_documents(docs)

            vector_store.add_documents(docs)

        return jsonify(response="Document is now AI ready!!!")

    @api_blueprint.route("/api/v1/pdf-loader", methods=["POST"])
    def PDFLoader():
        if request.method == "POST":
            documents = []

        if request.form.get("fileType") == "pdf":
            reader = PdfReader(request.files.get("file"))
            pages = len(reader.pages)

            for page in range(int(pages)):
                _page = reader.pages[page]
                documents.append(
                    Document(
                        page_content=re.sub(
                            r"[^a-zA-Z0-9\s]",
                            "",
                            _page.extract_text().replace("\n", " "),
                        )
                    )
                )

        elif request.form.get("fileType") == "docx":
            doc = docx.Document(request.files.get("file"))
            text = []
            for para in doc.paragraphs:
                text.append(para.text)
            documents.append(
                Document(
                    page_content=re.sub(
                        r"[^a-zA-Z0-9\s]", "", "\n".join(text.replace("\n", " "))
                    )
                )
            )

        elif request.form.get("fileType") == "html":
            htmlDoc = request.files.get("file").read()
            soup = BeautifulSoup(htmlDoc, "html.parser")
            text = soup.get_text().replace("\n", "")

            documents.append(
                Document(
                    page_content=text.replace("!@#$%^&*()[]{};:,./<>?\|`~-=_+“", " ")
                )
            )

        else:
            return jsonify(
                response="We currently have no support for the uploaded document. We only support .docx, .pdf, .txt"
            )

        vector_store.add_documents(documents)

        return jsonify(response="Document is AI Ready!!!")

    @api_blueprint.route("/api/v1/prompt", methods=["POST", "GET"])
    def Prompt():
        if request.method == "POST":
            payload = request.form.get("prompt")

            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system_prompt),
                    ("human", "{input}"),
                ]
            )

            question_answer_chain = create_stuff_documents_chain(llm, prompt)
            rag_chain = create_retrieval_chain(retriever, question_answer_chain)

            results = rag_chain.invoke({"input": payload})

            chat_history = []

            ai_msg_1 = rag_chain.invoke(
                {"input": payload, "chat_history": chat_history}
            )
            chat_history.extend(
                [
                    HumanMessage(content=payload),
                    AIMessage(content=ai_msg_1["answer"]),
                ]
            )

            second_question = "What are common ways of doing it?"
            ai_msg_2 = rag_chain.invoke(
                {"input": second_question, "chat_history": chat_history}
            )

            print(ai_msg_2["answer"])

            # We define a dict representing the state of the application.
            # This state has the same input and output keys as `rag_chain`.
            class State(TypedDict):
                input: str
                chat_history: Annotated[Sequence[BaseMessage], add_messages]
                context: str
                answer: str

            # We then define a simple node that runs the `rag_chain`.
            # The `return` values of the node update the graph state, so here we just
            # update the chat history with the input message and response.
            def call_model(state: State):
                response = rag_chain.invoke(state)

                return {
                    "chat_history": [
                        HumanMessage(state["input"]),
                        AIMessage(response["answer"]),
                    ],
                    "context": response["context"],
                    "answer": response["answer"],
                }

            # Our graph consists only of one node:
            workflow = StateGraph(state_schema=State)
            workflow.add_edge(START, "model")
            workflow.add_node("model", call_model)

            # Finally, we compile the graph with a checkpointer object.
            # This persists the state, in this case in memory.
            memory = MemorySaver()
            app_ = workflow.compile(checkpointer=memory)

            config = {"configurable": {"thread_id": "abc123"}}
            result = app_.invoke(
                {"input": payload},
                config=config,
            )

            result2 = app_.invoke(
                {"input": "What is one way of doing it?"},
                config=config,
            )
            response = {"Input": payload, "Answer": result["answer"]}
            print(response)
            print(result2["answer"])

            """
            chat_history = app_.get_state(config).values["chat_history"]
            for message in chat_history:
                message.pretty_print()

                print(message.pretty_print)    
            """

        return jsonify(response)


CORS(api_blueprint, origins=["*"], allow_headers=["Content-Type"])
app.register_blueprint(api_blueprint)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
