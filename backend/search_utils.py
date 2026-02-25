import os
from typing import List
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

search = DuckDuckGoSearchRun()

def gather_context_from_web(topic: str, objectives: List[str]) -> str:
    """
    Searches the web for context based on topic and objectives.
    """
    query = f" {topic} " + " ".join(objectives)
    results = search.run(query)
    return results

def search_for_simple_explanation(topic: str) -> str:
    """
    Specifically searches for simple explanations and analogies for the Feynman Technique.
    """
    query = f" {topic} analogy simple explanation for students ELI5"
    results = search.run(query)
    return results

def gather_context_from_notes(topic: str) -> str:
    """
    Simulates gathering context from user notes.
    In a real scenario, this would search a database or local files.
    """
    # For now, we return empty to trigger fallback to web search as per requirement
    return ""

def validate_relevance(topic: str, objectives: List[str], context: str) -> tuple[bool, float]:
    """
    Uses an LLM to validate if the gathered context is relevant to the objectives.
    Returns (is_relevant, score).
    """
    llm = ChatGroq(model="llama-3.3-70b-versatile") 
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a context validation expert. Your task is to determine if the provided context is relevant to the learning objectives of a topic."),
        ("user", "Topic: {topic}\nObjectives: {objectives}\n\nGathered Context: {context}\n\nAssess how relevant and sufficient this context is (0-100%). Respond in JSON format: {{\"score\": <score>, \"is_relevant\": <true/false>}}")
    ])
    
    from langchain_core.output_parsers import JsonOutputParser
    parser = JsonOutputParser()
    chain = prompt | llm | parser
    
    result = chain.invoke({"topic": topic, "objectives": ", ".join(objectives), "context": context})
    
    return result.get("is_relevant", False), float(result.get("score", 0.0))
