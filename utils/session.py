"""Session state helpers for DecisionDelay AI."""
import streamlit as st
from datetime import datetime
from typing import Dict, Any


def init_session():
    defaults = {
        "history": [],
        "current_result": None,
        "habit_log": [],
        "streak": 0,
        "total_analyses": 0,
        "user_name": "",
        "onboarded": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def save_result(result: Dict, inputs: Dict):
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "result": result,
        "inputs": inputs,
    }
    st.session_state.history.append(entry)
    st.session_state.current_result = result
    st.session_state.total_analyses += 1


def log_habit(domain: str, completed: bool, note: str = ""):
    entry = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M"),
        "domain": domain,
        "completed": completed,
        "note": note,
    }
    st.session_state.habit_log.append(entry)
    if completed:
        st.session_state.streak += 1
    else:
        st.session_state.streak = 0


def get_stats() -> Dict[str, Any]:
    history = st.session_state.history
    if not history:
        return {}
    causes = [h["result"]["delay_cause"] for h in history]
    severities = [h["result"]["delay_severity"] for h in history]
    return {
        "total": len(history),
        "avg_severity": round(sum(severities) / len(severities), 3),
        "top_cause": max(set(causes), key=causes.count),
        "causes": causes,
        "severities": severities,
    }