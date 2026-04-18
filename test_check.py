from rag_chain import get_rag_chain

def test_verify():
    print("Starting Verification...")
    try:
        chain = get_rag_chain()
        # Simple test query
        question = "What is the video about?"
        print(f"Querying: {question}")
        answer = chain.invoke(question)
        print(f"Answer: {answer}")
        print("Verification Successful!")
    except Exception as e:
        print(f"Verification Failed: {e}")

if __name__ == "__main__":
    test_verify()
