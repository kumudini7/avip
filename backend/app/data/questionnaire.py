"""Hardcoded per-domain readiness questionnaire.

10 fixed questions per domain, each a 1-5 rating scale with a domain-specific
descriptive label at every point. Replaces the earlier admin-configurable
question bank: this questionnaire ships with the app and is not editable via UI.
"""

from __future__ import annotations

from typing import Any

# Question 6 (current automation landscape) and Question 7 (AI governance maturity)
# use identical scale labels across every domain - only the question text varies.
_AUTOMATION_LANDSCAPE_LABELS = {
    1: "Mostly manual - spreadsheets, email, phone",
    2: "Basic scripts or macros for some tasks",
    3: "RPA in pilot - one or two bots running",
    4: "Enterprise RPA - multiple bots in production",
    5: "RPA + AI initiatives already underway",
}

_AI_GOVERNANCE_LABELS = {
    1: "No AI strategy - AI not on the roadmap",
    2: "Exploring AI - awareness but no projects",
    3: "Pilot projects - one or two AI experiments",
    4: "AI governance established - policies and oversight in place",
    5: "Enterprise AI Centre of Excellence - full strategy and execution",
}

_QUESTION_ORDER = [
    "process_standardization",
    "human_judgment_frequency",
    "data_type",
    "rule_change_frequency",
    "exception_rate",
    "automation_landscape",
    "ai_governance_maturity",
    "compliance_criticality",
    "system_integration_complexity",
    "primary_objective",
]

