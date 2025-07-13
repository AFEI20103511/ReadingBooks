#!/usr/bin/env python3
"""
Test script for LLM pipeline debugging
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import settings directly
LLM_BACKEND = "ollama"
LLM_MODEL = "llama2"

from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
import json

def test_llm():
    """Test the LLM pipeline with a simple example"""
    
    # Test text
    test_text = "John Smith and Mary Johnson went to the store. Alice Brown was there too."
    
    print(f"Testing with text: {test_text}")
    print("-" * 50)
    
    # Get LLM
    llm = OllamaLLM(model=LLM_MODEL)
    
    # Create prompt
    entity_prompt = PromptTemplate(
        input_variables=["text"],
        template="""
        Extract all human names (people) from the following text.
        Return ONLY a valid JSON array of objects with name and type fields.
        Do not include any additional text, quotes, or formatting.
        Example: [{{"name": "John Smith", "type": "person"}}, {{"name": "Mary Johnson", "type": "person"}}]
        
        Text: {text}
        
        JSON:
        """
    )
    
    # Get response
    print("Sending request to LLM...")
    response = llm(entity_prompt.format(text=test_text))
    
    print(f"Raw LLM Response:")
    print(response)
    print("-" * 50)
    
    # Try to parse JSON
    try:
        cleaned_response = response.strip()
        print(f"Cleaned response: {cleaned_response}")
        
        # Handle cases where LLM returns quoted JSON string
        if cleaned_response.startswith('"') and cleaned_response.endswith('"'):
            cleaned_response = json.loads(cleaned_response)
        
        # Try to parse as JSON
        if isinstance(cleaned_response, str):
            result = json.loads(cleaned_response)
        else:
            result = cleaned_response
            
        print(f"Parsed result: {result}")
        return result
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        return None

if __name__ == "__main__":
    result = test_llm()
    if result:
        print(f"Success! Found {len(result)} entities")
        for entity in result:
            print(f"  - {entity['name']} ({entity['type']})")
    else:
        print("Failed to parse entities") 