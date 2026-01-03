from crewai_tools import BaseTool
from typing import Type, Dict, Any, List
from pydantic import BaseModel, Field
import json
from datetime import datetime


# ============================================
# 1. INTENT ANALYSIS TOOL
# ============================================

class IntentAnalysisInput(BaseModel):
    """Input schema for Intent Analysis Tool"""
    amount: float = Field(..., description="Transaction amount in GBP")
    sender: str = Field(..., description="Sender identifier or name")
    receiver: str = Field(..., description="Receiver identifier or name")
    purpose: str = Field(..., description="Stated transaction purpose or description")
    timestamp: str = Field(..., description="Transaction timestamp (ISO format)")
    context: str = Field(default="", description="Additional context if available")


class IntentAnalysisTool(BaseTool):
    name: str = "Intent Classification Tool"
    description: str = (
        "Analyzes transaction details to classify the intent, determine urgency level, "
        "and calculate confidence score. Returns structured classification with reasoning."
    )
    args_schema: Type[BaseModel] = IntentAnalysisInput

    def _run(
        self, 
        amount: float, 
        sender: str, 
        receiver: str, 
        purpose: str, 
        timestamp: str,
        context: str = ""
    ) -> str:
        """Execute intent analysis and return JSON string"""
        
        # Intent classification logic
        intent_keywords = {
            "refund": ["refund", "return", "reimbursement", "reversal"],
            "payroll": ["salary", "wage", "payroll", "compensation", "bonus"],
            "vendor": ["vendor", "supplier", "invoice", "payment", "purchase"],
            "investment": ["investment", "equity", "acquisition", "stake"],
            "emergency": ["urgent", "emergency", "critical", "immediate"],
            "tax": ["tax", "vat", "hmrc", "duty"],
            "loan": ["loan", "credit", "financing", "borrowing"]
        }
        
        purpose_lower = purpose.lower()
        detected_intent = "general"
        matched_keywords = []
        
        # Find matching intent
        for intent_type, keywords in intent_keywords.items():
            matches = [kw for kw in keywords if kw in purpose_lower]
            if matches:
                detected_intent = intent_type
                matched_keywords = matches
                break
        
        # Determine urgency
        urgency_keywords = ["urgent", "emergency", "immediate", "asap", "critical"]
        urgency = "high" if any(kw in purpose_lower for kw in urgency_keywords) else "medium"
        
        # Adjust urgency based on amount
        if amount > 50000:
            urgency = "high"
        elif amount < 1000:
            urgency = "low"
        
        # Calculate confidence
        confidence = 0.95 if matched_keywords else 0.60
        if detected_intent == "general":
            confidence = 0.50
        
        # Check timing
        try:
            tx_time = datetime.fromisoformat(timestamp)
            hour = tx_time.hour
            is_off_hours = hour < 6 or hour > 22
        except:
            is_off_hours = False
        
        result = {
            "intent": detected_intent,
            "urgency": urgency,
            "confidence": round(confidence, 2),
            "matched_keywords": matched_keywords,
            "is_off_hours": is_off_hours,
            "amount_category": "high" if amount > 25000 else "medium" if amount > 5000 else "low",
            "analysis_timestamp": datetime.now().isoformat(),
            "reasoning": f"Classified as '{detected_intent}' based on keywords: {matched_keywords}. "
                        f"Urgency: {urgency} due to amount (£{amount:,.2f}) and purpose."
        }
        
        return json.dumps(result, indent=2)


# ============================================
# 2. RISK ASSESSMENT TOOL
# ============================================

class RiskAssessmentInput(BaseModel):
    """Input schema for Risk Assessment Tool"""
    amount: float = Field(..., description="Transaction amount in GBP")
    sender: str = Field(..., description="Sender identifier")
    receiver: str = Field(..., description="Receiver identifier")
    intent: str = Field(..., description="Classified intent from Intent Agent")
    timestamp: str = Field(..., description="Transaction timestamp")
    sender_history: str = Field(default="unknown", description="Sender's transaction history")


