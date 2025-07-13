# LLM pipeline for entity and relationship extraction
# This module handles the AI processing of extracted PDF text to find people and their relationships
from typing import List, Dict, Optional
import json
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ..config.settings import LLM_BACKEND, LLM_MODEL

def get_llm():
    """
    Get the configured LLM instance based on settings.
    
    Currently supports:
    - Ollama (local LLM runner)
    - TODO: Add support for OpenAI, Gemini, etc.
    
    Returns:
        LLM instance (Ollama, OpenAI, etc.)
        
    Raises:
        ValueError: If the configured LLM backend is not supported
    """
    if LLM_BACKEND == "ollama":
        return OllamaLLM(model=LLM_MODEL)
    else:
        # TODO: Add support for other LLM backends
        raise ValueError(f"Unsupported LLM backend: {LLM_BACKEND}")

def extract_entities(text: str) -> List[Dict[str, str]]:
    """
    Extract human names (entities) from text using LLM.
    
    This function:
    1. Sends the text to an LLM with a specific prompt
    2. Handles text chunking for large documents
    3. Parses the LLM response as JSON
    4. Removes duplicate entities
    
    Args:
        text: Input text to analyze (extracted from PDF)
        
    Returns:
        List of entities with their names and types
        Example: [{"name": "John Smith", "type": "person"}]
    """
    try:
        llm = get_llm()
        
        # Prompt template for entity extraction
        # The LLM is instructed to return only JSON format
        entity_prompt = PromptTemplate(
            input_variables=["text"],
            template="""
            Extract all human names (people) from the following text.
            Return ONLY a valid JSON array of strings with the names.
            Do not include any additional text, quotes, or formatting.
            The response should be a direct JSON array, not wrapped in an object.
            Example: ["John Smith", "Mary Johnson"]
            
            Text: {text}
            
            JSON:
            """
        )
        
        # Handle large texts by splitting into chunks
        # This prevents LLM context limits and improves processing
        if len(text) > 4000:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=200)
            text_chunks = text_splitter.split_text(text)
            all_entities = []
            
            # Process each chunk separately
            for chunk in text_chunks:
                response = llm.invoke(entity_prompt.format(text=chunk))
                try:
                    cleaned_response = response.strip()
                    
                    # Handle cases where LLM returns quoted JSON string
                    if cleaned_response.startswith('"') and cleaned_response.endswith('"'):
                        cleaned_response = json.loads(cleaned_response)
                    
                    # Try to parse as JSON
                    if isinstance(cleaned_response, str):
                        parsed = json.loads(cleaned_response)
                    else:
                        parsed = cleaned_response
                    
                    # Handle different response formats
                    if isinstance(parsed, dict):
                        # If LLM returns {"names": [...]} or {"entities": [...]}
                        if "names" in parsed:
                            names = parsed["names"]
                        elif "entities" in parsed:
                            names = parsed["entities"]
                        else:
                            # Try to find any array in the response
                            names = []
                            for key, value in parsed.items():
                                if isinstance(value, list):
                                    names = value
                                    break
                    elif isinstance(parsed, list):
                        names = parsed
                    else:
                        names = []
                    
                    # Convert to simple array of names if needed
                    if names and isinstance(names[0], dict):
                        # Convert [{"name": "John"}, {"name": "Mary"}] to ["John", "Mary"]
                        entities = [item.get("name", str(item)) for item in names]
                    else:
                        # Already in correct format: ["John", "Mary"]
                        entities = names
                    
                    all_entities.extend(entities)
                except json.JSONDecodeError:
                    # Skip chunks that don't return valid JSON
                    continue
            
            # Remove duplicate names (force string handling)
            seen = set()
            unique_entities = []
            for name in all_entities:
                if isinstance(name, str):
                    if name not in seen:
                        seen.add(name)
                        unique_entities.append(name)
            return unique_entities
        else:
            # For smaller texts, process directly
            response = llm.invoke(entity_prompt.format(text=text))
            try:
                # Clean the response and try to parse JSON
                cleaned_response = response.strip()
                print(f"LLM Response: {cleaned_response}")  # Debug output
                
                # Extract JSON from the response (remove extra text)
                import re
                json_match = re.search(r'\[.*\]', cleaned_response, re.DOTALL)
                if json_match:
                    cleaned_response = json_match.group(0)
                
                # Handle cases where LLM returns quoted JSON string
                if cleaned_response.startswith('"') and cleaned_response.endswith('"'):
                    cleaned_response = json.loads(cleaned_response)
                
                # Try to parse as JSON
                if isinstance(cleaned_response, str):
                    parsed = json.loads(cleaned_response)
                else:
                    parsed = cleaned_response
                
                # Handle different response formats
                if isinstance(parsed, list):
                    # Remove duplicates, preserve order
                    seen = set()
                    unique_entities = []
                    for name in parsed:
                        if isinstance(name, str):
                            if name not in seen:
                                seen.add(name)
                                unique_entities.append(name)
                    return unique_entities
                else:
                    return []
                
                # Convert to simple array of names if needed
                if names and isinstance(names[0], dict):
                    # Convert [{"name": "John"}, {"name": "Mary"}] to ["John", "Mary"]
                    return [item.get("name", str(item)) for item in names]
                else:
                    # Already in correct format: ["John", "Mary"]
                    return names
                    
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                print(f"Raw response: {response}")
                return []
                
    except Exception as e:
        print(f"Error extracting entities: {str(e)}")
        return []

