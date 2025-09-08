import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=GEMINI_API_KEY)

def generate_response(query: str, context: str = None) -> str:
    """
    Generate a response using Gemini model based on the user query and optional context.
    
    Args:
        query (str): The user's query
        context (str, optional): Additional context to provide to the model
        
    Returns:
        str: Generated response from Gemini
    """
    try:
        # Initialize the model
        model = genai.GenerativeModel('gemini-pro')
        
        # Prepare the prompt with context if provided
        if context:
            prompt = f"""Context: {context}
            
            Based on the above context, answer the following question:
            Question: {query}
            
            Provide a clear and concise answer:"""
        else:
            prompt = f"Answer the following question concisely:\n{query}"
        
        # Generate response
        response = model.generate_content(prompt)
        
        # Return the generated text
        return response.text
    
    except Exception as e:
        return f"Error generating response: {str(e)}"

# Example usage
if __name__ == "__main__":
    test_query = "What is the capital of France?"
    print(f"Query: {test_query}")
    print(f"Response: {generate_response(test_query)}")
