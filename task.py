from crewai import Task
from agents import (
    intent_agent,
    risk_agent,
    policy_agent,
    treasury_agent,
    decision_agent,
    audit_agent
)

# ============================================================================
# TASK 1: INTENT ANALYSIS
# ============================================================================
intent_analysis_task = Task(
    description=(
        "Analyze the incoming monetary transaction request and classify its intent.\n\n"
        "You will receive:\n"
        "- Transaction amount: {amount}\n"
        "- Sender: {sender}\n"
        "- Receiver: {receiver}\n"
        "- Stated purpose: {purpose}\n"
        "- Timestamp: {timestamp}\n"
        "- Historical context: {history}\n\n"
        "Your job is to:\n"
        "1. Determine the TRUE intent behind this transaction (refund, payroll, vendor payment, "
        "investment, emergency, transfer, or suspicious)\n"
        "2. Assess the urgency level (low/medium/high/critical)\n"
        "3. Provide a confidence score (0.0 to 1.0)\n"
        "4. Flag any red flags or inconsistencies between stated purpose and actual intent\n"
        "5. Consider transaction patterns and historical behavior\n\n"
        "Be thorough but concise. Your classification will determine how other agents evaluate this transaction."
    ),
    expected_output=(
        "A structured JSON response containing:\n"
        "{\n"
        '  "intent": "vendor_payment" | "refund" | "payroll" | "investment" | "transfer" | "emergency" | "suspicious",\n'
        '  "urgency": "low" | "medium" | "high" | "critical",\n'
        '  "confidence": 0.0 to 1.0,\n'
        '  "reasoning": "Brief explanation of why this intent was assigned",\n'
        '  "red_flags": ["list of any concerns or inconsistencies"],\n'
        '  "historical_pattern": "normal" | "unusual" | "first_time"\n'
        "}"
    ),
    agent=intent_agent,
)

# ============================================================================
# TASK 2: RISK ASSESSMENT
# ============================================================================
risk_assessment_task = Task(
    description=(
        "Evaluate the fraud risk and anomaly likelihood of this transaction.\n\n"
        "You will receive:\n"
        "- Transaction details: {amount}, {sender}, {receiver}\n"
        "- Intent classification from previous analysis: {intent_output}\n"
        "- Time of transaction: {timestamp}\n"
        "- Sender/receiver profiles and history\n\n"
        "Your job is to:\n"
        "1. Calculate a risk score (0.0 = safe, 1.0 = maximum risk)\n"
        "2. Classify risk level (low/medium/high/critical)\n"
        "3. Identify specific risk factors (timing anomalies, amount outliers, suspicious patterns)\n"
        "4. Check for known fraud indicators (blacklisted accounts, velocity checks, geographic mismatches)\n"
        "5. Provide mitigation recommendations if risk is elevated\n\n"
        "Consider:\n"
        "- Is the amount unusual for this sender/receiver pair?\n"
        "- Is the timing suspicious (late night, weekend, holiday)?\n"
        "- Are there behavioral anomalies?\n"
        "- Does this match known fraud patterns?\n\n"
        "Balance between protecting against fraud and not blocking legitimate transactions."
    ),
    expected_output=(
        "A structured JSON response containing:\n"
        "{\n"
        '  "risk_score": 0.0 to 1.0,\n'
        '  "risk_level": "low" | "medium" | "high" | "critical",\n'
        '  "risk_factors": ["list of identified risk signals"],\n'
        '  "fraud_indicators": ["specific fraud patterns detected, if any"],\n'
        '  "anomalies": {"timing": bool, "amount": bool, "behavior": bool, "geographic": bool},\n'
        '  "recommendation": "approve" | "approve_with_monitoring" | "reject" | "escalate_to_human",\n'
        '  "reasoning": "Detailed explanation of risk assessment"\n'
        "}"
    ),
    agent=risk_agent,
    context=[intent_analysis_task],  # Depends on intent analysis
)

