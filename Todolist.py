import customtkinter as ctk
import json
import os
import random

# Set appearance mode and color theme
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class TaskFrame(ctk.CTkFrame):
    def __init__(self, master, task_text, is_completed, update_callback, delete_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.task_text = task_text
        self.is_completed = is_completed
        self.update_callback = update_callback
        self.delete_callback = delete_callback

        # Configure columns so the text can take up most space and the button is on the right
        self.grid_columnconfigure(0, weight=1)
        
        # Label for the task text
        self.task_label = ctk.CTkLabel(
            self, 
            text=task_text, 
            font=ctk.CTkFont(size=14)
        )
        self.task_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")

        # Tick Mark Label
        self.tick_label = ctk.CTkLabel(
            self, 
            text="✔" if self.is_completed else "", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#4CAF50"
        )
        self.tick_label.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="w")

        # Mark as Done / Undo Button
        self.done_button = ctk.CTkButton(
            self,
            text="Mark as Done" if not self.is_completed else "Undo",
            width=100,
            fg_color="#4CAF50" if not self.is_completed else "#FF9800",
            hover_color="#388E3C" if not self.is_completed else "#F57C00",
            command=self.toggle_done,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.done_button.grid(row=0, column=2, padx=(10, 5), pady=10, sticky="e")

        # Delete Task Button
        self.delete_button = ctk.CTkButton(
            self, 
            text="Delete Task", 
            width=80, 
            fg_color="#FF5252", 
            hover_color="#D32F2F", 
            command=self.on_delete,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.delete_button.grid(row=0, column=3, padx=(5, 15), pady=10, sticky="e")

        self._update_text_appearance()

    def _update_text_appearance(self):
        # Change text color as a visual cue of completion.
        if self.is_completed:
            self.task_label.configure(text_color="gray")
            self.done_button.configure(text="Undo", fg_color="#FF9800", hover_color="#F57C00")
            self.tick_label.configure(text="✔")
        else:
            self.task_label.configure(text_color=("black", "white"))
            self.done_button.configure(text="Mark as Done", fg_color="#4CAF50", hover_color="#388E3C")
            self.tick_label.configure(text="")

    def toggle_done(self):
        self.is_completed = not self.is_completed
        self._update_text_appearance()
        self.update_callback(self.task_text, self.is_completed)

    def on_delete(self):
        self.delete_callback(self.task_text, self)

class ToDoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Professional To-Do List")
        self.geometry("500x600")
        self.minsize(400, 500)

        # File to store tasks
        self.data_file = "tasks.json"
        self.tasks = self.load_tasks()

        # Header Title
        self.title_label = ctk.CTkLabel(
            self, 
            text="My Tasks", 
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.title_label.pack(pady=(20, 5))

        # Status Message Label
        self.message_label = ctk.CTkLabel(
            self, 
            text="", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4CAF50"
        )
        self.message_label.pack(pady=(0, 5))

        # Input Frame (Entry + Add Button)
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(pady=10, padx=20, fill="x")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.task_entry = ctk.CTkEntry(
            self.input_frame, 
            placeholder_text="Enter a new task here...",
            font=ctk.CTkFont(size=14),
            height=40
        )
        self.task_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.task_entry.bind("<Return>", lambda event: self.add_task())

        self.add_button = ctk.CTkButton(
            self.input_frame, 
            text="Add New Task", 
            width=120, 
            height=40,
            command=self.add_task,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.add_button.grid(row=0, column=1)

        # Scrollable Frame for Tasks List
        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.task_frames = []
        self.populate_tasks()

        # Motivational Quotes Section
        self.quotes = [
            "“The secret of getting ahead is getting started.” – Mark Twain",
            "“It always seems impossible until it's done.” – Nelson Mandela",
            "“Don’t watch the clock; do what it does. Keep going.” – Sam Levenson",
            "“Quality is not an act, it is a habit.” – Aristotle",
            "“Small deeds done are better than great deeds planned.” – Peter Marshall",
            "“You miss 100% of the shots you don't take.” – Wayne Gretzky",
            "“Believe you can and you're halfway there.” – Theodore Roosevelt",
            "“Success is the sum of small efforts, repeated day-in and day-out.” – Robert Collier"
        ]
        
        self.quote_label = ctk.CTkLabel(
            self, 
            text="", 
            font=ctk.CTkFont(size=16, weight="bold", slant="italic"),
            text_color="gray",
            wraplength=450
        )
        self.quote_label.pack(side="bottom", pady=15, padx=20)
        
        self.update_quote()

    def update_quote(self):
        new_quote = random.choice(self.quotes)
        self.quote_label.configure(text=new_quote)
        self.after(10000, self.update_quote)  # Change quote every 10 seconds

    def load_tasks(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_tasks(self):
        with open(self.data_file, "w") as f:
            json.dump(self.tasks, f)

    def populate_tasks(self):
        for task_text, is_completed in self.tasks.items():
            self.create_task_widget(task_text, is_completed)

    def add_task(self):
        task_text = self.task_entry.get().strip()
        if task_text:
            if task_text in self.tasks:
                self.task_entry.delete(0, 'end')
                return
            
            self.tasks[task_text] = False
            self.save_tasks()
            self.create_task_widget(task_text, False)
            self.task_entry.delete(0, 'end')
            self.message_label.configure(text="New Task added successfully!")
            self.after(3000, lambda: self.message_label.configure(text=""))

    def create_task_widget(self, task_text, is_completed):
        task_frame = TaskFrame(
            self.scrollable_frame, 
            task_text, 
            is_completed, 
            self.update_task_status, 
            self.delete_task
        )
        task_frame.pack(fill="x", pady=5)
        self.task_frames.append(task_frame)

    def update_task_status(self, task_text, is_completed):
        if task_text in self.tasks:
            self.tasks[task_text] = is_completed
            self.save_tasks()

    def delete_task(self, task_text, task_frame):
        if task_text in self.tasks:
            del self.tasks[task_text]
            self.save_tasks()
        
        task_frame.destroy()
        self.task_frames.remove(task_frame)

if __name__ == "__main__":
    app = ToDoApp()
    app.mainloop()