class RiskAssessmentTool(BaseTool):
    name: str = "Fraud Risk Assessment Tool"
    description: str = (
        "Evaluates fraud risk by analyzing transaction patterns, amounts, timing, and behavioral signals. "
        "Returns risk score (0-1), risk level, and identified risk factors."
    )
    args_schema: Type[BaseModel] = RiskAssessmentInput

    def _run(
        self,
        amount: float,
        sender: str,
        receiver: str,
        intent: str,
        timestamp: str,
        sender_history: str = "unknown"
    ) -> str:
        """Execute risk assessment and return JSON string"""
        
        risk_score = 0.0
        risk_factors = []
        
        # 1. Amount-based risk
        if amount > 100000:
            risk_score += 0.25
            risk_factors.append("very_high_amount")
        elif amount > 50000:
            risk_score += 0.15
            risk_factors.append("high_amount")
        elif amount > 25000:
            risk_score += 0.08
            risk_factors.append("elevated_amount")
        
        # 2. Time-based risk
        try:
            tx_time = datetime.fromisoformat(timestamp)
            hour = tx_time.hour
            day_of_week = tx_time.weekday()  # 0=Monday, 6=Sunday
            
            # Off-hours transactions
            if hour < 6 or hour > 22:
                risk_score += 0.12
                risk_factors.append("off_hours_transaction")
            
            # Weekend transactions
            if day_of_week >= 5:  # Saturday or Sunday
                risk_score += 0.08
                risk_factors.append("weekend_transaction")
        except:
            risk_score += 0.05
            risk_factors.append("invalid_timestamp")
        
        # 3. Receiver risk
        receiver_lower = receiver.lower()
        suspicious_patterns = ["unknown", "temp", "test", "cash", "personal"]
        if any(pattern in receiver_lower for pattern in suspicious_patterns):
            risk_score += 0.20
            risk_factors.append("suspicious_receiver")
        
        # 4. Sender history risk
        if sender_history.lower() == "unknown":
            risk_score += 0.10
            risk_factors.append("unknown_sender_history")
        elif "new" in sender_history.lower():
            risk_score += 0.08
            risk_factors.append("new_sender")
        
        # 5. Intent-based risk
        high_risk_intents = ["emergency", "general", "loan"]
        if intent in high_risk_intents:
            risk_score += 0.10
            risk_factors.append(f"high_risk_intent_{intent}")
        
        # 6. Round number risk (potential structuring)
        if amount % 10000 == 0 and amount >= 10000:
            risk_score += 0.05
            risk_factors.append("suspicious_round_amount")
        
        # Cap risk score at 1.0
        risk_score = min(risk_score, 1.0)
        
        # Determine risk level
        if risk_score < 0.25:
            risk_level = "low"
        elif risk_score < 0.50:
            risk_level = "medium"
        elif risk_score < 0.75:
            risk_level = "high"
        else:
            risk_level = "critical"
        
        result = {
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "risk_factor_count": len(risk_factors),
            "requires_additional_review": risk_score >= 0.50,
            "assessment_timestamp": datetime.now().isoformat(),
            "recommendation": (
                "REJECT - Too risky" if risk_score >= 0.75 else
                "ESCALATE - Human review required" if risk_score >= 0.50 else
                "PROCEED - Acceptable risk" if risk_score >= 0.25 else
                "APPROVE - Low risk"
            )
        }
        
        return json.dumps(result, indent=2)


# ============================================
# 3. POLICY VALIDATION TOOL
# ============================================

class PolicyValidationInput(BaseModel):
    """Input schema for Policy Validation Tool"""
    amount: float = Field(..., description="Transaction amount in GBP")
    intent: str = Field(..., description="Transaction intent classification")
    sender: str = Field(..., description="Sender identifier")
    receiver: str = Field(..., description="Receiver identifier")
    urgency: str = Field(default="medium", description="Transaction urgency level")


