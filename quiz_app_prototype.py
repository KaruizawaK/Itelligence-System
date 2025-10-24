import tkinter as tk
from tkinter import ttk
import random

# ---------------- QUIZ DATA ----------------
QUIZ_DATA = {
    "easy": [
        {"text": "What is the capital of France?",
         "options": {"A": "London", "B": "Berlin", "C": "Paris", "D": "Madrid"}, "correct": "C"},
        {"text": "Which number is even?",
         "options": {"A": "3", "B": "7", "C": "4", "D": "9"}, "correct": "C"},
        {"text": "What color do you get when you mix red and white?",
         "options": {"A": "Pink", "B": "Blue", "C": "Orange", "D": "Purple"}, "correct": "A"},
        {"text": "Which planet is closest to the Sun?",
         "options": {"A": "Venus", "B": "Mercury", "C": "Earth", "D": "Mars"}, "correct": "B"},
        {"text": "Which animal says 'meow'?",
         "options": {"A": "Dog", "B": "Cat", "C": "Bird", "D": "Cow"}, "correct": "B"},
    ],
    "medium": [
        {"text": "Who painted the Mona Lisa?",
         "options": {"A": "Vincent van Gogh", "B": "Leonardo da Vinci", "C": "Pablo Picasso", "D": "Michelangelo"}, "correct": "B"},
        {"text": "What is the chemical symbol for gold?",
         "options": {"A": "Ag", "B": "Au", "C": "Gd", "D": "Go"}, "correct": "B"},
        {"text": "How many continents are there on Earth?",
         "options": {"A": "5", "B": "6", "C": "7", "D": "8"}, "correct": "C"},
        {"text": "What gas do plants absorb during photosynthesis?",
         "options": {"A": "Oxygen", "B": "Hydrogen", "C": "Carbon Dioxide", "D": "Nitrogen"}, "correct": "C"},
        {"text": "What is the largest mammal on Earth?",
         "options": {"A": "Elephant", "B": "Blue Whale", "C": "Giraffe", "D": "Great White Shark"}, "correct": "B"},
    ],
    "hard": [
        {"text": "What is the square root of 144?",
         "options": {"A": "12", "B": "11", "C": "13", "D": "14"}, "correct": "A"},
        {"text": "Who proposed the theory of general relativity?",
         "options": {"A": "Isaac Newton", "B": "Albert Einstein", "C": "Nikola Tesla", "D": "Stephen Hawking"}, "correct": "B"},
        {"text": "What is the hardest natural substance on Earth?",
         "options": {"A": "Diamond", "B": "Steel", "C": "Titanium", "D": "Graphene"}, "correct": "A"},
        {"text": "Which planet has the most moons?",
         "options": {"A": "Earth", "B": "Jupiter", "C": "Saturn", "D": "Neptune"}, "correct": "C"},
        {"text": "What year did World War II end?",
         "options": {"A": "1942", "B": "1945", "C": "1950", "D": "1939"}, "correct": "B"},
    ],
}

# ---------------- GUI CLASS ----------------
class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Quiz Master 🧠")
        self.root.geometry("700x500")
        self.root.config(bg="#E3E7FF")

        self.difficulty = tk.StringVar(value="easy")
        self.questions = []
        self.current_q = 0
        self.score = 0
        self.selected = tk.StringVar()
        self.feedback_label = None

        self.create_start_screen()

    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    # ---------- START SCREEN ----------
    def create_start_screen(self):
        self.clear()
        tk.Label(self.root, text="🎯 AI Quiz Master", font=("Comic Sans MS", 28, "bold"),
                 bg="#E3E7FF", fg="#2B2D42").pack(pady=30)
        tk.Label(self.root, text="Choose your difficulty level:", font=("Arial", 14),
                 bg="#E3E7FF").pack(pady=10)

        frame = tk.Frame(self.root, bg="#E3E7FF")
        frame.pack()
        for diff in ["easy", "medium", "hard"]:
            ttk.Radiobutton(frame, text=diff.capitalize(),
                            variable=self.difficulty, value=diff).pack(side="left", padx=20)

        ttk.Button(self.root, text="🚀 Start Quiz", command=self.start_quiz).pack(pady=40)

    # ---------- START QUIZ ----------
    def start_quiz(self):
        self.questions = random.sample(QUIZ_DATA[self.difficulty.get()], 5)
        self.score = 0
        self.current_q = 0
        self.show_question()

    # ---------- SHOW QUESTION ----------
    def show_question(self):
        self.clear()
        q = self.questions[self.current_q]

        card = tk.Frame(self.root, bg="#FFFFFF", relief="ridge", bd=4)
        card.place(relx=0.5, rely=0.5, anchor="center", width=550, height=330)

        tk.Label(card, text=f"Question {self.current_q + 1} / {len(self.questions)}",
                 font=("Arial", 12, "italic"), bg="#FFFFFF", fg="#6C63FF").pack(pady=5)
        tk.Label(card, text=q["text"], wraplength=500, font=("Arial", 14, "bold"),
                 bg="#FFFFFF", fg="#2B2D42").pack(pady=10)

        self.selected.set("")
        for key, val in q["options"].items():
            ttk.Radiobutton(card, text=f"{key}. {val}", variable=self.selected, value=key).pack(anchor="w", padx=50, pady=3)

        ttk.Button(card, text="Submit", command=self.check_answer).pack(pady=10)
        self.feedback_label = tk.Label(card, text="", font=("Arial", 12), bg="#FFFFFF")
        self.feedback_label.pack(pady=5)

    # ---------- CHECK ANSWER ----------
    def check_answer(self):
        q = self.questions[self.current_q]
        if self.selected.get() == "":
            self.feedback_label.config(text="⚠️ Please select an answer.", fg="orange")
            return

        if self.selected.get() == q["correct"]:
            self.score += 1
            self.feedback_label.config(text="✅ Correct!", fg="green")
        else:
            correct_opt = q["options"][q["correct"]]
            self.feedback_label.config(text=f"❌ Incorrect! Correct answer: {correct_opt}", fg="red")

        # Disable buttons after answer
        self.root.after(1000, self.next_question)

    # ---------- NEXT QUESTION ----------
    def next_question(self):
        self.current_q += 1
        if self.current_q < len(self.questions):
            self.show_question()
        else:
            self.show_result()

    # ---------- RESULT SCREEN ----------
    def show_result(self):
        self.clear()
        tk.Label(self.root, text="🏁 Quiz Complete!", font=("Comic Sans MS", 26, "bold"),
                 bg="#E3E7FF", fg="#2B2D42").pack(pady=30)
        tk.Label(self.root, text=f"Your Score: {self.score}/{len(self.questions)}",
                 font=("Arial", 18), bg="#E3E7FF", fg="#2B2D42").pack(pady=10)

        if self.score == len(self.questions):
            msg = "🌟 Perfect score! You're a genius!"
        elif self.score >= 3:
            msg = "👏 Great job! You're doing awesome!"
        else:
            msg = "💪 Keep practicing! You got this next time!"

        tk.Label(self.root, text=msg, font=("Arial", 14), bg="#E3E7FF").pack(pady=10)
        ttk.Button(self.root, text="🔁 Play Again", command=self.create_start_screen).pack(pady=10)
        ttk.Button(self.root, text="Exit 🚪", command=self.root.quit).pack()


# ---------- RUN APP ----------
if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TButton", font=("Arial", 12), padding=6)
    style.configure("TRadiobutton", font=("Arial", 12))
    app = QuizApp(root)
    root.mainloop()
