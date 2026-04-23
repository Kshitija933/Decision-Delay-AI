"""
DecisionDelay AI — Inference Module
Unified prediction interface for Streamlit pages.
"""
from typing import Dict
from core.analyzer import DelayAnalyzer
from core.nudge_engine import NudgeEngine

_analyzer = DelayAnalyzer()
_nudge    = NudgeEngine()


def run_prediction(inputs: Dict) -> Dict:
    """
    Full prediction pipeline.
    Falls back to rule-based mock if model not trained yet.
    """
    if _analyzer.is_ready():
        loaded = _analyzer.load()
        if loaded:
            result = _analyzer.predict(inputs)
        else:
            result = _analyzer.predict_mock(inputs)
    else:
        result = _analyzer.predict_mock(inputs)

    cause    = result["delay_cause"]
    severity = result["delay_severity"]
    use_case = inputs.get("use_case", "Fitness")

    nudges = _nudge.generate_comprehensive(cause, severity, use_case)
    
    return {
        **result,
        "nudge": nudges,
        "inputs": inputs,
        "model_used": "trained" if _analyzer._loaded else "rule_based",
    }