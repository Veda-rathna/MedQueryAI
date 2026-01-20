"""
System and user prompts for the Drug Information Chatbot
"""

SYSTEM_PROMPT = """You are a drug labeling assistant.

You must answer ONLY using the provided context extracted from official prescribing information PDFs.

Rules:
- Do not use prior knowledge
- Do not guess or infer
- Do not provide medical advice
- Use the exact terminology from the document
- If information is not present, respond:
  "This information is not available in the provided prescribing document."

Always cite page numbers in the format:
(Page X)

If multiple sections are used, cite multiple pages."""


def create_user_prompt(retrieved_chunks: list, conversation_history: list, question: str) -> str:
    """
    Create user prompt with context, history, and question
    
    Args:
        retrieved_chunks: List of retrieved chunks with metadata
        conversation_history: Last 5 interactions
        question: Current user question
    
    Returns:
        Formatted prompt string
    """
    # Format retrieved chunks
    context_parts = []
    for i, chunk in enumerate(retrieved_chunks, 1):
        page = chunk.get('metadata', {}).get('page', 'Unknown')
        section = chunk.get('metadata', {}).get('section', 'Unknown Section')
        text = chunk.get('text', '')
        context_parts.append(f"[Chunk {i} - Page {page} - {section}]\n{text}\n")
    
    context_text = "\n".join(context_parts)
    
    # Format conversation history
    history_text = ""
    if conversation_history:
        history_parts = []
        for msg in conversation_history:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            history_parts.append(f"{role.upper()}: {content}")
        history_text = "\n".join(history_parts)
    
    # Build complete prompt
    prompt = f"""Extracted Context:
{context_text}

Conversation History:
{history_text if history_text else "No previous conversation"}

User Question:
{question}

Answer using ONLY the extracted context above."""
    
    return prompt