# ============================================================================
# TASK 3: POLICY VALIDATION
# ============================================================================
policy_validation_task = Task(
    description=(
        "Verify that this transaction complies with all company policies, spending limits, "
        "and regulatory requirements.\n\n"
        "You will receive:\n"
        "- Transaction amount: {amount}\n"
        "- Intent classification: {intent_output}\n"
        "- Risk assessment: {risk_output}\n"
        "- Sender and receiver details\n\n"
        "Your job is to:\n"
        "1. Check against spending limits (daily/weekly/monthly caps)\n"
        "2. Validate approval hierarchy requirements\n"
        "3. Verify jurisdictional compliance (AML/KYC, GDPR, local laws)\n"
        "4. Ensure transaction aligns with budget allocations\n"
        "5. Check for required documentation or pre-approvals\n"
        "6. Flag any policy violations with severity levels\n\n"
        "Policy Checks:\n"
        "- Spending limit: Is amount within authorized limits?\n"
        "- Approval chain: Does this require additional sign-offs?\n"
        "- Regulatory: Are there legal restrictions?\n"
        "- Documentation: Are required documents attached?\n"
        "- Timing: Are there time-based restrictions?\n\n"
        "If violations exist, suggest remediation steps."
    ),
    expected_output=(
        "A structured JSON response containing:\n"
        "{\n"
        '  "policy_passed": true | false,\n'
        '  "violations": [\n'
        '    {"type": "spending_limit" | "approval_required" | "regulatory" | "documentation",\n'
        '     "severity": "minor" | "major" | "critical",\n'
        '     "description": "Details of the violation"}\n'
        '  ],\n'
        '  "compliance_score": 0.0 to 1.0,\n'
        '  "required_approvals": ["list of required approvers, if any"],\n'
        '  "missing_documentation": ["list of missing docs, if any"],\n'
        '  "remediation_steps": ["suggested actions to become compliant"],\n'
        '  "recommendation": "approve" | "conditional_approve" | "reject" | "escalate",\n'
        '  "reasoning": "Detailed policy analysis"\n'
        "}"
    ),
    agent=policy_agent,
    context=[intent_analysis_task, risk_assessment_task],
)

# ============================================================================
# TASK 4: LIQUIDITY CHECK
# ============================================================================
liquidity_check_task = Task(
    description=(
        "Assess the financial feasibility of this transaction by evaluating account balances, "
        "cash flow, and budget constraints.\n\n"
        "You will receive:\n"
        "- Transaction amount: {amount}\n"
        "- Current account balance: {balance}\n"
        "- Daily spending limit: {daily_limit}\n"
        "- Monthly budget allocation: {monthly_budget}\n"
        "- Intent and risk assessments from previous agents\n\n"
        "Your job is to:\n"
        "1. Verify sufficient funds are available\n"
        "2. Check if transaction exceeds daily/monthly limits\n"
        "3. Assess impact on cash flow and reserves\n"
        "4. Consider upcoming obligations and commitments\n"
        "5. Determine if this would create liquidity strain\n"
        "6. Calculate remaining balance post-transaction\n\n"
        "Financial Checks:\n"
        "- Available balance vs transaction amount\n"
        "- Impact on minimum reserve requirements\n"
        "- Budget allocation vs spent-to-date\n"
        "- Cash flow forecast considerations\n"
        "- Timing of incoming funds\n\n"
        "Provide clear financial viability assessment."
    ),
    expected_output=(
        "A structured JSON response containing:\n"
        "{\n"
        '  "sufficient_funds": true | false,\n'
        '  "current_balance": float,\n'
        '  "post_transaction_balance": float,\n'
        '  "daily_limit_remaining": float,\n'
        '  "monthly_budget_remaining": float,\n'
        '  "liquidity_impact": "none" | "low" | "medium" | "high",\n'
        '  "reserve_status": "healthy" | "adequate" | "strained" | "critical",\n'
        '  "cash_flow_concerns": ["list of any cash flow issues"],\n'
        '  "recommendation": "approve" | "defer" | "reject",\n'
        '  "reasoning": "Detailed financial analysis"\n'
        "}"
    ),
    agent=treasury_agent,
    context=[intent_analysis_task, policy_validation_task],
)

