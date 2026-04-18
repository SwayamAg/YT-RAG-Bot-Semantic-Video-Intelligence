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
        vector_store = get_or_create_vector_store(video_id)
        
        if not vector_store:
            return None
            
        retriever = vector_store.as_retriever(
            search_type=SEARCH_TYPE, 
            search_kwargs={"k": RETRIEVAL_K}
        )
    except Exception as e:
        print(f"[SYSTEM ERROR] Pipeline failed to start: {e}")
        return None
    
    # 2. Prompt Engineering
    template = """
      You are a specialized AI Research Assistant. Your goal is to answer questions 
      based strictly on the provided YouTube video transcript context.

      ### RULES:
      1. Use ONLY the provided context to answer.
      2. If the answer is not in the context, say: "I'm sorry, that information is not available in the transcript."
      3. Be professional, technical, and concise.

      ### CONTEXT:
      {context}
      
      ### USER QUESTION: 
      {question}

      ### FINAL ANSWER:
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
    
    return rag_pipeline

if __name__ == "__main__":
    from config import YOUTUBE_VIDEO_ID
    if get_rag_chain(YOUTUBE_VIDEO_ID):
        print("[OK] RAG Pipeline diagnostic passed.")
