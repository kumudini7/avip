from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import settings
from app.data.use_cases import find_use_case
from app.services.assessment_classification_service import classify_assessment


class AssessmentClassificationServiceTest(unittest.TestCase):
    def test_classify_assessment_uses_local_healthcare_fallback_without_groq(self) -> None:
        questions = [
            {
                "key": "process_standardization",
                "question_text": "How standardized is your clinical/administrative process?",
                "scale_labels": {3: "About half admin/clinical steps are standardized"},
            },
            {
                "key": "human_judgment_frequency",
                "question_text": "How often does this process require clinical or administrative judgment?",
                "scale_labels": {4: "Often - most cases need clinical or admin judgment"},
            },
            {
                "key": "data_type",
                "question_text": "What type of data does the process primarily use?",
                "scale_labels": {5: "Fully unstructured - handwritten notes, radiology reports, prescriptions"},
            },
            {
                "key": "rule_change_frequency",
                "question_text": "How frequently do payer rules or clinical protocols change?",
                "scale_labels": {4: "Payer policies and clinical guidelines change frequently"},
            },
            {
                "key": "exception_rate",
                "question_text": "What % of cases require manual intervention or exception handling?",
                "scale_labels": {4: "30-50% of cases require significant manual handling"},
            },
            {
                "key": "automation_landscape",
                "question_text": "What is your current automation landscape in healthcare operations?",
                "scale_labels": {2: "Basic scripts or macros for some tasks"},
            },
            {
                "key": "ai_governance_maturity",
                "question_text": "How mature is your organisation's AI governance for clinical AI?",
                "scale_labels": {4: "AI governance established - policies and oversight in place"},
            },
            {
                "key": "compliance_criticality",
                "question_text": "How critical are compliance, auditability, and patient data privacy?",
                "scale_labels": {4: "High - clinical audit trails mandatory"},
            },
            {
                "key": "system_integration_complexity",
                "question_text": "How many systems does this process integrate with?",
                "scale_labels": {4: "Four to five - EHR + LIS + PACS + billing + payer"},
            },
            {
                "key": "primary_objective",
                "question_text": "Primary objective?",
                "scale_labels": {2: "Faster claims processing and patient throughput"},
            },
        ]

        responses_by_question = {
            "process_standardization": 3,
            "human_judgment_frequency": 4,
            "data_type": 5,
            "rule_change_frequency": 4,
            "exception_rate": 4,
            "automation_landscape": 2,
            "ai_governance_maturity": 4,
            "compliance_criticality": 4,
            "system_integration_complexity": 4,
            "primary_objective": 2,
        }

        with patch.object(settings, "groq_api_key", "", create=True):
            classification = classify_assessment(
                domain="Healthcare",
                business_context={
                    "prior_automation": "Prior authorization requests, payer portal submissions, and clinical criteria review.",
                    "documentation_level": "Clinical notes and payer policy review.",
                    "data_quality": "Mixed EHR data and unstructured fax scans.",
                    "volume_consistency": "High daily volume with recurring payer rules.",
                },
                questions=questions,
                responses_by_question=responses_by_question,
            )

        self.assertNotEqual(
            classification["matched_use_case"],
            "Not available - AI use-case matching requires GROQ_API_KEY",
        )
        self.assertEqual(classification["category"], "rpa_ai")
        self.assertGreater(classification["confidence_score"], 0)
        self.assertIsNotNone(
            find_use_case("Healthcare", classification["category"], classification["matched_use_case"])
        )


if __name__ == "__main__":
    unittest.main()