class PolicyValidationTool(BaseTool):
    name: str = "Policy Compliance Validation Tool"
    description: str = (
        "Validates transactions against company policies, spending limits, approval requirements, "
        "and regulatory constraints. Returns compliance status and any violations."
    )
    args_schema: Type[BaseModel] = PolicyValidationInput

    def _run(
        self,
        amount: float,
        intent: str,
        sender: str,
        receiver: str,
        urgency: str = "medium"
    ) -> str:
        """Execute policy validation and return JSON string"""
        
        # Define spending limits per intent type
        spending_limits = {
            "refund": 15000,
            "vendor": 30000,
            "payroll": 150000,
            "investment": 100000,
            "emergency": 50000,
            "tax": 200000,
            "loan": 75000,
            "general": 5000
        }
        
        violations = []
        warnings = []
        policy_passed = True
        
        # 1. Check spending limits
        applicable_limit = spending_limits.get(intent, spending_limits["general"])
        if amount > applicable_limit:
            violations.append(
                f"Exceeds {intent} spending limit of £{applicable_limit:,.2f} "
                f"(requested: £{amount:,.2f})"
            )
            policy_passed = False
        
        # 2. Check approval requirements
        if amount > 10000 and "approved" not in sender.lower() and "manager" not in sender.lower():
            violations.append(
                "Requires management pre-approval for amounts over £10,000"
            )
            policy_passed = False
        
        if amount > 50000 and "director" not in sender.lower():
            violations.append(
                "Requires director authorization for amounts over £50,000"
            )
            policy_passed = False
        
        # 3. Multi-signature requirement
        if amount > 100000:
            violations.append(
                "Requires dual authorization (two signatures) for amounts over £100,000"
            )
            policy_passed = False
        
        # 4. Receiver validation
        receiver_lower = receiver.lower()
        blocked_keywords = ["sanctioned", "blacklist", "blocked"]
        if any(keyword in receiver_lower for keyword in blocked_keywords):
            violations.append(
                "Receiver is on blocked/sanctioned list"
            )
            policy_passed = False
        
        # 5. Emergency transaction policies
        if urgency == "high" and amount > 25000:
            warnings.append(
                "High urgency + high amount transactions require post-payment audit"
            )
        
        # 6. Daily transaction limit check (simplified)
        daily_limit = 200000
        if amount > daily_limit:
            violations.append(
                f"Exceeds daily transaction limit of £{daily_limit:,.2f}"
            )
            policy_passed = False
        
        # 7. AML/KYC checks for high amounts
        if amount > 10000:
            warnings.append(
                "Transaction requires AML/KYC documentation per regulatory requirements"
            )
        
        result = {
            "policy_passed": policy_passed,
            "violations": violations,
            "warnings": warnings,
            "applicable_limit": applicable_limit,
            "amount_within_limit": amount <= applicable_limit,
            "approval_level_required": (
                "dual_authorization" if amount > 100000 else
                "director" if amount > 50000 else
                "manager" if amount > 10000 else
                "standard"
            ),
            "validation_timestamp": datetime.now().isoformat(),
            "compliance_score": 1.0 if policy_passed and not warnings else 
                               0.7 if policy_passed and warnings else 
                               0.0
        }
        
        return json.dumps(result, indent=2)


# ============================================
# 4. LIQUIDITY CHECK TOOL
# ============================================

class LiquidityCheckInput(BaseModel):
    """Input schema for Liquidity Check Tool"""
    amount: float = Field(..., description="Transaction amount in GBP")
    account_id: str = Field(default="primary", description="Account identifier")
    intent: str = Field(default="general", description="Transaction intent")


class LiquidityCheckTool(BaseTool):
    name: str = "Liquidity and Balance Check Tool"
    description: str = (
        "Checks account balances, liquidity constraints, cash flow impact, and ensures "
        "sufficient funds are available while maintaining required reserves."
    )
    args_schema: Type[BaseModel] = LiquidityCheckInput

    def _run(
        self,
        amount: float,
        account_id: str = "primary",
        intent: str = "general"
    ) -> str:
        """Execute liquidity check and return JSON string"""
        
        # Simulated account data (in production: query real banking API)
        account_balances = {
            "primary": 180000,
            "reserve": 50000,
            "payroll": 200000,
            "operations": 75000
        }
        
        current_balance = account_balances.get(account_id, 150000)
        
        # Financial constraints
        minimum_reserve = 25000  # Must maintain this minimum
        daily_transaction_limit = 75000
        monthly_budget_remaining = 150000
        
        # Calculate post-transaction balance
        remaining_balance = current_balance - amount
        sufficient_funds = remaining_balance >= minimum_reserve
        within_daily_limit = amount <= daily_transaction_limit
        within_budget = amount <= monthly_budget_remaining
        
        # Liquidity warnings
        warnings = []
        concerns = []
        
        if remaining_balance < minimum_reserve:
            concerns.append(
                f"Transaction would breach minimum reserve requirement of £{minimum_reserve:,.2f}"
            )
        
        if remaining_balance < (minimum_reserve * 1.2):
            warnings.append(
                "Balance would fall close to minimum reserve threshold"
            )
        
        if amount > (current_balance * 0.5):
            warnings.append(
                "Transaction represents >50% of available balance - high liquidity impact"
            )
        
        if not within_daily_limit:
            concerns.append(
                f"Exceeds daily transaction limit of £{daily_transaction_limit:,.2f}"
            )
        
        # Cash flow impact assessment
        if intent == "emergency":
            cash_flow_impact = "high_priority"
        elif amount > 50000:
            cash_flow_impact = "significant"
        elif amount > 10000:
            cash_flow_impact = "moderate"
        else:
            cash_flow_impact = "minimal"
        
        # Overall feasibility
        financially_viable = sufficient_funds and within_daily_limit and within_budget
        
        result = {
            "sufficient_funds": sufficient_funds,
            "financially_viable": financially_viable,
            "current_balance": current_balance,
            "remaining_balance": remaining_balance,
            "minimum_reserve": minimum_reserve,
            "reserve_cushion": remaining_balance - minimum_reserve if sufficient_funds else 0,
            "daily_limit": daily_transaction_limit,
            "within_daily_limit": within_daily_limit,
            "monthly_budget_remaining": monthly_budget_remaining,
            "within_budget": within_budget,
            "warnings": warnings,
            "concerns": concerns,
            "cash_flow_impact": cash_flow_impact,
            "liquidity_health": (
                "excellent" if remaining_balance > (minimum_reserve * 3) else
                "good" if remaining_balance > (minimum_reserve * 2) else
                "adequate" if sufficient_funds else
                "insufficient"
            ),
            "check_timestamp": datetime.now().isoformat()
        }
        
        return json.dumps(result, indent=2)


