# import time
# import os
# from groq import Groq
# from dotenv import load_dotenv
# import pdfplumber


# # ------------------ ENV SETUP ------------------
# load_dotenv()

# API_KEY = os.getenv("API_KEY")
# if not API_KEY:
#     raise ValueError("❌ GROQ API key not found. Please set API_KEY in .env")

# client = Groq(api_key=API_KEY)

# # ------------------ SYSTEM PROMPT ------------------
# SYSTEM_PROMPT = """
# You are AIVA, a senior technical interviewer at a top technology company.

# Rules:
# - Ask ONLY one question at a time
# - Be professional, calm, and encouraging
# - Do NOT reveal answers unless explicitly asked
# - Increase difficulty gradually
# - Keep questions realistic and concise
# - If the candidate struggles, reassure politely
# - Maintain a natural interview flow

# Interview Flow:
# 1. Warm-up
# 2. Core technical questions
# 3. Scenario-based / problem-solving
# 4. Wrap-up

# Tone:
# Professional, friendly, confident
# """
# import json

# # ------------------ INTERVIEW BOT ------------------
# class InterviewBot:
#     def __init__(self):
#         self.start_time = None
#         self.skill = None
#         self.history = []
#         self.ended = False

#         # ⭐ NEW: Vision support (does not affect old logic)
#         self.vision = None
#         self.behavior_log = []

#     # ⭐ NEW: Attach camera system
#     def attach_vision(self, vision):
#         self.vision = vision

#     # ---------- START INTERVIEW ----------
#     def start_interview(self, setup=None):
#         self.start_time = time.time()
#         self.history.clear()
#         self.ended = False
#         self.behavior_log.clear()

#         if not setup:
#             return {
#                 "role": "assistant",
#                 "message": "⚠️ Interview setup is missing. Please restart the interview from the setup page."
#             }

#         self.setup = setup

#         name = self.setup.get("name", "Candidate")
#         topic = self.setup.get("topic")
#         difficulty = self.setup.get("difficulty", "Intermediate")
#         mode = self.setup.get("mode", "Concept Based")

#         self.skill = topic

#         print("SETUP RECEIVED:", self.setup)

#         return {
#             "role": "assistant",
#             "message": (
#                 f"Hello {name}, welcome to your technical interview. 👋\n\n"
#                 f"I’m **AIVA**, and I’ll be conducting your **{difficulty}-level** interview on **{topic}** today.\n\n"
#                 f"🧠 **Interview Format:** {mode}\n"
#                 f"⏱️ **Structure:** We’ll begin with a short warm-up, then move into core technical and problem-solving questions.\n\n"
#                 f"Please feel free to think aloud while answering — clarity of thought is as important as correctness.\n\n"
#                 f"---\n"
#                 f"### 🚀 Warm-up Question\n\n"
#                 f"👉 **What is {topic}, and in which real-world scenarios is it commonly used?**"
#             )
#         }


#     # ---------- HANDLE USER MESSAGE ----------
#     def ask_question(self, user_message: str):
#         user_message = user_message.strip()

#         # End session
#         if user_message.lower() in ["end session", "end interview", "quit", "exit"]:
#             self.ended = True
#             return self.generate_report()

#         # Skill selection
#         if not self.skill:
#             self.skill = user_message

#             prompt = f"""
# You are starting a technical interview on **{self.skill}**.

# Begin with a brief warm-up question suitable for an interview.
# Ask ONLY the first question.
# """
#         else:
#             prompt = f"""
# Continue the technical interview on **{self.skill}**.

# Based on the candidate’s previous answer:
# - Internally evaluate it but in two to three sentences but in easy language
# - Ask next question accordingly.
# - Provide constructive feedback if necessary
# - Ask the NEXT appropriate question 

# """

#         self.history.append({"role": "user", "content": user_message})

#         completion = client.chat.completions.create(
#             model="llama-3.1-8b-instant",
#             messages=[
#                 {"role": "system", "content": SYSTEM_PROMPT},
#                 {"role": "system", "content": prompt},
#                 *self.history
#             ],
#             temperature=0.6,
#         )

#         reply = completion.choices[0].message.content.strip()
#         self.history.append({"role": "assistant", "content": reply})

