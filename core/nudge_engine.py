"""
DecisionDelay AI — Nudge Engine
Evidence-based behavioral nudges (BJ Fogg · Gollwitzer · SDT)
"""
import random
from typing import Dict, List

NUDGE_BANK = {
    "Fear of Failure": {
        "strategies": ["Reframe failure as data", "Minimum Viable Action", "Fear-setting exercise"],
        "Fitness": [
            "Start with 5 minutes only. Showing up IS the success — performance is optional.",
            "Write the worst realistic outcome. Then ask: can you survive it? Almost always yes.",
            "Track attempts, not results. Your log shows 'tried', not 'achieved'.",
            "Do a 'comfort reps only' session today. Remove all performance pressure.",
        ],
        "Studying": [
            "Open the textbook to any page and read 1 paragraph. Begin there.",
            "Study with 'draft mode' on — notes don't need to be perfect, just get thoughts out.",
            "Take the practice test before studying. Fear loses power when exposed.",
            "Write: 'Even if I fail this, I will still...' Complete that sentence honestly.",
        ],
        "Career Choices": [
            "Apply to 3 jobs you think you're underqualified for. Rejection data > rumination.",
            "Set a 'fear deadline': make the decision by [date], imperfect info and all.",
            "Talk to someone who made a similar leap — fear needs a witness, not just advice.",
            "Ask: what would you do if failure had no social consequences? Start there.",
        ],
    },
    "Overwhelm / Complexity": {
        "strategies": ["Task decomposition", "Single next action", "2-minute rule"],
        "Fitness": [
            "Your only task: put on your workout clothes. That's the whole goal for today.",
            "Pick ONE exercise. Do it. Nothing else counts.",
            "Write the workout plan in 3 words: e.g., 'Push. Pull. Run.' Go.",
            "Tiny habit anchor: after brushing teeth → 10 squats. No gym required.",
        ],
        "Studying": [
            "Open one tab. Set a 25-min Pomodoro. Close everything else. Begin.",
            "Write the ONE thing you need to understand today. Ignore everything else.",
            "Shrink the session: study only chapter headings for 10 mins first.",
            "Make a 'dumb list': what are the 3 simplest things to do right now?",
        ],
        "Career Choices": [
            "List every sub-decision inside the big decision. Pick just ONE to decide today.",
            "Draw a 2×2: impact vs effort. Do the high-impact, low-effort thing first.",
            "Give yourself a 48-hour decision window. No research, just gut + reflection.",
            "Separate 'what to decide' from 'how to decide'. They are not the same step.",
        ],
    },
    "Lack of Immediate Reward": {
        "strategies": ["Temptation bundling", "Implementation intentions", "Progress visualization"],
        "Fitness": [
            "Bundle your workout with something you love: podcast, playlist, or post-gym coffee.",
            "Take a before photo right now. Future-you will thank present-you.",
            "Set a 14-day visible streak tracker. The streak itself becomes the reward.",
            "Plan a micro-reward after every 3 workouts. Make it genuinely exciting.",
        ],
        "Studying": [
            "Use the 'study then reward' contract: 45 min focus = 15 min guilt-free pleasure.",
            "Create a visible progress bar for the syllabus. Color in sections as you complete.",
            "Join or form a study group — social loops create short-term reward.",
            "Write a letter to your future self describing how this effort paid off.",
        ],
        "Career Choices": [
            "Create a 'decision journal': log the choice and revisit in 6 months.",
            "Find a mentor in your target role. Proximity to the future self is motivating.",
            "Set a 30-day micro-experiment toward the goal. Short timeline = faster feedback.",
            "Visualize not the destination but the first week in the new role. Make it concrete.",
        ],
    },
    "Past Failure Loop": {
        "strategies": ["Failure analysis reframe", "Identity-based habits", "Compassion reset"],
        "Fitness": [
            "You didn't fail — you gathered data. What specifically didn't work? Change one variable.",
            "Rename your identity: 'I am someone who moves daily' — even 2 min walks count.",
            "Start a fresh 7-day streak with a dramatically lower bar than before.",
            "Write: 'Last time I stopped because ___. This time I will handle that by ___.'",
        ],
        "Studying": [
            "Audit the past failure: was it method, consistency, or environment? Fix that one thing.",
            "Use spaced repetition this time (Anki). Past failures often have a method mismatch.",
            "Study with a partner. Social accountability reduces relapse into old loops.",
            "Create a 'failure-proof day': study for only 10 mins. You cannot fail at this.",
        ],
        "Career Choices": [
            "Interview yourself: why did the last attempt not work? Be specific, not self-critical.",
            "Find 3 people who failed similarly and succeeded later. Data beats narrative.",
            "Create a structured 'next attempt' plan with explicit changes from last time.",
            "Give yourself explicit permission to try again. Failure isn't a permanent verdict.",
        ],
    },
    "Perfectionism": {
        "strategies": ["Good enough threshold", "Time-boxing", "Anti-perfectionism commitment"],
        "Fitness": [
            "The 'good enough' workout beats the 'perfect' workout you never did.",
            "Set a time limit: 20 mins max. Stop when the timer ends, regardless.",
            "Track consistency %, not quality ratings. 80% attendance > 20% perfect sessions.",
            "Allow one 'ugly' workout per week intentionally. Normalize imperfect effort.",
        ],
        "Studying": [
            "Submit the imperfect draft. Revision requires a draft to exist.",
            "Set a 'done > perfect' rule: notes need to be legible, not beautiful.",
            "Time-box your studying: 30 min on each topic, move on regardless.",
            "Study with someone less meticulous than you. Exposure therapy for perfectionism.",
        ],
        "Career Choices": [
            "Make the decision with 70% of the information. You will never have 100%.",
            "Set a decision deadline. Unscheduled decisions live in perfectionism forever.",
            "List what 'good enough' looks like for this choice. Use that as your bar.",
            "Ask: what is the cost of waiting for perfect? That is often the real decision.",
        ],
    },
    "Decision Fatigue": {
        "strategies": ["Decision batching", "Environment design", "Default choices"],
        "Fitness": [
            "Decide your workout for the entire week on Sunday. No daily decisions needed.",
            "Pack your gym bag the night before. Remove decision points at the moment of action.",
            "Follow a pre-written program. Decision fatigue vanishes when choice vanishes.",
            "Set a default time: 'I work out at 7am' — not 'I'll figure it out tomorrow'.",
        ],
        "Studying": [
            "Create a fixed schedule: same time, same place, same subject order.",
            "Pre-plan tomorrow's session at the end of today's. Don't decide when tired.",
            "Use a pre-made study plan (template) rather than designing your own each time.",
            "Batch all 'what to study' decisions into one weekly planning session.",
        ],
        "Career Choices": [
            "Separate the 'gathering info' phase from the 'deciding' phase. Don't mix them.",
            "Give yourself a decision-free zone: no career thinking after 8pm.",
            "Use a decision framework (pros/cons, 10/10/10 rule) to reduce cognitive load.",
            "Batch all career research into 2 dedicated sessions per week. Contain the noise.",
        ],
    },
}

