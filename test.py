from crewai import Agent, Task, Crew, Process
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

def process_transaction(transaction_data):
    print("\n🤖 AI Treasury System Starting...")
    
    llm = ChatGroq(
        temperature=0.7,
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.3-70b-versatile"
    )
    
    intent_agent = Agent(
        role="Intent Analyst",
        goal="Analyze transaction",
        backstory="Transaction expert",
        verbose=True,
        llm=llm
    )
    
    risk_agent = Agent(
        role="Risk Officer",
        goal="Assess risk",
        backstory="Risk expert",
        verbose=True,
        llm=llm
    )
    
    decision_agent = Agent(
        role="CFO",
        goal="Final decision",
        backstory="Decision maker",
        verbose=True,
        llm=llm
    )
    
    intent_task = Task(
        description=f"Analyze: {transaction_data}",
        expected_output="Intent analysis",
        agent=intent_agent
    )
    
    risk_task = Task(
        description=f"Risk check: {transaction_data}",
        expected_output="Risk score",
        agent=risk_agent
    )
    
    decision_task = Task(
        description="APPROVE or DENY decision",
        expected_output="Final decision",
        agent=decision_agent
    )
    
    crew = Crew(
        agents=[intent_agent, risk_agent, decision_agent],
        tasks=[intent_task, risk_task, decision_task],
        verbose=True,
        process=Process.sequential
    )
    
    return crew.kickoff()

if __name__ == "__main__":
    transaction = {
        "amount": 7500.00,
        "receiver": "Acme Supplies",
        "purpose": "Monthly payment",
        "balance": 125000.00,
    }
    
    print("="*60)
    print("AI TREASURY SYSTEM")
    print("="*60)
    
    result = process_transaction(transaction)
    
    print("\n"+"="*60)
    print("RESULT:", result)
    print("="*60)