#         # ⭐ NEW: store live behavior snapshot (safe)
#         if self.vision:
#             self.behavior_log.append(self.vision.get_metrics())

#         return {
#             "role": "assistant",
#             "message": reply
#         }

#     # ---------- GENERATE REPORT ----------
#     def generate_report(self):
#         time_taken = round(time.time() - self.start_time, 2)

#         report_prompt = f"""
# You are a STRICT and HONEST technical interviewer.

# Your job is to generate a FACT-BASED evaluation report.

# Skill Interviewed: {self.skill}

# Conversation History:
# {self.history}

# Behavior Metrics (camera data):
# {self.behavior_log}

# IMPORTANT RULES:
# - Do NOT assume any knowledge the candidate did not clearly show.
# - If answers are vague, short, incorrect, or unclear, list them as weaknesses.
# - If the candidate said "I don't know", "not sure", or avoided a question, mention it.
# - Only list a skill as STRONG if it was clearly demonstrated with explanation or example.
# - Use behavior metrics to judge confidence, stress, comfort, and stability.
# - Be realistic, not motivational.
# - It is OK if the report is negative.

# You MUST return STRICT JSON in the following format and NOTHING ELSE:

# {{
#   "summary": "Short honest summary of performance",
#   "strengths": ["clear strengths based only on answers"],
#   "weaknesses": ["clear weaknesses based only on answers"],
#   "strong_skills": ["only skills clearly demonstrated"],
#   "moderate_skills": ["skills partially demonstrated"],
#   "recommendation": "What the candidate should study and improve",
#   "overall_rating": number from 1 to 10
# }}

# SCORING GUIDE:
# 1-3 = Very weak
# 4-5 = Beginner
# 6 = Average
# 7 = Decent
# 8 = Good
# 9 = Very good
# 10 = Excellent

# Be STRICT. Be HONEST. Be REALISTIC.
# """


#         completion = client.chat.completions.create(
#             model="llama-3.1-8b-instant",
#             messages=[
#                 {"role": "system", "content": report_prompt}
#             ],
#             temperature=0.4,
#         )

#         raw = completion.choices[0].message.content.strip()
#         try:
#             report = json.loads(raw)
#         except:
#     # fallback if model outputs bad format
#             report = {
#             "summary": raw,
#             "strengths": [],
#             "weaknesses": [],
#             "strong_skills": [],
#             "moderate_skills": [],
#             "recommendation": "Needs improvement",
#             "overall_rating": 5
#         }


#         return {
#             "role": "assistant",
#             "ended": True,
#             "time_taken_seconds": time_taken,
#             "report": report
#         }


import time
import os
from groq import Groq
from dotenv import load_dotenv
import pdfplumber
import json

# ------------------ ENV SETUP ------------------
load_dotenv()

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("❌ GROQ API key not found. Please set API_KEY in .env")

client = Groq(api_key=API_KEY)

# ------------------ SYSTEM PROMPT ------------------
SYSTEM_PROMPT = """
You are AIVA, a senior technical interviewer at a top technology company.

Rules:
- Ask ONLY one question at a time
- Keep your question precise
- Be professional, calm, and encouraging
- Do NOT reveal answers unless explicitly asked
- Increase difficulty gradually
- Keep questions realistic and concise
- If the candidate struggles, reassure politely
- Maintain a natural interview flow
-if someone asked about who create you say created by abuzar maroof and aareb khan

Interview Flow:
1. Warm-up
2. Core technical questions
3. Scenario-based / problem-solving
4. Wrap-up

Tone:
Professional, friendly, confident
"""

