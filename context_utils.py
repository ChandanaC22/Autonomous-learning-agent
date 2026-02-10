import os
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from pydantic import BaseModel, Field
from models import MCQ

# Local embedding model
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def chunk_text(text: str) -> List[str]:
    """Splits text into chunks for vectorization."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
    )
    return text_splitter.split_text(text)

def setup_vector_store(chunks: List[str]):
    """Creates a temporary in-memory vector store."""
    return Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        collection_name="temp_context"
    )

def generate_summary(context: str, topic: str) -> str:
    """Generates a concise summary/study material from the context."""
    llm = ChatGroq(model="llama-3.3-70b-versatile")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an educator. Create a concise, structured, and engaging study summary for the given topic based strictly on the provided context. Use bullet points and bold text for key terms."),
        ("user", "Topic: {topic}\nContext: {context}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"topic": topic, "context": context})

class MCQList(BaseModel):
    mcqs: List[MCQ] = Field(description="A list of 3-5 Multiple Choice Questions.")

def generate_mcqs(context: str, topic: str, seen_questions: List[str] = []) -> List[MCQ]:
    """Generates 3-5 MCQs based on the provided context, avoiding duplicates."""
    llm = ChatGroq(model="llama-3.3-70b-versatile")
    
    parser = JsonOutputParser(pydantic_object=MCQList)
    
    avoid_block = ""
    if seen_questions:
        avoid_block = f"\nCRITICAL: DO NOT use any of these questions as they have already been used: {seen_questions}. Please focus on different nuances or aspects of the topic."

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an educator. Generate 3-5 Multiple Choice Questions (MCQs) based strictly on the provided context. Each question must have exactly 4 options and one clearly correct index. Return as JSON."),
        ("user", "Topic: {topic}\nContext: {context}{avoid_block}\n\n{format_instructions}")
    ]).partial(format_instructions=parser.get_format_instructions())
    
    chain = prompt | llm | parser
    result = chain.invoke({"topic": topic, "context": context, "avoid_block": avoid_block})
    # Convert dicts to MCQ objects if necessary, though JsonOutputParser with pydantic_object helps
    return [MCQ(**m) if isinstance(m, dict) else m for m in result["mcqs"]]

class EvaluationScore(BaseModel):
    score: float = Field(description="A score from 0 to 100.")
    feedback: str = Field(description="Brief feedback on the answer.")

def evaluate_answer(question: str, context: str, answer: str) -> float:
    """Evaluates a single answer against the context and returns a score."""
    llm = ChatGroq(model="llama-3.3-70b-versatile")
    
    parser = JsonOutputParser(pydantic_object=EvaluationScore)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an examiner. Evaluate the learner's answer based on the provided context. Give a score from 0 to 100 based on accuracy and completeness."),
        ("user", "Question: {question}\nContext: {context}\nLearner's Answer: {answer}\n\n{format_instructions}")
    ]).partial(format_instructions=parser.get_format_instructions())
    
    chain = prompt | llm | parser
    result = chain.invoke({"question": question, "context": context, "answer": answer})
    return result["score"]

def generate_feynman_explanation(topic: str, context: str, simple_context: str) -> str:
    """Generates a simple, jargon-free explanation using the Feynman Technique (for a 10-year-old)."""
    llm = ChatGroq(model="llama-3.3-70b-versatile")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a master educator using the Feynman Technique. 
        Your goal is to transform complex information into something a 10-year-old can explain to their friends.
        
        Use the 'Primary Context' and 'Simplified Web Context' to create a structured explanation.
        
        STRUCTURE YOUR RESPONSE AS FOLLOWS:
        1. **The Core Idea**: A 1-sentence summary that avoids any technical terms.
        2. **The Everyday Analogy**: Compare the concept to something very common (like a kitchen, a playground, or a backpack). Use vivid imagery.
        3. **How it Works**: Explain the 'why' using the analogy.
        4. **Quick Recap**: A simple takeaway.
        
        RULES:
        - Strictly NO jargon. If you must use a term, explain it with a toy analogy.
        - Tone: Encouraging, clear, and vivid.
        - Length: Concise but impactful (max 250 words)."""),
        ("user", "Topic: {topic}\nPrimary Context: {context}\nSimplified Web Context: {simple_context}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"topic": topic, "context": context, "simple_context": simple_context})