_DOMAIN_QUESTIONS: dict[str, dict[str, dict[str, Any]]] = {
    "BFSI": {
        "process_standardization": {
            "question_text": "How standardized is your banking/financial process? (e.g. loan processing, KYC, reconciliation)",
            "scale_labels": {
                1: "Every transaction is unique, no two are alike",
                2: "Some steps are standard but many vary",
                3: "About half the process is standardized",
                4: "Most steps follow a defined process with rare exceptions",
                5: "Fully standardized, same steps every time",
            },
        },
        "human_judgment_frequency": {
            "question_text": "How often does this process require human judgment? (e.g. credit decisions, fraud review)",
            "scale_labels": {
                1: "Never - fully rule-based (e.g. data entry, reconciliation)",
                2: "Rarely - judgment needed only for edge cases",
                3: "Sometimes - moderate judgment for exceptions",
                4: "Often - most transactions need some human review",
                5: "Almost always - every transaction needs human decision",
            },
        },
        "data_type": {
            "question_text": "What type of data does the process primarily use? (1=core banking structured data, 5=emails/PDFs/trade documents)",
            "scale_labels": {
                1: "Fully structured - core banking, ERP, database fields only",
                2: "Mostly structured with some Excel/CSV reports",
                3: "Mix - structured data plus PDFs, trade documents, statements",
                4: "Mostly unstructured - letters of credit, contracts, correspondence",
                5: "Fully unstructured - free-text emails, scanned documents, images",
            },
        },
        "rule_change_frequency": {
            "question_text": "How frequently do regulatory or business rules change? (e.g. RBI/SEBI compliance updates)",
            "scale_labels": {
                1: "Rules almost never change - stable for years",
                2: "Rules change once or twice a year",
                3: "Rules change quarterly - e.g. regulatory updates",
                4: "Rules change monthly - frequent regulatory/product updates",
                5: "Rules change constantly - highly dynamic regulatory environment",
            },
        },
        "exception_rate": {
            "question_text": "What % of transactions require manual exception handling? (e.g. AML alerts, claim disputes)",
            "scale_labels": {
                1: "Less than 5% - almost all transactions flow straight through",
                2: "5-15% exceptions - mostly low-value edge cases",
                3: "15-30% exceptions - moderate manual intervention",
                4: "30-50% exceptions - high manual intervention",
                5: "More than 50% - majority of transactions need manual handling",
            },
        },
        "automation_landscape": {
            "question_text": "What is your current automation landscape in BFSI operations?",
            "scale_labels": _AUTOMATION_LANDSCAPE_LABELS,
        },
        "ai_governance_maturity": {
            "question_text": "How mature is your organisation's AI governance for financial AI? (model risk, explainability)",
            "scale_labels": _AI_GOVERNANCE_LABELS,
        },
        "compliance_criticality": {
            "question_text": "How critical are compliance, audit trail, and explainability? (e.g. regulatory reporting)",
            "scale_labels": {
                1: "Low - internal ops, no external audit requirement",
                2: "Moderate - some internal audit requirements",
                3: "Important - regular internal and external audits",
                4: "High - RBI/SEBI regulatory reporting mandatory",
                5: "Mission-critical - every decision must be explainable and auditable",
            },
        },
        "system_integration_complexity": {
            "question_text": "How many core systems does this process touch? (CBS, LOS, trade systems, payer portals)",
            "scale_labels": {
                1: "One system only - e.g. core banking or LOS",
                2: "Two systems - e.g. CBS + email",
                3: "Two to three systems - e.g. CBS + LOS + portal",
                4: "Four to five systems - e.g. CBS + trade + regulatory + email + portal",
                5: "More than five systems across multiple platforms",
            },
        },
        "primary_objective": {
            "question_text": "Primary objective? (Reduce ops cost / Faster TAT / Reduce errors / Better risk decisions / Regulatory compliance)",
            "scale_labels": {
                1: "Reduce manual effort and operational cost",
                2: "Increase processing speed and TAT",
                3: "Improve accuracy and reduce errors",
                4: "Improve decision-making with data insights",
                5: "Generate business insights and competitive intelligence",
            },
        },
    },
    "Healthcare": {
        "process_standardization": {
            "question_text": "How standardized is your clinical/administrative process? (e.g. claims, scheduling, discharge)",
            "scale_labels": {
                1: "Every patient case is handled differently",
                2: "Some admin steps are standard, clinical steps vary",
                3: "About half admin/clinical steps are standardized",
                4: "Most steps are protocol-driven with few exceptions",
                5: "Fully protocol-driven, no variation",
            },
        },
        "human_judgment_frequency": {
            "question_text": "How often does this process require clinical or administrative judgment?",
            "scale_labels": {
                1: "Never - purely administrative, no clinical input needed",
                2: "Rarely - occasional admin clarification needed",
                3: "Sometimes - clinical review needed for some cases",
                4: "Often - most cases need clinical or admin judgment",
                5: "Almost always - every patient interaction needs judgment",
            },
        },
        "data_type": {
            "question_text": "What type of data does the process primarily use? (1=structured HMS/EHR data, 5=clinical notes/radiology reports/handwritten forms)",
            "scale_labels": {
                1: "Fully structured - HMS/EHR coded fields only",
                2: "Mostly structured with some spreadsheet-based data",
                3: "Mix - structured EHR plus clinical notes, discharge summaries",
                4: "Mostly unstructured - clinical notes, radiology reports, prescriptions",
                5: "Fully unstructured - handwritten notes, images, voice recordings",
            },
        },
        "rule_change_frequency": {
            "question_text": "How frequently do payer rules, clinical protocols, or regulations change?",
            "scale_labels": {
                1: "Clinical protocols rarely change",
                2: "Protocols updated annually or during accreditation",
                3: "Payer rules or protocols change quarterly",
                4: "Payer policies and clinical guidelines change frequently",
                5: "Rules change with every patient, payer, or clinical scenario",
            },
        },
        "exception_rate": {
            "question_text": "What % of cases require manual intervention or exception handling?",
            "scale_labels": {
                1: "Less than 5% of cases need manual intervention",
                2: "5-15% of cases need manual review",
                3: "15-30% of cases require clinical judgment",
                4: "30-50% of cases require significant manual handling",
                5: "More than 50% of cases require full manual processing",
            },
        },
        "automation_landscape": {
            "question_text": "What is your current automation landscape in healthcare operations?",
            "scale_labels": _AUTOMATION_LANDSCAPE_LABELS,
        },
        "ai_governance_maturity": {
            "question_text": "How mature is your organisation's AI governance for clinical AI? (HIPAA, explainability)",
            "scale_labels": _AI_GOVERNANCE_LABELS,
        },
        "compliance_criticality": {
            "question_text": "How critical are compliance, auditability, and patient data privacy?",
            "scale_labels": {
                1: "Low - back-office admin with no patient impact",
                2: "Moderate - some admin compliance required",
                3: "Important - HIPAA and payer audit requirements",
                4: "High - clinical audit trails mandatory",
                5: "Mission-critical - patient safety and regulatory explainability required",
            },
        },
        "system_integration_complexity": {
            "question_text": "How many systems does this process integrate with? (HMS, LIS, payer portals, EHR)",
            "scale_labels": {
                1: "One system - HMS or EHR only",
                2: "Two systems - HMS + email",
                3: "Two to three - HMS + LIS + payer portal",
                4: "Four to five - EHR + LIS + PACS + billing + payer",
                5: "More than five - full hospital ecosystem",
            },
        },
        "primary_objective": {
            "question_text": "Primary objective? (Reduce admin burden / Faster claims / Reduce denials / Better patient outcomes / Compliance)",
            "scale_labels": {
                1: "Reduce administrative burden on clinical staff",
                2: "Faster claims processing and patient throughput",
                3: "Improve data quality and reduce claim denials",
                4: "Better clinical and operational decision-making",
                5: "Generate population health and operational insights",
            },
        },
    },
    "IT Services": {
        "process_standardization": {
            "question_text": "How standardized is your IT process? (e.g. onboarding, ticket triage, deployments)",
            "scale_labels": {
                1: "Every request is handled ad-hoc",
                2: "Some steps follow a pattern but most are manual",
                3: "About half the process follows defined SLAs",
                4: "Most steps follow runbooks with rare deviations",
                5: "Fully standardized runbook, zero deviation",
            },
        },
        "human_judgment_frequency": {
            "question_text": "How often does this process require human judgment? (e.g. incident RCA, code review)",
            "scale_labels": {
                1: "Never - fully scripted, zero decision-making",
                2: "Rarely - only escalations need human input",
                3: "Sometimes - L2 judgment needed for complex tickets",
                4: "Often - most incidents need engineer analysis",
                5: "Almost always - every request needs human reasoning",
            },
        },
        "data_type": {
            "question_text": "What type of data does the process primarily use? (1=structured ITSM/JIRA data, 5=logs/emails/unstructured tickets)",
            "scale_labels": {
                1: "Fully structured - ITSM/Jira fields, database records",
                2: "Mostly structured with some email notifications",
                3: "Mix - structured tickets plus log files, error dumps",
                4: "Mostly unstructured - incident logs, code repos, emails",
                5: "Fully unstructured - free-text logs, chat, unstructured documentation",
            },
        },
        "rule_change_frequency": {
            "question_text": "How frequently do business rules or SLA policies change?",
            "scale_labels": {
                1: "SLA policies and runbooks rarely change",
                2: "Policies updated occasionally, infrequent sprints",
                3: "Sprint-level policy changes every few months",
                4: "Rules change with every release cycle",
                5: "Rules change daily - highly agile, continuous deployment",
            },
        },
        "exception_rate": {
            "question_text": "What % of tickets/tasks require manual exception handling?",
            "scale_labels": {
                1: "Less than 5% of tickets escalate",
                2: "5-15% of requests need L2 involvement",
                3: "15-30% of tickets need engineer intervention",
                4: "30-50% of requests need senior engineer input",
                5: "More than 50% of requests are fully manual",
            },
        },
        "automation_landscape": {
            "question_text": "What is your current automation landscape in IT operations?",
            "scale_labels": _AUTOMATION_LANDSCAPE_LABELS,
        },
        "ai_governance_maturity": {
            "question_text": "How mature is your organisation's AI/DevOps governance?",
            "scale_labels": _AI_GOVERNANCE_LABELS,
        },
        "compliance_criticality": {
            "question_text": "How critical are auditability and compliance? (e.g. SOC2, ISO27001)",
            "scale_labels": {
                1: "Low - internal tooling, no compliance requirement",
                2: "Moderate - some SLA reporting required",
                3: "Important - SOC 2 or ISO 27001 compliance",
                4: "High - security and compliance audits frequent",
                5: "Mission-critical - every action logged for security compliance",
            },
        },
        "system_integration_complexity": {
            "question_text": "How many systems does this process touch? (ServiceNow, Jira, GitHub, Slack, cloud platforms)",
            "scale_labels": {
                1: "One system - ServiceNow or Jira only",
                2: "Two systems - ITSM + email",
                3: "Two to three - ITSM + Jira + GitHub",
                4: "Four to five - ITSM + Jira + GitHub + Slack + cloud",
                5: "More than five - full DevOps + cloud + security stack",
            },
        },
        "primary_objective": {
            "question_text": "Primary objective? (Reduce MTTR / Faster delivery / Improve quality / Better decisions / Cost reduction)",
            "scale_labels": {
                1: "Reduce manual IT operations effort",
                2: "Faster incident resolution and deployment",
                3: "Improve code quality and reduce defects",
                4: "Better engineering and business decisions",
                5: "Generate engineering and business intelligence",
            },
        },
    },
    "Manufacturing": {
        "process_standardization": {
            "question_text": "How standardized is your manufacturing process? (e.g. PO generation, quality inspection, shift reporting)",
            "scale_labels": {
                1: "Every production run is unique",
                2: "Some steps are standard but exceptions are frequent",
                3: "Most steps are defined but flexibility exists",
                4: "Most steps are defined and rarely deviate",
                5: "Completely standardized, same every time",
            },
        },
        "human_judgment_frequency": {
            "question_text": "How often does this process require human judgment? (e.g. defect classification, maintenance decisions)",
            "scale_labels": {
                1: "Never - machine parameters decide everything",
                2: "Rarely - only breakdown scenarios need judgment",
                3: "Sometimes - quality exceptions need human call",
                4: "Often - most quality checks need human sign-off",
                5: "Almost always - every production decision is manual",
            },
        },
        "data_type": {
            "question_text": "What type of data does the process primarily use? (1=structured ERP/MES data, 5=images/sensor streams/maintenance notes)",
            "scale_labels": {
                1: "Fully structured - ERP/MES/SCADA numeric data",
                2: "Mostly structured with some maintenance logs",
                3: "Mix - ERP data plus sensor streams, inspection images",
                4: "Mostly unstructured - maintenance notes, defect images, reports",
                5: "Fully unstructured - camera feeds, freeform operator notes",
            },
        },
        "rule_change_frequency": {
            "question_text": "How frequently do production rules, BOMs, or supplier terms change?",
            "scale_labels": {
                1: "Production rules and BOMs rarely change",
                2: "Rules change with new product lines (annual)",
                3: "Rules change with supplier or product updates",
                4: "Production parameters change frequently",
                5: "Rules change with every production order",
            },
        },
        "exception_rate": {
            "question_text": "What % of production transactions require manual intervention?",
            "scale_labels": {
                1: "Less than 5% of production runs have exceptions",
                2: "5-15% of batches have quality exceptions",
                3: "15-30% of runs need human quality sign-off",
                4: "30-50% of production steps need manual oversight",
                5: "More than 50% of production steps are manual",
            },
        },
        "automation_landscape": {
            "question_text": "What is your current automation landscape in manufacturing ops?",
            "scale_labels": _AUTOMATION_LANDSCAPE_LABELS,
        },
        "ai_governance_maturity": {
            "question_text": "How mature is your organisation's AI/Industry 4.0 strategy?",
            "scale_labels": _AI_GOVERNANCE_LABELS,
        },
        "compliance_criticality": {
            "question_text": "How critical are compliance and traceability? (e.g. ISO, FDA, GMP)",
            "scale_labels": {
                1: "Low - internal reporting, no regulatory requirement",
                2: "Moderate - some quality documentation needed",
                3: "Important - ISO or quality management compliance",
                4: "High - FDA, GMP, or traceability mandatory",
                5: "Mission-critical - full traceability for regulatory certification",
            },
        },
        "system_integration_complexity": {
            "question_text": "How many systems does this process integrate with? (SAP, MES, SCADA, WMS, supplier portals)",
            "scale_labels": {
                1: "One system - ERP or MES only",
                2: "Two systems - ERP + email",
                3: "Two to three - ERP + MES + WMS",
                4: "Four to five - ERP + MES + SCADA + WMS + supplier portal",
                5: "More than five - full Industry 4.0 ecosystem",
            },
        },
        "primary_objective": {
            "question_text": "Primary objective? (Reduce downtime / Improve quality / Cut costs / Faster fulfilment / Better decisions)",
            "scale_labels": {
                1: "Reduce manual production and reporting effort",
                2: "Faster production cycles and fulfilment",
                3: "Improve product quality and reduce defects",
                4: "Better production and quality decisions",
                5: "Generate operational and predictive insights",
            },
        },
    },
    "Retail & Customer Service": {
        "process_standardization": {
            "question_text": "How standardized is your retail/service process? (e.g. order processing, returns, inventory sync)",
            "scale_labels": {
                1: "Every order/request is handled differently",
                2: "Some steps are standard but many vary",
                3: "About half the process is standardized",
                4: "Most steps follow a defined process",
                5: "Completely standardized, same every time",
            },
        },
        "human_judgment_frequency": {
            "question_text": "How often does this process require human judgment? (e.g. return fraud, pricing decisions)",
            "scale_labels": {
                1: "Never - rule-based order processing",
                2: "Rarely - only fraud flags need review",
                3: "Sometimes - returns/disputes need review",
                4: "Often - pricing and exceptions need human approval",
                5: "Almost always - every request needs personal handling",
            },
        },
        "data_type": {
            "question_text": "What type of data does the process primarily use? (1=structured OMS/ERP data, 5=emails/chat/images/reviews)",
            "scale_labels": {
                1: "Fully structured - OMS/ERP order fields",
                2: "Mostly structured with some email orders",
                3: "Mix - OMS data plus customer emails, chat messages",
                4: "Mostly unstructured - reviews, social messages, return reasons",
                5: "Fully unstructured - free-text emails, images, chat transcripts",
            },
        },
        "rule_change_frequency": {
            "question_text": "How frequently do pricing rules, promotions, or return policies change?",
            "scale_labels": {
                1: "Pricing and return policies rarely change",
                2: "Policies change seasonally",
                3: "Promotions and rules change monthly",
                4: "Pricing rules change weekly",
                5: "Rules change daily - flash sales, dynamic pricing",
            },
        },
        "exception_rate": {
            "question_text": "What % of orders/requests require manual exception handling?",
            "scale_labels": {
                1: "Less than 5% of orders need manual handling",
                2: "5-15% of orders have issues",
                3: "15-30% of orders or returns need manual review",
                4: "30-50% of customer interactions need agent handling",
                5: "More than 50% of transactions require manual handling",
            },
        },
        "automation_landscape": {
            "question_text": "What is your current automation landscape in retail operations?",
            "scale_labels": _AUTOMATION_LANDSCAPE_LABELS,
        },
        "ai_governance_maturity": {
            "question_text": "How mature is your organisation's AI/personalization strategy?",
            "scale_labels": _AI_GOVERNANCE_LABELS,
        },
        "compliance_criticality": {
            "question_text": "How critical are compliance and auditability? (e.g. consumer protection, marketplace policies)",
            "scale_labels": {
                1: "Low - internal ops, no regulatory requirement",
                2: "Moderate - some consumer protection requirements",
                3: "Important - marketplace policy compliance",
                4: "High - financial and consumer compliance critical",
                5: "Mission-critical - full audit trail for financial compliance",
            },
        },
        "system_integration_complexity": {
            "question_text": "How many systems does this process touch? (OMS, ERP, CRM, marketplace APIs, payment gateway)",
            "scale_labels": {
                1: "One system - OMS only",
                2: "Two systems - OMS + email",
                3: "Two to three - OMS + ERP + CRM",
                4: "Four to five - OMS + ERP + CRM + marketplace + payment",
                5: "More than five - full omnichannel ecosystem",
            },
        },
        "primary_objective": {
            "question_text": "Primary objective? (Reduce ops cost / Faster fulfilment / Better CX / Personalisation / Reduce returns)",
            "scale_labels": {
                1: "Reduce manual order processing and ops cost",
                2: "Faster order fulfilment and delivery",
                3: "Improve order accuracy and reduce returns",
                4: "Better pricing, inventory, and CX decisions",
                5: "Generate customer and market insights",
            },
        },
    },
}