SEVERITY_PREFIX = {
    "low":    ["You're close — just one small move:", "Mild resistance detected. Try this:", "A gentle push:"],
    "medium": ["Real delay pattern detected. Here's a targeted nudge:", "This is worth addressing directly:", "Structured action needed:"],
    "high":   ["High delay severity. This needs urgent reframing:", "You're stuck deep. Try this reset:", "Critical nudge — don't skip this:"],
}


class NudgeEngine:
    def generate(self, cause: str, severity: float, use_case: str) -> Dict:
        if use_case not in ["Fitness", "Studying", "Career Choices"]:
            use_case = "Fitness"
        bank = NUDGE_BANK.get(cause, NUDGE_BANK["Overwhelm / Complexity"])
        actions = bank.get(use_case, bank.get("Fitness", []))
        strategies = bank.get("strategies", ["Focus on next action"])
        level = "low" if severity < 0.35 else "medium" if severity < 0.65 else "high"
        return {
            "cause": cause,
            "severity_level": level,
            "use_case": use_case,
            "strategy": random.choice(strategies),
            "action": random.choice(actions),
            "prefix": random.choice(SEVERITY_PREFIX[level]),
        }

    def batch(self, cause: str, severity: float, use_case: str, n: int = 3) -> List[Dict]:
        seen, results, attempts = set(), [], 0
        while len(results) < n and attempts < 30:
            nudge = self.generate(cause, severity, use_case)
            if nudge["action"] not in seen:
                seen.add(nudge["action"])
                results.append(nudge)
            attempts += 1
        return results