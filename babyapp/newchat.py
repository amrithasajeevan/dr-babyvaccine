from PyPDF2 import PdfReader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
import os
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI

os.environ["OPENAI_API_KEY"] = "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"

# provide the path of  pdf file/files.
pdfreader = PdfReader(r"C:\Users\User\babycalender\babyvaccinepro\Dr.baby.pdf")

# read text from pdf
raw_text = ''
for i, page in enumerate(pdfreader.pages):
    content = page.extract_text()
    if content:
        raw_text += content

# We need to split the text using Character Text Split such that it sshould not increse token size
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

document_search

chain = load_qa_chain(OpenAI(), chain_type="stuff")


def get_response(user_input):
    bot_response = ""  # Initialize bot_response with an empty string

    if user_input.strip().lower() in ["hi", "hello", "hey", "hy", "hi ruby", "hello ruby", "hey ruby", "hy ruby"]:
        bot_response = "Hello, welcome to Doctor Baby. How can I assist you today!"
    elif user_input.strip().lower() in ["bye", "by", "bye ruby", "by ruby", "thank you", "thanks"]:
        bot_response = "bye"
    else:
        question = user_input.strip()  # Extract and clean the question from user input
        if len(question) < 4:
            bot_response = "Please enter a valid question!"
        else:
            docs = document_search.similarity_search(user_input)
            bot_response = chain.run(input_documents=docs, question=question)

    return bot_response


while True:
    user_input = input("You: ")
    if user_input.lower() in ['exit', 'quit']:
        break

    bot_response = get_response(user_input)

    print("Doctor Baby:", bot_response)