# quizzard_gemini_prototype.py
import os
import json
import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import List, Dict, Any
import threading

# --- Gemini client (google-genai) ---
try:
    import google.genai as genai
except Exception as e:
    raise RuntimeError("google-genai not found. Install with: pip install google-genai") from e

# ---------------- Gemini Wrapper ----------------
class GeminiClient:
    def __init__(self, model: str = None):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError("❌ GEMINI_API_KEY is missing.")
        try:
            self.client = genai.Client(api_key=api_key)
            available_models = [m.name for m in self.client.models.list()]
        except Exception as e:
            raise RuntimeError(f"❌ Gemini API Error: {e}") from e

        default_model = None
        for m in available_models:
            if "gemini" in m.lower():
                default_model = m
                break
        self.model = model if model in available_models else default_model
        if not self.model:
            raise RuntimeError(f"No valid Gemini model found. Available: {available_models}")

    def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        resp = self.client.models.generate_content(model=self.model, contents=prompt)
        return getattr(resp, "text", str(resp))


# ---------------- Prompts ----------------
GENERATION_PROMPT_TEMPLATE = """
You are an assistant that generates quiz questions for learners aged roughly 6-22.
Generate {n_questions} questions for the following parameters:
- Subject: {subject}
- Grade level: {grade}
- Difficulty: {difficulty}
- Extra instructions / context: {description}

Return ONLY a JSON array of questions. Do NOT include any explanations or text outside the array.
Each question must have:
- "type": "mcq" or "enum"
- "text": the question text
- if type == "mcq": "options": list of 4 options
- "answer": the correct answer ("A"/"B"/"C"/"D" for mcq, text for enum)
"""


# ---------------- Helper ----------------
def extract_json(text: str):
    try:
        return json.loads(text)
    except:
        start = text.find('[')
        end = text.rfind(']')
        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end+1])
            except:
                return []
        return []