def extract_relationships(text: str, entities: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Extract relationships between entities using LLM.
    
    This function:
    1. Takes the list of entities found in the previous step
    2. Sends text and entity names to LLM for relationship analysis
    3. Handles text chunking for large documents
    4. Parses the LLM response as JSON
    5. Removes duplicate relationships
    
    Args:
        text: Input text to analyze (extracted from PDF)
        entities: List of extracted entities from previous step
        
    Returns:
        List of relationships between entities
        Example: [{"source": "John Smith", "target": "Mary Johnson", "type": "spouse"}]
    """
    try:
        # If no entities found, no relationships possible
        if not entities:
            return []
            
        llm = get_llm()
        
        # Create list of entity names for the prompt
        entity_names = entities  # entities is now already a list of strings
        
        # Prompt template for relationship extraction
        # The LLM is instructed to find relationships between the given people
        relationship_prompt = PromptTemplate(
            input_variables=["text", "entities"],
            template="""
            Find relationships between these people in the text: {entities}
            
            Return ONLY a valid JSON array of objects with "source", "target", and "type" fields.
            Do not include any additional text, quotes, or formatting.
            Example: [{"source": "John Smith", "target": "Mary Johnson", "type": "spouse"}]
            
            Text: {text}
            
            JSON:
            """
        )
        
        # Handle large texts by splitting into chunks
        if len(text) > 4000:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=200)
            text_chunks = text_splitter.split_text(text)
            all_relationships = []
            
            # Process each chunk separately
            for chunk in text_chunks:
                response = llm.invoke(relationship_prompt.format(text=chunk, entities=entity_names))
                try:
                    cleaned_response = response.strip()
                    
                    # Handle cases where LLM returns quoted JSON string
                    if cleaned_response.startswith('"') and cleaned_response.endswith('"'):
                        cleaned_response = json.loads(cleaned_response)
                    
                    # Try to parse as JSON
                    if isinstance(cleaned_response, str):
                        relationships = json.loads(cleaned_response)
                    else:
                        relationships = cleaned_response
                    all_relationships.extend(relationships)
                except json.JSONDecodeError:
                    # Skip chunks that don't return valid JSON
                    continue
            
            # Remove duplicate relationships (same source-target-type combination)
            seen = set()
            unique_relationships = []
            for rel in all_relationships:
                key = f"{rel['source']}-{rel['target']}-{rel['type']}"
                if key not in seen:
                    seen.add(key)
                    unique_relationships.append(rel)
            return unique_relationships
        else:
            # For smaller texts, process directly
            response = llm.invoke(relationship_prompt.format(text=text, entities=entity_names))
            try:
                cleaned_response = response.strip()
                print(f"Relationship LLM Response: {cleaned_response}")  # Debug output
                
                # Handle cases where LLM returns quoted JSON string
                if cleaned_response.startswith('"') and cleaned_response.endswith('"'):
                    cleaned_response = json.loads(cleaned_response)
                
                # Try to parse as JSON
                if isinstance(cleaned_response, str):
                    return json.loads(cleaned_response)
                else:
                    return cleaned_response
            except json.JSONDecodeError as e:
                print(f"Relationship JSON parsing error: {e}")
                print(f"Raw response: {response}")
                return []
                
    except Exception as e:
        print(f"Error extracting relationships: {str(e)}")
        return []

def process_text_with_llm(text: str) -> Dict[str, any]:
    """
    Main function to process text and extract entities and relationships.
    
    This is the primary entry point for LLM processing:
    1. Extracts all human names (entities) from the text
    2. Finds relationships between those entities
    3. Returns structured data for frontend visualization
    
    Args:
        text: Input text from PDF (extracted by pdf_parser module)
        
    Returns:
        Dictionary containing:
        - entities: List of people found in the text
        - relationships: List of relationships between people
        - text_length: Length of processed text
    """
    # Step 1: Extract all human names from the text
    entities = extract_entities(text)
    
    # Step 2: Find relationships between the discovered entities
    relationships = extract_relationships(text, entities)
    
    # Step 3: Return structured results for frontend
    return {
        "entities": entities,
        "relationships": relationships,
        "text_length": len(text)
    } 