def fixed_size_chunk(text: str, chunk_size=500, overlap=50) -> list[str]:
    """Fixed-size chunking with overlap window."""
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def semantic_chunk(text: str, max_chunk_size=600) -> list[str]:
    """
    Semantic chunking: split on paragraph/sentence boundaries.
    Never break mid-sentence. Respects natural language structure.
    """
    if not text:
        return []
    import re
    # Try to split by paragraphs first, then sentences if too long
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
    
    for p in paragraphs:
        if len(current_chunk) + len(p) <= max_chunk_size:
            current_chunk += ("\n\n" if current_chunk else "") + p
        else:
            if current_chunk:
                chunks.append(current_chunk)
            
            if len(p) > max_chunk_size:
                # split by sentence
                sentences = re.split(r'(?<=[.!?])\s+', p)
                sub_chunk = ""
                for s in sentences:
                    if len(sub_chunk) + len(s) <= max_chunk_size:
                        sub_chunk += (" " if sub_chunk else "") + s
                    else:
                        if sub_chunk:
                            chunks.append(sub_chunk)
                        sub_chunk = s
                if sub_chunk:
                    current_chunk = sub_chunk
            else:
                current_chunk = p
                
    if current_chunk:
        chunks.append(current_chunk)
        
    return chunks
