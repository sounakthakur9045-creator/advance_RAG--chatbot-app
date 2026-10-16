from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv

load_dotenv()

session_id = input("session id : ")

chat_history = []


llm = ChatOllama(model = "llama3.2:3b",temperature = 0)

embedding_model = HuggingFaceEmbeddings(model_name = "sentence-transformers/all-MiniLM-L6-v2")
db = Chroma(
    persist_directory= "database/chroma_db",
    embedding_function=embedding_model,
    collection_metadata = {"hnsw:space" : "cosine"})

retriever = db.as_retriever(
    search_type = "similarity",
    search_kwargs = {"k" :5 , "filter" : {"session_id" : session_id}}
)

while True:
    user_question = input("write a question : ").strip()
    if user_question.lower() == "quit":
        break
    if chat_history:
        formatted_history = "\n".join([f"{msg.type}: {msg.content}" for msg in chat_history])
        rephrase_prompt = f"""Instructions:
        Rewrite the latest user message into a standalone search query by replacing pronouns (like 'he', 'she', 'it', 'they', 'that') with actual names or topics from the chat history.
        If the message is already clear, a greeting, or sharing new facts, return it EXACTLY as-is.do NOT reply to the user. Do NOT ask questions back. Return ONLY the text.
        Chat History:
        {formatted_history}
        User Message: {user_question}
        Standalone Output:"""
        
        standalone_question = llm.invoke(rephrase_prompt).content
        print(f"your new question : {standalone_question}")
    else:
        standalone_question = user_question

    relevent_chunks = retriever.invoke(standalone_question)
    context = "\n".join([chunk.page_content for chunk in relevent_chunks])
    final_prompt = "you are a helpful assistant who gives short to the point answer."
    if context:
        final_prompt += f"\n\nContext of previous chats:\n{context}"

    message_final = [SystemMessage(content = final_prompt),HumanMessage(content = standalone_question)]

    answer = llm.invoke(message_final).content

    print(f"Bot : {answer}")

    chat_history.append(HumanMessage(content = standalone_question))
    chat_history.append(AIMessage(content = answer))


    db.add_texts(
        texts = [f"user : {standalone_question} | Bot : {answer}"],
        metadatas = [{"session_id" : session_id}]
        )




