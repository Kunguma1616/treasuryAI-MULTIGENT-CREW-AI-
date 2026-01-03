from crewai import Crew, Process
from datetime import datetime
import json
from typing import Dict, Any

# Import all agents
from agent import (
    intent_agent,
    risk_agent,
    policy_agent,
    treasury_agent,
    decision_agent,
    audit_agent
)

# Import all tools
from tool import (
    IntentAnalysisTool,
    RiskAssessmentTool,
    PolicyValidationTool,
    LiquidityCheckTool,
    AuditLogTool
)

# Import task creators
from task import (
    create_intent_task,
    create_risk_task,
    create_policy_task,
    create_treasury_task,
    create_decision_task,
    create_audit_task
)

class AITreasurySystem:
    """
    Autonomous AI Treasury System
    
    Governs monetary actions using specialized AI agents for:
    - Intent understanding
    - Risk assessment
    - Policy validation
    - Liquidity checking
    - Final decision making
    - Audit logging
    """
    
    def __init__(self):
        # Initialize all tools
        self.intent_tool = IntentAnalysisTool()
        self.risk_tool = RiskAssessmentTool()
        self.policy_tool = PolicyValidationTool()
        self.liquidity_tool = LiquidityCheckTool()
        self.audit_tool = AuditLogTool()
        
        print("✓ AI Treasury System Initialized")
        print("✓ All agents and tools loaded")
        print("="*60)
    
    def process_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a monetary transaction through the AI agent pipeline
        
        Args:
            transaction_data: Dictionary containing transaction details
            
        Returns:
            Final decision and complete audit trail
        """
        print(f"\n{'='*60}")
        print(f"PROCESSING TRANSACTION: {transaction_data.get('transaction_id', 'TXN-001')}")
        print(f"{'='*60}\n")
        
        # Add timestamp if not present
        if 'timestamp' not in transaction_data:
            transaction_data['timestamp'] = datetime.now().isoformat()
        
        # Stage 1: Intent Analysis
        print("\n[1/6] Intent Analysis...")
        intent_task = create_intent_task(
            intent_agent, 
            [self.intent_tool], 
            transaction_data
        )
        
        intent_crew = Crew(
            agents=[intent_agent],
            tasks=[intent_task],
            process=Process.sequential,
            verbose=True
        )
        intent_result = intent_crew.kickoff()
        print(f"✓ Intent Analysis Complete: {intent_result}")
        
        # Stage 2: Risk Assessment
        print("\n[2/6] Risk Assessment...")
        risk_task = create_risk_task(
            risk_agent,
            [self.risk_tool],
            transaction_data,
            str(intent_result)
        )
        
        risk_crew = Crew(
            agents=[risk_agent],
            tasks=[risk_task],
            process=Process.sequential,
            verbose=True
        )
        risk_result = risk_crew.kickoff()
        print(f"✓ Risk Assessment Complete: {risk_result}")
        
        # Stage 3: Policy Validation
        print("\n[3/6] Policy Validation...")
        policy_task = create_policy_task(
            policy_agent,
            [self.policy_tool],
            transaction_data,
            str(intent_result)
        )
        
        policy_crew = Crew(
            agents=[policy_agent],
            tasks=[policy_task],
            process=Process.sequential,
            verbose=True
        )
        policy_result = policy_crew.kickoff()
        print(f"✓ Policy Validation Complete: {policy_result}")
        
        # Stage 4: Liquidity Check
        print("\n[4/6] Liquidity Check...")
        treasury_task = create_treasury_task(
            treasury_agent,
            [self.liquidity_tool],
            transaction_data
        )
        
        treasury_crew = Crew(
            agents=[treasury_agent],
            tasks=[treasury_task],
            process=Process.sequential,
            verbose=True
        )
        treasury_result = treasury_crew.kickoff()
        print(f"✓ Liquidity Check Complete: {treasury_result}")
        
        # Stage 5: Final Decision
        print("\n[5/6] Making Final Decision...")
        all_results = [intent_result, risk_result, policy_result, treasury_result]
        decision_task = create_decision_task(
            decision_agent,
            transaction_data,
            all_results
        )
        
        decision_crew = Crew(
            agents=[decision_agent],
            tasks=[decision_task],
            process=Process.sequential,
            verbose=True
        )
        final_decision = decision_crew.kickoff()
        print(f"✓ Final Decision Made: {final_decision}")
        
        # Stage 6: Audit Logging
        print("\n[6/6] Creating Audit Record...")
        all_outputs = {
            "intent": str(intent_result),
            "risk": str(risk_result),
            "policy": str(policy_result),
            "treasury": str(treasury_result),
            "decision": str(final_decision)
        }
        
        audit_task = create_audit_task(
            audit_agent,
            [self.audit_tool],
            transaction_data,
            all_outputs,
            str(final_decision)
        )
        
        audit_crew = Crew(
            agents=[audit_agent],
            tasks=[audit_task],
            process=Process.sequential,
            verbose=True
        )
        audit_result = audit_crew.kickoff()
        print(f"✓ Audit Record Created: {audit_result}")
        
        # Compile final output
        final_output = {
            "transaction_id": transaction_data.get('transaction_id', 'TXN-001'),
            "timestamp": datetime.now().isoformat(),
            "input": transaction_data,
            "agent_outputs": all_outputs,
            "final_decision": str(final_decision),
            "audit_reference": str(audit_result)
        }
        
        print(f"\n{'='*60}")
        print("TRANSACTION PROCESSING COMPLETE")
        print(f"{'='*60}\n")
        
        return final_output


def main():
    """
    Main execution function - demonstrates the AI Treasury System
    """
    print("\n" + "="*60)
    print("AUTONOMOUS AI TREASURY SYSTEM")
    print("="*60 + "\n")
    
    # Initialize the system
    treasury_system = AITreasurySystem()
    
    # Example Transaction 1: Vendor payment at midnight
    transaction_1 = {
        "transaction_id": "TXN-20260103-001",
        "amount": 7500,
        "sender": "Company Operations",
        "receiver": "Acme Supplies Ltd",
        "purpose": "Vendor payment for Q1 supplies invoice #4521",
        "timestamp": "2026-01-03T00:30:00",
        "account_id": "primary"
    }
    
    print("\n" + "🔍 EXAMPLE 1: Midnight Vendor Payment")
    result_1 = treasury_system.process_transaction(transaction_1)
    
    print("\n\n" + "="*60)
    print("FINAL OUTPUT:")
    print("="*60)
    print(json.dumps(result_1, indent=2))
    
    # Example Transaction 2: High-value refund
    print("\n\n" + "="*60)
    print("="*60 + "\n")
    
    transaction_2 = {
        "transaction_id": "TXN-20260103-002",
        "amount": 45000,
        "sender": "Customer Service",
        "receiver": "Premium Client Corp",
        "purpose": "Urgent refund for cancelled enterprise contract",
        "timestamp": "2026-01-03T14:15:00",
        "account_id": "primary"
    }
    
    print("\n" + "🔍 EXAMPLE 2: High-Value Refund")
    result_2 = treasury_system.process_transaction(transaction_2)
    
    print("\n\n" + "="*60)
    print("FINAL OUTPUT:")
    print("="*60)
    print(json.dumps(result_2, indent=2))
    
    print("\n\n" + "="*60)
    print("ALL TRANSACTIONS PROCESSED")
    print("System demonstrated: Intent → Risk → Policy → Liquidity → Decision → Audit")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
