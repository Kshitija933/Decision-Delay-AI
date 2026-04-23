"""
DecisionDelay AI — Nudge Engine
Evidence-based behavioral nudges (BJ Fogg · Gollwitzer · SDT)
"""
from typing import Dict

NUDGE_BANK = {
    "Fear of Failure": {
        "strategy": "Fear-Setting Exercise",
        "insight": "Fear is a physiological data point, not a prediction. Action is the only known antidote to ruminative anxiety.",
        "recovery": "🔥 Worst-Case Reset: Write the absolute worst outcome. Realize you'd survive it. The fear loses its teeth.",
        "Fitness": {
            "micro_win": "Commit to just 2 minutes of movement. Success is defined by starting, not finishing.",
            "mindset_shift": "Reframe the gym as a 'stress-test' for your mind, not a judgment of your body.",
            "environment": "Lace up your shoes right now. Don't think about the workout, just the laces.",
            "tool": "Workout Buddy: Text one person that you are going. Social cost > personal fear."
        },
        "Studying": {
            "micro_win": "Read exactly one paragraph. If you want to stop then, you are allowed to.",
            "mindset_shift": "This is a 'shitty first draft' of your knowledge. Perfection is for the final exam.",
            "environment": "Clear your desk of everything except the one book you need. Space creates focus.",
            "tool": "Pomodoro: Set a 25-min timer. You are only racing the clock, not the material."
        },
        "Career Choices": {
            "micro_win": "Open your resume and change one bullet point. Just one.",
            "mindset_shift": "A 'No' from an employer is just data. A 'No' from yourself is a dead end.",
            "environment": "Close all tabs except the job application. Remove the escape hatches.",
            "tool": "LinkedIn: Send one 'low-stakes' connection request to someone in the field."
        }
    },
    "Overwhelm / Complexity": {
        "strategy": "Complexity Deconstruction",
        "insight": "Complexity is often just a collection of simple tasks pretending to be a monster. Deconstruct to conquer.",
        "recovery": "🔥 The 2-Minute Rule: If it takes less than 2 minutes, do it right now. Clear the cognitive clutter.",
        "Fitness": {
            "micro_win": "Do 10 air squats. Right where you are. Right now.",
            "mindset_shift": "You don't need a 60-min session. 10 mins of high intensity is a win.",
            "environment": "Put your gym clothes on top of your laptop. Choice architecture in action.",
            "tool": "Tabata Timer: Follow a 4-minute high-intensity routine. It's too short to be scary."
        },
        "Studying": {
            "micro_win": "Outline the chapter headings only. Get the skeleton before the meat.",
            "mindset_shift": "You aren't learning the book; you're solving 5 specific problems today.",
            "environment": "Study in a library or a focused zone. Borrow the collective willpower of the room.",
            "tool": "Mind Map: Draw the connections between 3 concepts. Visualizing reduces mental load."
        },
        "Career Choices": {
            "micro_win": "List 3 companies you like. Don't look at jobs, just list the names.",
            "mindset_shift": "You aren't picking a 'forever' career; you're picking the next 12-month experiment.",
            "environment": "Use a dedicated browser profile for career work. Contain the complexity.",
            "tool": "Decision Matrix: Score your top 3 options on Impact vs. Effort. Math beats rumination."
        }
    },
    "Lack of Immediate Reward": {
        "strategy": "Dopamine Re-Alignment",
        "insight": "The brain is wired for 'Now'. To succeed at 'Later', you must bring the reward into the present.",
        "recovery": "🔥 Dopamine Spike: Listen to your 'Power Song' at max volume for 30 seconds. Trigger the drive.",
        "Fitness": {
            "micro_win": "Take an active 'after' photo of your post-workout pump. Instant visual feedback.",
            "mindset_shift": "The gym isn't for a summer body; it's for the immediate clarity you'll feel in 20 mins.",
            "environment": "Watch a 30-second motivational clip of your favorite athlete. Borrow their 'Why'.",
            "tool": "Temptation Bundling: Only listen to your favorite podcast while you are exercising."
        },
        "Studying": {
            "micro_win": "Solve one easy problem first. Get the 'Completion Dopamine' early.",
            "mindset_shift": "Studying is an investment that pays daily dividends in confidence, not just future grades.",
            "environment": "Set up a 'Progress Wall'. Use Post-its to show every page you've mastered.",
            "tool": "Study Beats: Use Lo-Fi or Alpha-Wave audio to make the process itself pleasurable."
        },
        "Career Choices": {
            "micro_win": "Post a small professional update on LinkedIn. The 'Likes' are a short-term reward loop.",
            "mindset_shift": "Every application is a 'lottery ticket' for a better life. The more you have, the higher the odds.",
            "environment": "Treat yourself to a high-end coffee only while you do job research.",
            "tool": "Streak Tracker: Mark an 'X' on a physical calendar for every day you work on your career."
        }
    },
    "Past Failure Loop": {
        "strategy": "Identity Reset",
        "insight": "Your past is a lesson, not a life sentence. A new attempt with a new strategy is a completely new event.",
        "recovery": "🔥 Identity Reset: Say out loud: 'I am the person who adjusts and tries again.' Narrative shift.",
        "Fitness": {
            "micro_win": "Try one completely new exercise. Break the old neurological associations.",
            "mindset_shift": "The previous 'failure' was just a pilot study. Now you have the data to do it right.",
            "environment": "Change your gym or your workout time. New cues lead to new behaviors.",
            "tool": "Fitness App: Use a new tracker. A fresh interface signals a fresh start."
        },
        "Studying": {
            "micro_win": "Use a different study technique (e.g., Blurting vs. Flashcards). Shift the gear.",
            "mindset_shift": "You didn't fail last time; your *system* did. Today we switch the system.",
            "environment": "Sit in a different chair or a different room. Disrupt the 'fail' cues.",
            "tool": "Anki/Flashcards: Use Spaced Repetition. It's a data-proven way to stop the 'forgetting' loop."
        },
        "Career Choices": {
            "micro_win": "Rewrite your 'About' section from scratch. New words, new energy.",
            "mindset_shift": "One 'Yes' cancels out a thousand 'No's'. You only need to win once.",
            "environment": "Talk to a new mentor. A fresh perspective breaks the old circular thoughts.",
            "tool": "Resume Scanner: Use an AI tool to check your CV. External validation beats internal doubt."
        }
    },
    "Perfectionism": {
        "strategy": "The 70% Rule",
        "insight": "Perfectionism is just procrastination in a fancy suit. 'Done' is the only metric that matters.",
        "recovery": "🔥 The 70% Rule: If it's 70% as good as you want, it's ready to go. Shipping is the priority.",
        "Fitness": {
            "micro_win": "Do an 'ugly' workout. Messy form, mismatched clothes. Normalize imperfection.",
            "mindset_shift": "An average workout today is 100% better than the perfect workout you'll never do.",
            "environment": "Don't track any stats today. Just move for the sake of moving. Quiet the inner critic.",
            "tool": "Interval Timer: You must stop exactly when the timer beeps, even if you aren't 'finished'."
        },
        "Studying": {
            "micro_win": "Write a 'bad' summary of a page. Intentionally include a few minor errors.",
            "mindset_shift": "Your brain learns through mistakes, not through being perfectly right the first time.",
            "environment": "Use a messy notebook or scratch paper. Reduce the 'sacredness' of the study session.",
            "tool": "Speed Reading: Force yourself to move faster than you'd like. Speed kills perfectionism."
        },
        "Career Choices": {
            "micro_win": "Apply to a job you only 60% qualify for. Practice the 'reach'.",
            "mindset_shift": "Your resume is a marketing document, not a legal deposition. Highlight the wins.",
            "environment": "Set a strict 15-minute limit for writing any email or cover letter.",
            "tool": "AI Writer: Let an AI write the first draft. It breaks the 'blank page' perfectionism."
        }
    },
    "Decision Fatigue": {
        "strategy": "Choice Minimization",
        "insight": "Willpower is a rechargeable battery, and every choice drains it. Simplify to save energy.",
        "recovery": "🔥 The Coin Flip: For minor choices, flip a coin. Don't waste cognitive 'fuel' on trivialities.",
        "Fitness": {
            "micro_win": "Follow a pre-made 'Workout of the Day'. Zero decisions required.",
            "mindset_shift": "Stop deciding *if* you'll go. Decide *that* you're going. Close the mental tab.",
            "environment": "Lay out your workout gear tonight. Your 'Morning Self' has zero choices to make.",
            "tool": "App Randomizer: Let an app pick your exercises. Offload the mental labor."
        },
        "Studying": {
            "micro_win": "Study the very next thing in the syllabus. Don't browse for 'what's best'.",
            "mindset_shift": "Any study is better than the time spent deciding what to study.",
            "environment": "Block all distracting websites. Remove the recursive 'choice' to procrastinate.",
            "tool": "Study Planner: Spent 5 mins on Sunday planning the week. No daily decisions."
        },
        "Career Choices": {
            "micro_win": "Pick 3 companies and ignore the rest of the world for 24 hours. Limit the set.",
            "mindset_shift": "You can't optimize for everything. Pick the top 2 criteria and ignore everything else.",
            "environment": "Unsubscribe from job alert emails. Stop the constant drip of new choices.",
            "tool": "Decision Framework: Use the 10-10-10 rule (how will I feel in 10 mins, 10 months, 10 years?)."
        }
    }
}

class NudgeEngine:
    def generate_comprehensive(self, cause: str, severity: float, use_case: str) -> Dict:
        if use_case not in ["Fitness", "Studying", "Career Choices"]:
            use_case = "Fitness"
        
        bank = NUDGE_BANK.get(cause, NUDGE_BANK["Overwhelm / Complexity"])
        case_data = bank.get(use_case, bank["Fitness"])
        
        # Calculate severity level for backward compatibility
        level = "low" if severity < 0.35 else "medium" if severity < 0.65 else "high"
        
        return {
            "primary": case_data["micro_win"],
            "action_plan": {
                "micro_win": case_data["micro_win"],
                "mindset_shift": case_data["mindset_shift"],
                "environment": case_data["environment"],
                "tool": case_data["tool"]
            },
            "recovery": bank["recovery"],
            "insight": bank["insight"],
            # Legacy fields for backward compatibility
            "strategy": bank.get("strategy", "Strategic Action"),
            "action": case_data["micro_win"],
            "severity_level": level,
            "prefix": "Recommended:"
        }