# ---------------- GUI / App ----------------
class QuizzardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QUIZZARD")
        self.root.geometry("900x640")
        self.root.config(bg="#F7F8FF")

        self.gemini = GeminiClient(model="models/gemini-2.0-flash")

        # UI state
        self.educ_level = tk.StringVar()
        self.course = tk.StringVar()
        self.subject = tk.StringVar()
        self.difficulty = tk.StringVar(value="Easy")
        self.num_questions = tk.IntVar(value=5)

        # Quiz runtime
        self.questions: List[Dict[str, Any]] = []
        self.current_index = 0
        self.score = 0
        self.answer_var = tk.StringVar()
        self.selected_option = tk.StringVar()

        self.build_first_page()

    # ---------- Utility ----------
    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # ---------- First Page ----------
    def build_first_page(self):
        self.clear()
        tk.Label(self.root, text="QUIZZARD", font=("Helvetica", 48, "bold"), bg="#F7F8FF", fg="#323279").pack(pady=80)
        ttk.Button(self.root, text="Generate Quiz", command=self.build_education_screen, width=25).pack(pady=30)

    # ---------- Ask Education Level ----------
    def build_education_screen(self):
        self.clear()
        tk.Label(self.root, text="Select Your Educational Level", font=("Arial", 24, "bold"), bg="#F7F8FF").pack(pady=40)
        levels = [
            "Grade 1","Grade 2","Grade 3","Grade 4","Grade 5","Grade 6",
            "Grade 7","Grade 8","Grade 9","Grade 10",
            "Grade 11","Grade 12",
            "1st Year College","2nd Year College","3rd Year College","4th Year College"
        ]
        self.educ_level.set(levels[0])
        ttk.Combobox(self.root, textvariable=self.educ_level, values=levels, width=25).pack(pady=20)
        ttk.Button(self.root, text="Next", command=self.check_if_college).pack(pady=20)

    # ---------- Check if College Level ----------
    def check_if_college(self):
        level = self.educ_level.get()
        if "College" in level:
            self.build_course_screen()
        else:
            self.build_subject_screen()

    # ---------- College Course Selection ----------
    def build_course_screen(self):
        self.clear()
        tk.Label(self.root, text="Select Your College Course", font=("Arial", 24, "bold"), bg="#F7F8FF").pack(pady=40)
        courses = ["Computer Science", "Engineering", "Business Administration", "Education", "Psychology", "Other"]
        self.course.set(courses[0])
        ttk.Combobox(self.root, textvariable=self.course, values=courses, width=25).pack(pady=20)
        ttk.Button(self.root, text="Next", command=self.build_subject_screen).pack(pady=20)

    # ---------- Subject Selection based on education/course ----------
    def build_subject_screen(self):
        self.clear()
        level = self.educ_level.get()
        subjects = []

        if level in ["Grade 1","Grade 2","Grade 3","Grade 4","Grade 5","Grade 6"]:
            subjects = ["Mathematics","Science","Filipino","English","Arts","PE"]
        elif level in ["Grade 7","Grade 8","Grade 9","Grade 10"]:
            subjects = ["Mathematics","Science","Filipino","English","Social Studies","ICT","Arts","PE"]
        elif level in ["Grade 11","Grade 12"]:
            subjects = ["STEM","ABM","HUMSS","GAS","ICT","Arts","PE"]
        else:  # College
            course = self.course.get()
            if course == "Computer Science":
                subjects = ["Programming","Data Structures","Algorithms","Computer Networks"]
            elif course == "Engineering":
                subjects = ["Engineering Math","Physics","Mechanics","Thermodynamics"]
            elif course == "Business Administration":
                subjects = ["Accounting","Marketing","Finance","Management"]
            elif course == "Education":
                subjects = ["Pedagogy","Curriculum","Child Development","Educational Psychology"]
            elif course == "Psychology":
                subjects = ["Cognitive Psychology","Developmental Psychology","Abnormal Psychology","Research Methods"]
            else:
                subjects = ["General Education 1","General Education 2","General Education 3","General Education 4"]

        tk.Label(self.root, text="Choose Subject", font=("Arial", 24, "bold"), bg="#F7F8FF").pack(pady=30)
        self.subject.set(subjects[0])
        for subj in subjects:
            ttk.Radiobutton(self.root, text=subj, variable=self.subject, value=subj).pack(anchor="w", padx=50)

        # Difficulty and number of questions
        frame = tk.Frame(self.root, bg="#F7F8FF")
        frame.pack(pady=20)
        tk.Label(frame, text="Difficulty:", bg="#F7F8FF").grid(row=0, column=0, padx=6)
        ttk.Combobox(frame, textvariable=self.difficulty, values=["Easy","Medium","Hard"], width=12).grid(row=0, column=1, padx=6)
        tk.Label(frame, text="Number of questions:", bg="#F7F8FF").grid(row=0, column=2, padx=6)
        ttk.Spinbox(frame, from_=3, to=10, textvariable=self.num_questions, width=5).grid(row=0, column=3, padx=6)
        ttk.Button(self.root, text="Generate Quiz", command=self.generate_quiz).pack(pady=20)

    # ---------- Generate Quiz ----------
    def generate_quiz(self):
        self.clear()
        tk.Label(self.root, text="Generating quiz... Please wait.", bg="#F7F8FF", fg="red", font=("Arial",12,"bold")).pack(pady=20)

        def worker():
            prompt = GENERATION_PROMPT_TEMPLATE.format(
                n_questions=self.num_questions.get(),
                subject=self.subject.get(),
                grade=self.educ_level.get(),
                difficulty=self.difficulty.get(),
                description=""
            )
            try:
                response_text = self.gemini.generate(prompt)
                questions = extract_json(response_text)
                if not questions:
                    questions = [{"type":"enum","text":"Error: Could not parse questions from Gemini API.","answer":""}]
            except Exception as e:
                questions = [{"type":"enum","text":f"Error calling Gemini API: {e}","answer":""}]

            self.root.after(0, lambda: self.start_quiz(questions))

        threading.Thread(target=worker, daemon=True).start()

    # ---------- Quiz Flow ----------
    def start_quiz(self, questions: List[Dict[str, Any]]):
        self.questions = questions
        self.current_index = 0
        self.score = 0
        self.show_question()

    def show_question(self):
        self.clear()
        if not self.questions or self.current_index >= len(self.questions):
            self.show_score()
            return

        q = self.questions[self.current_index]
        tk.Label(self.root, text=f"Question {self.current_index+1} of {len(self.questions)}",
                 font=("Arial",14,"bold"), bg="#F7F8FF").pack(pady=10)
        tk.Label(self.root, text=q.get("text",""), font=("Arial",12), bg="#F7F8FF", wraplength=800, justify="left").pack(pady=10)

        if q.get("type") == "mcq":
            self.selected_option.set("")
            for idx, option in enumerate(q["options"]):
                # FIX: Remove double letters in MCQ choices
                clean_option = option
                if len(option) > 2 and option[1] == "." and option[0].isalpha():
                    clean_option = option[2:].strip()
                ttk.Radiobutton(
                    self.root,
                    text=f"{chr(65+idx)}. {clean_option}",
                    variable=self.selected_option,
                    value=chr(65+idx)
                ).pack(anchor="w")
        else:
            self.answer_var.set("")
            self.answer_entry = ttk.Entry(self.root, textvariable=self.answer_var, width=50)
            self.answer_entry.pack(pady=5)
            self.answer_entry.focus()

        ttk.Button(self.root, text="Next", command=self.submit_answer).pack(pady=20)

    def submit_answer(self):
        q = self.questions[self.current_index]
        user_answer = self.selected_option.get() if q.get("type")=="mcq" else self.answer_var.get().strip()
        correct = str(q.get("answer","")).strip()
        if user_answer.upper() == correct.upper():
            self.score += 1
        self.current_index += 1
        self.show_question()

    def show_score(self):
        self.clear()
        tk.Label(self.root, text=f"Quiz Completed!", font=("Helvetica",24,"bold"), bg="#F7F8FF").pack(pady=20)
        tk.Label(self.root, text=f"Your Score: {self.score} / {len(self.questions)}", font=("Arial",18), bg="#F7F8FF").pack(pady=10)
        ttk.Button(self.root, text="Back to Landing Page", command=self.build_first_page).pack(pady=20)


# -------------- RUN --------------
if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TButton", font=("Arial",12), padding=6)
    style.configure("TRadiobutton", font=("Arial",12))
    app = QuizzardApp(root)
    root.mainloop()