# ------------------ INTERVIEW BOT ------------------
class InterviewBot:
    def __init__(self):
        self.start_time = None
        self.skill = None
        self.history = []
        self.ended = False

        # Vision support
        self.vision = None
        self.behavior_log = []

        # ⭐ NEW: dynamic context (resume / notes / topic)
        self.dynamic_system_prompt = ""

    def attach_vision(self, vision):
        self.vision = vision

    # ---------- START INTERVIEW ----------
    def start_interview(self, setup=None):
        self.start_time = time.time()
        self.history.clear()
        self.ended = False
        self.behavior_log.clear()

        if not setup:
            return {
                "role": "assistant",
                "message": "⚠️ Interview setup is missing. Please restart the interview from the setup page."
            }

        self.setup = setup

        name = setup.get("name", "Candidate")
        topic = (setup.get("topic") or "").strip()
        difficulty = setup.get("difficulty", "Intermediate")
        mode = setup.get("mode", "Conceptual")

        # ⭐ THESE TWO MUST COME FROM FRONTEND
        resume_text = (setup.get("resume_text") or "").strip()
        notes_text = (setup.get("notes_text") or "").strip()

        print("SETUP RECEIVED KEYS:", setup)

        # ---------- DECIDE SOURCE ----------
        if resume_text:
            source = "resume"
            self.skill = "Resume"
            context_text = resume_text

        elif notes_text:
            source = "notes"
            self.skill = "Notes"
            context_text = notes_text

        elif topic:
            source = "topic"
            self.skill = topic
            context_text = ""

        else:
            return {
                "role": "assistant",
                "message": "⚠️ Please provide at least one: Topic or Resume or Notes."
            }

        # ---------- BUILD SYSTEM CONTEXT ----------
        if source in ["resume", "notes"]:
            self.dynamic_system_prompt = f"""
    You are a senior technical interviewer.

    This is the candidate's document:

    ----------------
    {context_text[:6000]}
    ----------------

    Rules:
    - Ask questions ONLY from this content
    - Ask about projects, skills, technologies mentioned
    - Do NOT ask generic theory questions
    - Be realistic and professional
    - Ask only ONE question at a time
    """

            warmup = (
                "Can you walk me through your background and then explain one project or skill you are most confident about?"
            )

        else:
            self.dynamic_system_prompt = f"""
    You are taking a technical interview on the topic: {topic}
    """

            warmup = (
                f"Before we go deep, tell me in your own words what {topic} is and where you have used or seen it."
            )

        # ---------- BUILD SHORT INTRO ----------
        if source in ["resume", "notes"]:
            intro = (
                f"Hello {name}. I’m AIVA, your virtual interviewer.\n"
                f"I’ve reviewed your {source} and I’ll be asking questions based on it.\n"
                f"Let’s begin.\n\n"
            )
        else:
            intro = (
                f"Hello {name}. I’m AIVA, your virtual interviewer.\n"
                f"Your interview on {topic} is starting now.\n"
                f"Let’s begin.\n\n"
            )

        return {
            "role": "assistant",
            "message": intro + warmup
        }


    # ---------- HANDLE USER MESSAGE ----------
    def ask_question(self, user_message: str):
        user_message = user_message.strip()

        # End session
        if user_message.lower() in ["end session", "end interview", "quit", "exit"]:
            self.ended = True
            return self.generate_report()

        # Build prompt
        if not self.history:
            prompt = """
Start the interview properly.
Ask the NEXT logical question based on the context.
Ask only ONE question.
"""
        else:
            prompt = """
Continue the interview.

Based on the candidate’s previous answer:
- Briefly evaluate internally (do not over-praise)
- Ask the NEXT logical interview question
- Keep it realistic and professional
- Ask only ONE question
"""

        self.history.append({"role": "user", "content": user_message})

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "system", "content": self.dynamic_system_prompt},
                {"role": "system", "content": prompt},
                *self.history
            ],
            temperature=0.6,
        )

        reply = completion.choices[0].message.content.strip()
        self.history.append({"role": "assistant", "content": reply})

        # Store live behavior snapshot
        if self.vision:
            self.behavior_log.append(self.vision.get_metrics())

        return {
            "role": "assistant",
            "message": reply
        }

    # ---------- GENERATE REPORT ----------
        # ---------- GENERATE REPORT (PRACTICE / TRAINING MODE) ----------
    def generate_report(self):
        time_taken = round(time.time() - self.start_time, 2)

        # Collect user answers
        user_answers = [
            msg["content"]
            for msg in self.history
            if msg["role"] == "user" and msg["content"].strip()
        ]

        # If user really did nothing
        if len(user_answers) == 0:
            return {
                "role": "assistant",
                "ended": True,
                "time_taken_seconds": time_taken,
                "report": {
                    "summary": "You did not answer any questions, so the interview could not be evaluated.",
                    "strengths": [],
                    "weaknesses": ["No answers were provided"],
                    "strong_skills": [],
                    "moderate_skills": [],
                    "weak_skills": ["Communication", "Concept clarity"],
                    "recommendation": "Try again and attempt the questions. This system is for practice and improvement.",
                    "overall_rating": 10,
                    "scores": {
                        "overall": 10,
                        "completeness": 0,
                        "communication": 0,
                        "technical": 0,
                        "confidence": 0
                    }
                }
            }

        # ---------- USE LLM AS THE REAL EVALUATOR ----------
        report_prompt = f"""
You are a friendly but honest technical mentor.

This is a PRACTICE interview, not a hiring decision.

Your job:
- Analyze the candidate's answers
- Find strengths and weaknesses
- Guide the candidate how to improve
- Be constructive, honest, and practical
- If answers are weak, clearly say so
- If answers are okay, encourage and suggest improvements
- If answers are good, still suggest how to become better

Candidate answers:
{user_answers}

Return ONLY valid JSON in this format:

{{
"summary": "string",
"strengths": ["string"],
"weaknesses": ["string"],
"strong_skills": ["string"],
"moderate_skills": ["string"],
"weak_skills": ["string"],
"recommendation": "string",
"overall_rating": number,   // 0–100 realistic practice score
"scores": {{
    "overall": number,
    "completeness": number,
    "communication": number,
    "technical": number,
    "confidence": number
}}
}}

Rules:
- Be realistic and consistent
- If answers are weak, scores should be low (30–50)
- If answers are average, scores should be medium (50–70)
- If answers are good, scores can be higher (70–85)
- Rarely give above 90
- Scores and text MUST agree with each other
"""

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": report_prompt}],
            temperature=0.3,
        )

        raw = completion.choices[0].message.content.strip()

        try:
            report = json.loads(raw)
        except:
            report = {
                "summary": "Your answers were recorded, but the system could not generate a proper evaluation.",
                "strengths": [],
                "weaknesses": ["Could not analyze answers properly"],
                "strong_skills": [],
                "moderate_skills": [],
                "weak_skills": ["General understanding"],
                "recommendation": "Please try again and give clearer answers.",
                "overall_rating": 40,
                "scores": {
                    "overall": 40,
                    "completeness": 40,
                    "communication": 40,
                    "technical": 40,
                    "confidence": 40
                }
            }

        # ---------- SOFT ADJUST CONFIDENCE USING VISION ----------
        if self.behavior_log:
            avg_conf = sum(b.get("confidence", 50) for b in self.behavior_log) / len(self.behavior_log)
            avg_stress = sum(b.get("stress", 50) for b in self.behavior_log) / len(self.behavior_log)
            vision_conf = int(avg_conf * 0.7 + (100 - avg_stress) * 0.3)

            # Blend with LLM confidence
            report["scores"]["confidence"] = int(
                (report["scores"].get("confidence", 50) * 0.7) + (vision_conf * 0.3)
            )

        return {
            "role": "assistant",
            "ended": True,
            "time_taken_seconds": time_taken,
            "report": report
        }

#     def generate_report(self):
#         time_taken = round(time.time() - self.start_time, 2)

#         report_prompt = f"""
# You are a STRICT and HONEST technical interviewer.                                                                                            
        
# Skill Interviewed: {self.skill}

# Conversation History:
# {self.history}

# Behavior Metrics:
# {self.behavior_log}

# Rules:
# - Be honest and realistic
# - Do not assume knowledge
# - Only judge from answers

# Return STRICT JSON only.
# """

#         completion = client.chat.completions.create(
#             model="llama-3.1-8b-instant",
#             messages=[
#                 {"role": "system", "content": report_prompt}
#             ],
#             temperature=0.4,
#         )

#         raw = completion.choices[0].message.content.strip()
#         try:
#             report = json.loads(raw)
#         except:
#             report = {
#                 "summary": raw,
#                 "strengths": [],
#                 "weaknesses": [],
#                 "strong_skills": [],
#                 "moderate_skills": [],
#                 "recommendation": "Needs improvement",
#                 "overall_rating": 5
#             }

#         return {
#             "role": "assistant",
#             "ended": True,
#             "time_taken_seconds": time_taken,
#             "report": report
#         }