BUSINESS_OBJECTIVE_OPTIONS = [
    {"key": "reduce_cost", "label": "Reduce Cost"},
    {"key": "improve_cx", "label": "Improve Customer Experience"},
    {"key": "increase_revenue", "label": "Increase Revenue"},
    {"key": "improve_compliance", "label": "Improve Compliance"},
    {"key": "reduce_risk", "label": "Reduce Risk"},
    {"key": "improve_quality", "label": "Improve Quality"},
]

# Questions added on top of the original 10 domain-flavored ones, to power the
# Process DNA / Decision Complexity / AI Readiness / Business Case dashboard
# blocks. These are shared verbatim across every domain (rather than getting
# bespoke per-domain text like the original 10) to keep the addition
# tractable - four of the six Decision Complexity parameters and two of the
# five AI Readiness areas are intentionally answered by reusing existing keys
# above instead of asking the same thing twice (see readiness_scoring_service
# and final_scorecard_service).
_EXTENDED_QUESTION_ORDER = [
    "business_objectives",
    "process_dna_rule_based",
    "process_dna_human_judgment",
    "process_dna_knowledge_dependency",
    "process_dna_creativity",
    "process_dna_collaboration",
    "recommendations_needed",
    "risk_of_wrong_decision",
    "ai_data_readiness",
    "ai_infrastructure_readiness",
    "ai_skills_readiness",
    "current_compliance_rate",
    "current_error_rate",
]

