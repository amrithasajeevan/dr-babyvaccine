from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from PyPDF2 import PdfReader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain

import os
from langchain.llms import OpenAI

os.environ["OPENAI_API_KEY"] = "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"

# Read text from PDF
pdfreader = PdfReader(r"C:\Users\User\babycalender\babyvaccinepro\Dr.baby.pdf")
raw_text = ''
for page in pdfreader.pages:
    content = page.extract_text()
    if content:
        raw_text += content

# Split the text using Character Text Splitter
text_splitter = CharacterTextSplitter(
    separator="\n",
    chunk_size=800,
    chunk_overlap=200,
    length_function=len,
)
texts = text_splitter.split_text(raw_text)

# Download embeddings from OpenAI
embeddings = OpenAIEmbeddings()
document_search = FAISS.from_texts(texts, embeddings)

# Load question-answering chain
chain = load_qa_chain(OpenAI(), chain_type="stuff")

# Initialize ChatterBot
chatbot = ChatBot("DoctorBaby")
trainer = ListTrainer(chatbot)  # Change ChatterBotCorpusTrainer to ListTrainer
trainer.train("chatterbot.corpus.english")  # Train with English language data

def get_response(user_input):
    # Custom logic for responses based on user input
    if user_input.lower() in ["hi", "hello", "hey", "hy","hai"]:
        return "Hello, welcome to Dr Baby. How can I assist you today!"
    elif user_input.lower() in ["bye", "by", "thank you", "thanks"]:
        return "bye"
    else:
        # Retrieve documents based on user input
        docs = document_search.similarity_search(user_input)
        # Use the question-answering chain to get a response
        return chain.run(input_documents=docs, question=user_input)

# Example of using ChatterBot for responses
while True:
    user_input = input("You: ")
    if user_input.lower() == 'exit':
        break
    bot_response = get_response(user_input)
    print("Dr Baby:", bot_response)