"""
System and user prompts for the Drug Information Chatbot
"""

SYSTEM_PROMPT = """You are a precise drug information assistant. Answer ONLY using the provided context from prescribing information.

Rules:
- Use exact terminology and values from context
- Include route of administration for dosages
- Mention special populations or conditions when relevant
- Cite page numbers AND section numbers from the context: (Page X, Section Y.Z)
- If info incomplete, say: "Not available in document"
- No medical advice, diagnosis, or treatment recommendations

Be specific and comprehensive within the given context."""


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
    # Detect query type for better instructions
    question_lower = question.lower()
    query_type_hint = ""
    
    if any(word in question_lower for word in ['dosage', 'dose', 'how much', 'mg', 'frequency']):
        query_type_hint = "\nFor dosage questions, include: dose amount, frequency, route of administration, and special considerations."
    elif any(word in question_lower for word in ['side effect', 'adverse', 'reaction', 'warning']):
        query_type_hint = "\nFor safety questions, include: type of reaction, frequency if available, and severity indicators."
    elif any(word in question_lower for word in ['contraindication', 'should not', 'avoid', 'cannot']):
        query_type_hint = "\nFor contraindication questions, be clear about absolute vs relative contraindications."
    elif any(word in question_lower for word in ['interaction', 'drug-drug', 'combine', 'together']):
        query_type_hint = "\nFor interaction questions, specify the mechanism and clinical significance."
    
    # Format retrieved chunks with section information
    context_parts = []
    for i, chunk in enumerate(retrieved_chunks, 1):
        page = chunk.get('metadata', {}).get('page', '?')
        section = chunk.get('metadata', {}).get('section', '')
        text = chunk.get('text', '')
        
        # Include section if available
        if section:
            context_parts.append(f"[Page {page}, Section {section}]\n{text}")
        else:
            context_parts.append(f"[Page {page}]\n{text}")
    
    context_text = "\n\n".join(context_parts)
    
    # Format conversation history (last 2 only to save space)
    history_text = ""
    if conversation_history:
        recent_history = conversation_history[-2:]  # Only last 2 exchanges
        history_parts = [f"{msg['role']}: {msg['content']}" for msg in recent_history]
        history_text = "\n".join(history_parts)
    
    # Build complete prompt (more concise)
    history_section = ""
    if history_text:
        history_section = f"Recent conversation:\n{history_text}\n\n"
    
    prompt = f"""Context:
{context_text}

{history_section}Question: {question}
{query_type_hint}

Answer using only the context above. Always cite with page AND section numbers from the context headers."""
    
    return prompt