_SHARED_EXTENDED_QUESTIONS: dict[str, dict[str, Any]] = {
    "business_objectives": {
        "question_text": "Why are you automating this process? (select all that apply)",
        "question_type": "multi_select",
        "options": BUSINESS_OBJECTIVE_OPTIONS,
    },
    "process_dna_rule_based": {
        "question_text": "What % of this process follows fixed, deterministic rules?",
        "question_type": "percent",
    },
    "process_dna_human_judgment": {
        "question_text": "What % of this process requires human judgment or discretion?",
        "question_type": "percent",
    },
    "process_dna_knowledge_dependency": {
        "question_text": "What % of this process depends on specialised knowledge or expertise?",
        "question_type": "percent",
    },
    "process_dna_creativity": {
        "question_text": "What % of this process requires creative or novel problem-solving?",
        "question_type": "percent",
    },
    "process_dna_collaboration": {
        "question_text": "What % of this process requires cross-team or cross-system collaboration?",
        "question_type": "percent",
    },
    "recommendations_needed": {
        "question_text": "Does the process need the system to proactively recommend a next-best action, rather than just execute steps?",
        "scale_labels": {
            1: "No recommendation needed - purely execute fixed steps",
            2: "Rarely - occasional suggestions would help",
            3: "Sometimes - recommendations would help with some cases",
            4: "Often - most cases benefit from a suggested next action",
            5: "Always - the process is centred on recommending the best action",
        },
    },
    "risk_of_wrong_decision": {
        "question_text": "What is the business impact if an automated decision in this process is wrong?",
        "scale_labels": {
            1: "Negligible - easily caught and corrected, no real impact",
            2: "Minor - small rework cost, no external impact",
            3: "Moderate - noticeable cost or customer impact",
            4: "High - significant financial, compliance, or reputational impact",
            5: "Severe - safety, legal, or major financial consequences",
        },
    },
    "ai_data_readiness": {
        "question_text": "How ready is your data (quality, accessibility, labeling) for AI use?",
        "scale_labels": {
            1: "Data is scattered, inconsistent, or largely inaccessible",
            2: "Some data is centralised but quality/labeling is poor",
            3: "Data is reasonably clean and accessible, moderate quality",
            4: "Data is well-structured, accessible, and mostly clean",
            5: "Data is high-quality, labeled, and readily available for AI",
        },
    },
    "ai_infrastructure_readiness": {
        "question_text": "How ready is your infrastructure (compute, APIs, cloud access) for AI/agentic deployment?",
        "scale_labels": {
            1: "No cloud/API access, on-prem only, no AI infrastructure",
            2: "Limited infrastructure, mostly manual/legacy systems",
            3: "Some cloud and API access, partial AI-readiness",
            4: "Good cloud/API infrastructure, ready for most AI workloads",
            5: "Full cloud-native infrastructure with mature AI/ML platform",
        },
    },
    "ai_skills_readiness": {
        "question_text": "How mature are your team's AI/ML skills?",
        "scale_labels": {
            1: "No AI/ML skills in the team",
            2: "Basic awareness, no hands-on experience",
            3: "Some team members have applied AI/ML experience",
            4: "Dedicated AI/ML practitioners on the team",
            5: "Mature AI/ML/engineering practice with proven delivery",
        },
    },
    "current_compliance_rate": {
        "question_text": "What % of this process currently meets compliance requirements?",
        "question_type": "percent",
    },
    "current_error_rate": {
        "question_text": "What % of transactions in this process currently contain errors or require rework?",
        "question_type": "percent",
    },
}


def get_questionnaire(domain: str) -> list[dict[str, Any]]:
    domain_questions = _DOMAIN_QUESTIONS.get(domain, {})
    questions: list[dict[str, Any]] = []

    for key in _QUESTION_ORDER:
        if key not in domain_questions:
            continue
        questions.append(
            {
                "key": key,
                "question_text": domain_questions[key]["question_text"],
                "question_type": "rating",
                "scale_labels": domain_questions[key]["scale_labels"],
                "options": None,
            }
        )

    for key in _EXTENDED_QUESTION_ORDER:
        definition = _SHARED_EXTENDED_QUESTIONS[key]
        questions.append(
            {
                "key": key,
                "question_text": definition["question_text"],
                "question_type": definition.get("question_type", "rating"),
                "scale_labels": definition.get("scale_labels", {}),
                "options": definition.get("options"),
            }
        )

    return questions


def get_question_keys() -> list[str]:
    return list(_QUESTION_ORDER) + list(_EXTENDED_QUESTION_ORDER)
