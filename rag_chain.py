from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from config import get_llm, RETRIEVAL_K, SEARCH_TYPE
from ingestion import get_or_create_vector_store

def format_docs(docs):
    """Joins multiple documents into a single string context."""
    return "\n\n".join(doc.page_content for doc in docs)

def get_rag_chain(video_id: str):
    """Constructs the RAG pipeline for a specific video_id."""
    
    # 1. Pipeline Initialization
    try:
        llm = get_llm()
        vector_store, is_fallback = get_or_create_vector_store(video_id)
        
        if not vector_store:
            return None, False
            
        retriever = vector_store.as_retriever(
            search_type=SEARCH_TYPE, 
            search_kwargs={"k": RETRIEVAL_K}
        )
    except Exception as e:
        print(f"[SYSTEM ERROR] Pipeline failed to start: {e}")
        return None, False
    
    # 2. Prompt Engineering
    template = """
      You are a Senior Technical Analyst and Research Assistant. Your goal is to provide 
      high-fidelity, structured summaries and answers based on the provided YouTube transcript.

      ### INSTRUCTIONS:
      1. Use ONLY the provided context. Do not use outside knowledge.
      2. CLEAN FORMATTING: Do NOT use Markdown symbols like #, *, or **.
      3. HEADERS: Use ALL CAPS for section headers (e.g., OVERVIEW, CORE WORKFLOW).
      4. LISTS: Use simple dashes (-) for bullet points.
      5. STRUCTURE: Organize your response into these sections:
         OVERVIEW: A brief summary.
         CORE WORKFLOW / KEY CONCEPTS: Breakdown of processes.
         TECHNICAL HIGHLIGHTS: Specific tools or methods.
         INSIGHTS / TAKEAWAYS: The key value.
         TIMESTAMPS: List specific [MM:SS] markers.
      6. If the answer is not in the context, state that clearly.

      ### CONTEXT:
      {context}
      
      ### USER QUESTION: 
      {question}

      ### STRUCTURED RESPONSE (PLAIN TEXT ONLY):
    """
    prompt = PromptTemplate(
        template=template,
        input_variables=['context', 'question']
    )
    
    # 3. Chain Assembly
    rag_pipeline = (
        RunnableParallel({
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough()
        })
        | prompt 
        | llm 
        | StrOutputParser()
    )
    
    return rag_pipeline, is_fallback

if __name__ == "__main__":
    from config import YOUTUBE_VIDEO_ID
    if get_rag_chain(YOUTUBE_VIDEO_ID):
        print("[OK] RAG Pipeline diagnostic passed.")
