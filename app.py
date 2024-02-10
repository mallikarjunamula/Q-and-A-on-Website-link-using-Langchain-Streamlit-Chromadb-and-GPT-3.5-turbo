import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chains.question_answering import load_qa_chain
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv("openai_api_key")
st.subheader("Query Given Web Page Link:", divider='rainbow')
link = st.text_input("Enter your Web link here:")
query  = st.text_input("Enter your question here:")
def weblink_docs(link):
  loader = WebBaseLoader(link)
  loader.requests_kwargs = {'verify':False}
  data = loader.load()
  text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
  docs = text_splitter.split_documents(data)
  embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
  persist_directory = "mychromadb"
  vectordb = Chroma.from_documents(
      documents=docs, embedding=embeddings, persist_directory=persist_directory
  )
  vectordb.persist()
  db = Chroma.from_documents(docs, embeddings)
  matching_docs = db.similarity_search(query)
  return matching_docs

def webpage_qa(link, query):
  model_name = "gpt-3.5-turbo-1106"
  llm = ChatOpenAI(model_name=model_name, api_key=api_key)
  chain = load_qa_chain(llm, chain_type="stuff")
  similar_docs = weblink_docs(link)
  answer = chain.run(input_documents=similar_docs, question=query)
  return answer

# st.title("How to Query Webpages")
button = st.button("Generate Response")
if button and query and link:
    with st.spinner("Generating Response!..."):
        reply = webpage_qa(link, query)
    st.write(reply)