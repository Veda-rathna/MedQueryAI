"""
Conversation Memory Module - Manages chat history per session
Implements sliding window memory for context-aware responses
"""
from typing import List, Dict, Optional
from collections import defaultdict
from datetime import datetime
import config


class ConversationMemory:
    """
    Manages conversation history with sliding window
    Stores separate histories per session
    """
    
    def __init__(self, max_history: int = config.MAX_HISTORY_MESSAGES):
        """
        Initialize memory manager
        
        Args:
            max_history: Maximum number of message pairs to store
        """
        self.max_history = max_history
        self.sessions = defaultdict(list)
        self.session_metadata = {}
    
    def add_message(self, session_id: str, role: str, content: str):
        """
        Add a message to session history
        
        Args:
            session_id: Unique session identifier
            role: 'user' or 'assistant'
            content: Message content
        """
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        
        self.sessions[session_id].append(message)
        
        # Trim to max history (keep most recent)
        if len(self.sessions[session_id]) > self.max_history * 2:
            # Keep last max_history pairs
            self.sessions[session_id] = self.sessions[session_id][-(self.max_history * 2):]
    
    def get_history(self, session_id: str, max_messages: Optional[int] = None) -> List[Dict]:
        """
        Get conversation history for a session
        
        Args:
            session_id: Session identifier
            max_messages: Optional limit on number of messages to return
        
        Returns:
            List of message dictionaries
        """
        history = self.sessions.get(session_id, [])
        
        if max_messages:
            return history[-max_messages:]
        
        return history
    
    def get_last_n_pairs(self, session_id: str, n: int = 5) -> List[Dict]:
        """
        Get last N message pairs (user + assistant)
        
        Args:
            session_id: Session identifier
            n: Number of pairs to retrieve
        
        Returns:
            List of messages (up to n*2 messages)
        """
        history = self.sessions.get(session_id, [])
        return history[-(n * 2):]
    
    def clear_session(self, session_id: str):
        """
        Clear history for a session
        
        Args:
            session_id: Session identifier
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
        if session_id in self.session_metadata:
            del self.session_metadata[session_id]
    
    def set_session_metadata(self, session_id: str, metadata: Dict):
        """
        Store metadata about a session (e.g., document name)
        
        Args:
            session_id: Session identifier
            metadata: Dictionary of metadata
        """
        self.session_metadata[session_id] = metadata
    
    def get_session_metadata(self, session_id: str) -> Dict:
        """
        Get metadata for a session
        
        Args:
            session_id: Session identifier
        
        Returns:
            Metadata dictionary
        """
        return self.session_metadata.get(session_id, {})
    
    def list_active_sessions(self) -> List[str]:
        """
        List all active session IDs
        
        Returns:
            List of session IDs
        """
        return list(self.sessions.keys())
    
    def format_history_for_llm(self, session_id: str) -> List[Dict]:
        """
        Format history for LLM consumption (OpenAI format)
        
        Args:
            session_id: Session identifier
        
        Returns:
            List of message dicts with 'role' and 'content'
        """
        history = self.get_last_n_pairs(session_id, self.max_history)
        
        # Return in OpenAI format (just role and content)
        return [
            {'role': msg['role'], 'content': msg['content']}
            for msg in history
        ]


# Global memory instance
memory = ConversationMemory()


def get_memory() -> ConversationMemory:
    """Get the global memory instance"""
    return memory


if __name__ == "__main__":
    # Test memory
    mem = ConversationMemory(max_history=3)
    
    session = "test-session-1"
    
    # Add messages
    mem.add_message(session, "user", "What is the dosage?")
    mem.add_message(session, "assistant", "The dosage is 15mg once daily. (Page 9)")
    mem.add_message(session, "user", "Are there any contraindications?")
    mem.add_message(session, "assistant", "Yes, see contraindications section. (Page 15)")
    
    # Get history
    history = mem.get_history(session)
    print(f"Total messages: {len(history)}")
    
    for msg in history:
        print(f"{msg['role'].upper()}: {msg['content']}")
    
    # Test trimming
    for i in range(10):
        mem.add_message(session, "user", f"Question {i}")
        mem.add_message(session, "assistant", f"Answer {i}")
    
    print(f"\nAfter many messages: {len(mem.get_history(session))} messages stored")