# ============================================================================
# TASK 5: FINAL DECISION
# ============================================================================
final_decision_task = Task(
    description=(
        "Make the final approval or rejection decision based on all evidence gathered from "
        "specialized agents.\n\n"
        "You will receive consolidated intelligence from:\n"
        "1. Intent Agent: Transaction classification and urgency\n"
        "2. Risk Agent: Fraud risk and anomaly assessment\n"
        "3. Policy Agent: Compliance and regulatory validation\n"
        "4. Treasury Agent: Financial feasibility and liquidity status\n\n"
        "Your job is to:\n"
        "1. Synthesize all inputs into a unified decision framework\n"
        "2. Apply decision logic:\n"
        "   - APPROVE if: low risk + policy compliant + sufficient funds\n"
        "   - REJECT if: high risk OR critical policy violation OR insufficient funds\n"
        "   - ESCALATE if: medium risk + policy issues OR high uncertainty\n"
        "3. Calculate overall confidence score\n"
        "4. Provide clear, defensible reasoning\n"
        "5. Suggest next steps (execute, escalate to human, request more info)\n\n"
        "Decision Matrix:\n"
        "- All green lights → APPROVE\n"
        "- Any critical red flag → REJECT\n"
        "- Mixed signals or uncertainty → ESCALATE\n"
        "- Urgent + low risk + compliant → FAST-TRACK APPROVE\n\n"
        "Your decision must be explainable, auditable, and aligned with organizational risk tolerance."
    ),
    expected_output=(
        "A structured JSON response containing:\n"
        "{\n"
        '  "decision": "approve" | "reject" | "escalate_to_human",\n'
        '  "confidence": 0.0 to 1.0,\n'
        '  "overall_risk_level": "low" | "medium" | "high" | "critical",\n'
        '  "decision_factors": {\n'
        '    "intent_score": float,\n'
        '    "risk_score": float,\n'
        '    "policy_score": float,\n'
        '    "liquidity_score": float\n'
        '  },\n'
        '  "blocking_issues": ["list of critical issues that influenced decision"],\n'
        '  "green_lights": ["list of positive factors"],\n'
        '  "next_steps": ["specific actions to take"],\n'
        '  "human_escalation_reason": "explanation if escalated",\n'
        '  "reasoning": "Comprehensive explanation of final decision",\n'
        '  "execution_instructions": "how to proceed if approved"\n'
        "}"
    ),
    agent=decision_agent,
    context=[intent_analysis_task, risk_assessment_task, policy_validation_task, liquidity_check_task],
)

# ============================================================================
# TASK 6: AUDIT LOGGING
# ============================================================================
audit_logging_task = Task(
    description=(
        "Create a complete, immutable audit record of this transaction and all decision-making steps.\n\n"
        "You will receive:\n"
        "- Original transaction request with all metadata\n"
        "- Complete outputs from all agents (intent, risk, policy, treasury, decision)\n"
        "- Final decision and execution status\n"
        "- Timestamps for each stage\n\n"
        "Your job is to:\n"
        "1. Compile all inputs, outputs, and decisions into a comprehensive audit log\n"
        "2. Ensure traceability of every decision point\n"
        "3. Document agent reasoning and confidence levels\n"
        "4. Record any human interventions or overrides\n"
        "5. Format for regulatory compliance and legal defensibility\n"
        "6. Include metadata for search and retrieval\n"
        "7. Generate audit trail hash for immutability verification\n\n"
        "This record must:\n"
        "- Support regulatory inquiries\n"
        "- Enable forensic analysis if needed\n"
        "- Provide full transparency into AI decision-making\n"
        "- Meet compliance standards (SOX, GDPR, AML)\n"
        "- Be tamper-evident and timestamped\n\n"
        "Create a permanent record that can withstand audit scrutiny."
    ),
    expected_output=(
        "A structured JSON audit log containing:\n"
        "{\n"
        '  "audit_id": "unique identifier",\n'
        '  "transaction_id": "original transaction reference",\n'
        '  "timestamp": "ISO 8601 timestamp",\n'
        '  "transaction_details": {\n'
        '    "amount": float,\n'
        '    "sender": string,\n'
        '    "receiver": string,\n'
        '    "purpose": string\n'
        '  },\n'
        '  "agent_outputs": {\n'
        '    "intent_analysis": {full intent agent output},\n'
        '    "risk_assessment": {full risk agent output},\n'
        '    "policy_validation": {full policy agent output},\n'
        '    "liquidity_check": {full treasury agent output},\n'
        '    "final_decision": {full decision agent output}\n'
        '  },\n'
        '  "decision_trail": ["chronological sequence of decision points"],\n'
        '  "human_intervention": {"occurred": bool, "details": string},\n'
        '  "execution_status": "pending" | "executed" | "rejected" | "escalated",\n'
        '  "compliance_tags": ["SOX", "AML", "GDPR", etc.],\n'
        '  "audit_hash": "cryptographic hash for integrity",\n'
        '  "retrieval_metadata": {"indexed fields for search"}\n'
        "}\n\n"
        "Save this to permanent storage with immutability guarantees."
    ),
    agent=audit_agent,
    context=[intent_analysis_task, risk_assessment_task, policy_validation_task, 
             liquidity_check_task, final_decision_task],
)

# ============================================================================
# TASK EXECUTION ORDER
# ============================================================================
# The CrewAI framework will execute tasks in the order defined by their context dependencies:
# 1. intent_analysis_task (no dependencies)
# 2. risk_assessment_task (depends on intent)
# 3. policy_validation_task (depends on intent + risk)
# 4. liquidity_check_task (depends on intent + policy)
# 5. final_decision_task (depends on all above)
# 6. audit_logging_task (depends on all above)
