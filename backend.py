import os
import json
from datetime import datetime
from typing import List, Dict, Any, Generator, Tuple
from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv()

PERSIST_DIR = "database/chroma_db"
SESSIONS_FILE = "database/sessions_meta.json"

class ChatBackend:
    def __init__(self, model_name: str = "llama3.2:3b", embedding_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.embedding_name = embedding_name
        
        # Initialize LLM
        self.llm = ChatOllama(model=self.model_name, temperature=0)
        
        # Initialize Embeddings & Chroma DB
        self.embedding_model = HuggingFaceEmbeddings(model_name=self.embedding_name)
        self.db = Chroma(
            persist_directory=PERSIST_DIR,
            embedding_function=self.embedding_model,
            collection_metadata={"hnsw:space": "cosine"}
        )
        
        # Ensure session metadata store exists
        self._init_session_meta()

    def _init_session_meta(self):
        os.makedirs("database", exist_ok=True)
        if not os.path.exists(SESSIONS_FILE):
            self._save_session_meta({})

    def _get_session_meta(self) -> Dict[str, Any]:
        if os.path.exists(SESSIONS_FILE):
            try:
                with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_session_meta(self, meta: Dict[str, Any]):
        with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        Lists all sessions combining stored metadata and existing session_ids in Chroma.
        """
        meta = self._get_session_meta()
        chroma_sessions = set()
        
        try:
            res = self.db._collection.get(include=["metadatas"])
            if res and res.get("metadatas"):
                for m in res["metadatas"]:
                    if m and "session_id" in m and m["session_id"]:
                        chroma_sessions.add(str(m["session_id"]))
        except Exception as e:
            print(f"Error fetching sessions from Chroma: {e}")

        # Sync any newly found sessions from Chroma into meta
        updated = False
        for s_id in chroma_sessions:
            if s_id not in meta:
                meta[s_id] = {
                    "id": s_id,
                    "title": s_id.capitalize() if s_id != "default" else "New Chat",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "messages": []
                }
                updated = True

        if updated:
            self._save_session_meta(meta)

        # Return list sorted by updated_at descending
        sessions_list = list(meta.values())
        sessions_list.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return sessions_list

    def create_session(self, title: str = "New Chat", session_id: str = None) -> str:
        """
        Creates a new session record and returns its ID.
        """
        if not session_id:
            session_id = f"chat_{int(datetime.now().timestamp())}"
        
        meta = self._get_session_meta()
        meta[session_id] = {
            "id": session_id,
            "title": title,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": []
        }
        self._save_session_meta(meta)
        return session_id

    def update_session_title(self, session_id: str, new_title: str):
        meta = self._get_session_meta()
        if session_id in meta:
            meta[session_id]["title"] = new_title
            meta[session_id]["updated_at"] = datetime.now().isoformat()
            self._save_session_meta(meta)

    def delete_session(self, session_id: str):
        """
        Deletes session metadata and its documents from Chroma DB.
        """
        meta = self._get_session_meta()
        if session_id in meta:
            del meta[session_id]
            self._save_session_meta(meta)
            
        try:
            self.db._collection.delete(where={"session_id": session_id})
        except Exception as e:
            print(f"Error deleting documents for session {session_id}: {e}")

    def load_session_history(self, session_id: str) -> List[Dict[str, str]]:
        """
        Loads past chat messages for this session from session store or Chroma.
        Returns a list of {"role": "user"|"assistant", "content": ...}
        """
        meta = self._get_session_meta()
        # If stored in session metadata with messages, use that
        if session_id in meta and meta[session_id].get("messages"):
            return meta[session_id]["messages"]

        # Otherwise load and parse from Chroma DB
        messages = []
        try:
            res = self.db._collection.get(
                where={"session_id": session_id},
                include=["documents", "metadatas"]
            )
            docs = res.get("documents", [])
            for doc in docs:
                if " | Bot : " in doc:
                    parts = doc.split(" | Bot : ", 1)
                    user_part = parts[0]
                    bot_part = parts[1]
                    if user_part.startswith("user : "):
                        user_text = user_part[len("user : "):].strip()
                    else:
                        user_text = user_part.strip()
                    bot_text = bot_part.strip()
                    messages.append({"role": "user", "content": user_text})
                    messages.append({"role": "assistant", "content": bot_text})
            
            # Cache parsed messages into meta for persistent fast ordering
            if session_id in meta and messages:
                meta[session_id]["messages"] = messages
                self._save_session_meta(meta)
        except Exception as e:
            print(f"Error loading session history: {e}")
            
        return messages

    def get_standalone_question(self, user_question: str, history_messages: List[Dict[str, str]]) -> str:
        """
        Rephrases question if history exists, identical to retrieval_pipeline.py logic.
        """
        if not history_messages:
            return user_question

        formatted_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history_messages])
        rephrase_prompt = f"""Instructions:
        Rewrite the latest user message into a standalone search query by replacing pronouns (like 'he', 'she', 'it', 'they', 'that') with actual names or topics from the chat history.
        If the message is already clear, a greeting, or sharing new facts, return it EXACTLY as-is.do NOT reply to the user. Do NOT ask questions back. Return ONLY the text.
        Chat History:
        {formatted_history}
        User Message: {user_question}
        Standalone Output:"""

        standalone_question = self.llm.invoke(rephrase_prompt).content.strip()
        return standalone_question

    def retrieve_context(self, session_id: str, standalone_question: str) -> Tuple[List[str], str]:
        """
        Retrieves relevant chunks from Chroma DB for the current session.
        """
        retriever = self.db.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5, "filter": {"session_id": session_id}}
        )
        relevant_chunks = retriever.invoke(standalone_question)
        chunks_text = [chunk.page_content for chunk in relevant_chunks]
        context = "\n".join(chunks_text)
        return chunks_text, context

    def prepare_chat_turn(
        self,
        session_id: str,
        user_question: str,
        history_messages: List[Dict[str, str]]
    ) -> Tuple[str, List[str], Generator[str, None, None]]:
        """
        Prepares standalone query and retrieved context once, then returns:
        (standalone_question, chunks, stream_generator)
        """
        # Step 1: Standalone query rephrasing
        standalone_question = self.get_standalone_question(user_question, history_messages)
        
        # Step 2: Context Retrieval
        chunks, context = self.retrieve_context(session_id, standalone_question)
        
        # Step 3: Final prompt assembly
        final_prompt = "you are a helpful assistant who gives short to the point answer."
        if context:
            final_prompt += f"\n\nContext of previous chats:\n{context}"

        message_final = [
            SystemMessage(content=final_prompt),
            HumanMessage(content=standalone_question)
        ]

        # Step 4: Stream Generator that saves upon completion
        def stream_generator():
            full_answer = ""
            for chunk in self.llm.stream(message_final):
                token = chunk.content
                full_answer += token
                yield token

            # Step 5: Save interaction to Chroma DB (identical to retrieval_pipeline.py)
            self.db.add_texts(
                texts=[f"user : {standalone_question} | Bot : {full_answer}"],
                metadatas=[{"session_id": session_id}]
            )

            # Update session messages and title in metadata
            meta = self._get_session_meta()
            if session_id not in meta:
                meta[session_id] = {
                    "id": session_id,
                    "title": user_question[:30] + ("..." if len(user_question) > 30 else ""),
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "messages": []
                }
            
            if "messages" not in meta[session_id]:
                meta[session_id]["messages"] = []
                
            meta[session_id]["messages"].append({"role": "user", "content": user_question})
            meta[session_id]["messages"].append({"role": "assistant", "content": full_answer})
            
            # Auto-title if default or new
            curr_title = meta[session_id].get("title", "")
            if curr_title in ["New Chat", "default", ""] or curr_title.startswith("chat_"):
                meta[session_id]["title"] = user_question[:28] + ("..." if len(user_question) > 28 else "")

            meta[session_id]["updated_at"] = datetime.now().isoformat()
            self._save_session_meta(meta)

        return standalone_question, chunks, stream_generator()