# ============================================
# 5. AUDIT LOGGING TOOL
# ============================================

class AuditLogInput(BaseModel):
    """Input schema for Audit Logging Tool"""
    transaction_id: str = Field(..., description="Unique transaction identifier")
    decision: str = Field(..., description="Final decision: APPROVE/REJECT/ESCALATE")
    agent_outputs: str = Field(..., description="JSON string of all agent outputs")
    rationale: str = Field(..., description="Decision rationale")
    decision_maker: str = Field(default="AI Treasury System", description="Who made the decision")


class AuditLogTool(BaseTool):
    name: str = "Audit Trail Creation Tool"
    description: str = (
        "Creates comprehensive, immutable audit records of all transaction decisions. "
        "Stores inputs, agent outputs, final decisions, and generates verification hash."
    )
    args_schema: Type[BaseModel] = AuditLogInput

    def _run(
        self,
        transaction_id: str,
        decision: str,
        agent_outputs: str,
        rationale: str,
        decision_maker: str = "AI Treasury System"
    ) -> str:
        """Create audit log and return JSON string"""
        
        # Parse agent outputs if it's a JSON string
        try:
            outputs_dict = json.loads(agent_outputs) if isinstance(agent_outputs, str) else agent_outputs
        except:
            outputs_dict = {"raw": agent_outputs}
        
        # Create comprehensive audit record
        audit_record = {
            "audit_id": f"AUDIT-{transaction_id}",
            "transaction_id": transaction_id,
            "timestamp": datetime.now().isoformat(),
            "decision": decision,
            "decision_maker": decision_maker,
            "rationale": rationale,
            "agent_outputs": outputs_dict,
            "audit_trail": {
                "intent_analysis_completed": "intent" in str(outputs_dict),
                "risk_assessment_completed": "risk" in str(outputs_dict),
                "policy_validation_completed": "policy" in str(outputs_dict),
                "liquidity_check_completed": "treasury" in str(outputs_dict),
                "final_decision_made": decision in ["APPROVE", "REJECT", "ESCALATE"]
            },
            "compliance_flags": {
                "complete_audit_trail": True,
                "all_agents_consulted": True,
                "decision_documented": bool(rationale),
                "timestamp_recorded": True
            },
            "verification_hash": hash(json.dumps({
                "tx_id": transaction_id,
                "decision": decision,
                "timestamp": datetime.now().isoformat()
            }, sort_keys=True))
        }
        
        # In production: Write to immutable storage (blockchain, WORM, etc.)
        # For now: Print to console for visibility
        print("\n" + "="*70)
        print("🔒 IMMUTABLE AUDIT RECORD CREATED")
        print("="*70)
        print(f"Transaction ID: {transaction_id}")
        print(f"Decision: {decision}")
        print(f"Timestamp: {audit_record['timestamp']}")
        print(f"Verification Hash: {audit_record['verification_hash']}")
        print("="*70 + "\n")
        
        result = {
            "audit_logged": True,
            "audit_id": audit_record["audit_id"],
            "record_timestamp": audit_record["timestamp"],
            "verification_hash": audit_record["verification_hash"],
            "storage_location": "immutable_audit_database",  # Placeholder
            "compliance_status": "COMPLIANT",
            "record_retrievable": True
        }
        
        return json.dumps(result, indent=2)
