import customtkinter as ctk
import math
import re
import json
import os

# Set appearance mode and color theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

def safe_eval(expr):
    expr = expr.strip()
    if not expr:
        return ""
    
    # Replace '^' with '**'
    expr = expr.replace('^', '**')
    
    # Replace number% with (number/100)
    expr = re.sub(r'(\d+(\.\d+)?)%', r'(\1/100)', expr)
    
    replacements = {
        'sin': 'math.sin',
        'cos': 'math.cos',
        'tan': 'math.tan',
        'log': 'math.log10',
        'ln': 'math.log',
        'sqrt': 'math.sqrt',
        'pi': 'math.pi',
        'e': 'math.e',
    }
    
    allowed_words = set(replacements.keys())
    
    # Validate words to avoid arbitrary code execution
    words = re.findall(r'[a-zA-Z]+', expr)
    for word in words:
        if word not in allowed_words:
            raise ValueError(f"Unauthorized word: {word}")
            
    # Do replacements
    for user_fn, math_fn in replacements.items():
        expr = re.sub(r'\b' + user_fn + r'\b', math_fn, expr)
        
    context = {
        'math': math,
        '__builtins__': None
    }
    
    return eval(expr, context, {})

def format_result(val):
    if isinstance(val, (int, float)):
        if isinstance(val, float) and val.is_integer():
            return str(int(val))
        if isinstance(val, float):
            res = round(val, 10)
            if res.is_integer():
                return str(int(res))
            return str(res)
    return str(val)

class CalculatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Advanced Calculator")
        self.geometry("360x550")
        self.resizable(True, False)
        self.minsize(360, 550)
        
        # State variables
        self.expression = ""
        self.result_shown = False
        self.sci_visible = False
        self.history_visible = False
        self.history_file = "calculator_history.json"
        self.history = self.load_history()
        
        # Grid layout configuration for main window
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0) # Sci panel
        self.grid_columnconfigure(1, weight=1) # Main calculator
        self.grid_columnconfigure(2, weight=0) # History panel
        
        # Setup panels
        self.setup_main_panel()
        self.setup_sci_panel()
        self.setup_history_panel()
        
        # Populate history
        self.populate_history_view()
        
        # Keyboard binds
        self.bind_keys()
        
    def setup_main_panel(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # Header
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 5))
        
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="Calculator", 
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
        )
        self.title_label.pack(side="left", padx=5)
        
        self.theme_btn = ctk.CTkButton(
            self.header_frame,
            text="☀️/🌙",
            width=40,
            height=30,
            fg_color=("#E5E7EB", "#374151"),
            hover_color=("#D1D5DB", "#4B5563"),
            text_color=("#111827", "#F9FAFB"),
            command=self.toggle_theme,
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.theme_btn.pack(side="right", padx=5)
        
        self.hist_btn = ctk.CTkButton(
            self.header_frame, 
            text="📜 History", 
            width=80, 
            height=30,
            fg_color=("#E5E7EB", "#374151"),
            hover_color=("#D1D5DB", "#4B5563"),
            text_color=("#111827", "#F9FAFB"),
            command=self.toggle_history_panel,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        )
        self.hist_btn.pack(side="right", padx=5)
        
        # Display Screen Frame
        self.display_frame = ctk.CTkFrame(self.main_frame, fg_color=("#F3F4F6", "#1F2937"), corner_radius=10)
        self.display_frame.pack(fill="x", pady=5)
        
        self.expr_label = ctk.CTkLabel(
            self.display_frame, 
            text="", 
            font=ctk.CTkFont(family="Segoe UI", size=14), 
            text_color="gray", 
            anchor="e"
        )
        self.expr_label.pack(fill="x", padx=15, pady=(10, 0))
        
        self.result_label = ctk.CTkLabel(
            self.display_frame, 
            text="0", 
            font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"), 
            text_color=("#111827", "#F9FAFB"), 
            anchor="e"
        )
        self.result_label.pack(fill="x", padx=15, pady=(0, 10))
        
        # Keypad
        self.keypad_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.keypad_frame.pack(fill="both", expand=True, pady=(5, 0))
        
        for r in range(5):
            self.keypad_frame.grid_rowconfigure(r, weight=1)
        for c in range(4):
            self.keypad_frame.grid_columnconfigure(c, weight=1)
            
        buttons = [
            ('AC', 0, 0), ('⌫', 0, 1), ('%', 0, 2), ('/', 0, 3),
            ('7',  1, 0), ('8',  1, 1), ('9',  1, 2), ('*',  1, 3),
            ('4',  2, 0), ('5',  2, 1), ('6',  2, 2), ('-',  2, 3),
            ('1',  3, 0), ('2',  3, 1), ('3',  3, 2), ('+',  3, 3),
            ('Sci',4, 0), ('0',  4, 1), ('.',  4, 2), ('=',  4, 3)
        ]
        
        for text, r, c in buttons:
            if text == 'AC':
                fg = ("#EF4444", "#DC2626")
                hover = ("#DC2626", "#B91C1C")
                text_col = "#FFFFFF"
                cmd = self.clear_all
            elif text == '⌫':
                fg = ("#D1D5DB", "#4B5563")
                hover = ("#9CA3AF", "#374151")
                text_col = ("#000000", "#FFFFFF")
                cmd = self.backspace
            elif text in ['/', '*', '-', '+', '=']:
                display_text = text
                if text == '/': display_text = '÷'
                if text == '*': display_text = '×'
                
                fg = ("#FF9500", "#FF9F0A")
                hover = ("#E68600", "#CC7F00")
                text_col = "#FFFFFF"
                
                if text == '=':
                    cmd = self.calculate_result
                else:
                    cmd = lambda dt=display_text: self.append_to_expression(dt)
            elif text == 'Sci':
                fg = ("#D1D5DB", "#4B5563")
                hover = ("#9CA3AF", "#374151")
                text_col = ("#000000", "#FFFFFF")
                cmd = self.toggle_sci_panel
            else:
                fg = ("#F9FAFB", "#1F2937")
                hover = ("#F3F4F6", "#111827")
                text_col = ("#111827", "#F9FAFB")
                cmd = lambda t=text: self.append_to_expression(t)
                
            btn = self.create_button(
                self.keypad_frame,
                text=text,
                row=r,
                col=c,
                command=cmd,
                fg_color=fg,
                hover_color=hover,
                text_color=text_col
            )
            
            if text == 'Sci':
                self.sci_btn = btn
                
    def setup_sci_panel(self):
        self.sci_frame = ctk.CTkFrame(self, width=150, corner_radius=0, fg_color=("#F3F4F6", "#1F2937"))
        
        for r in range(4):
            self.sci_frame.grid_rowconfigure(r, weight=1)
        for c in range(3):
            self.sci_frame.grid_columnconfigure(c, weight=1)
            
        sci_buttons = [
            ('sin', 0, 0), ('cos', 0, 1), ('tan', 0, 2),
            ('log', 1, 0), ('ln', 1, 1), ('sqrt', 1, 2),
            ('(', 2, 0), (')', 2, 1), ('^', 2, 2),
            ('π', 3, 0), ('e', 3, 1), ('+/-', 3, 2)
        ]
        
        for text, r, c in sci_buttons:
            if text == '+/-':
                cmd = self.toggle_sign
            elif text in ['sin', 'cos', 'tan', 'log', 'ln', 'sqrt']:
                cmd = lambda t=text: self.append_to_expression(t + "(")
            elif text == 'π':
                cmd = lambda: self.append_to_expression("π")
            else:
                cmd = lambda t=text: self.append_to_expression(t)
                
            self.create_button(
                self.sci_frame,
                text=text,
                row=r,
                col=c,
                command=cmd,
                fg_color=("#E5E7EB", "#2D3748"),
                hover_color=("#D1D5DB", "#1A202C"),
                text_color=("#111827", "#F9FAFB")
            )
            
    def setup_history_panel(self):
        self.history_frame = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=("#F3F4F6", "#1F2937"))
        
        self.history_header = ctk.CTkFrame(self.history_frame, fg_color="transparent")
        self.history_header.pack(fill="x", padx=10, pady=10)
        
        self.history_title = ctk.CTkLabel(
            self.history_header, 
            text="History", 
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        )
        self.history_title.pack(side="left")
        
        self.clear_hist_btn = ctk.CTkButton(
            self.history_header,
            text="Clear",
            width=50,
            height=25,
            fg_color=("#EF4444", "#DC2626"),
            hover_color=("#DC2626", "#B91C1C"),
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self.clear_history
        )
        self.clear_hist_btn.pack(side="right")
        
        self.history_scroll = ctk.CTkScrollableFrame(self.history_frame, fg_color="transparent")
        self.history_scroll.pack(fill="both", expand=True, padx=5, pady=(0, 10))

    def create_button(self, parent, text, row, col, command, fg_color, hover_color, text_color):
        btn = ctk.CTkButton(
            parent,
            text=text,
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            fg_color=fg_color,
            hover_color=hover_color,
            text_color=text_color,
            corner_radius=8,
            command=command
        )
        btn.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")
        return btn

    def toggle_sci_panel(self):
        self.sci_visible = not self.sci_visible
        if self.sci_visible:
            self.sci_frame.grid(row=0, column=0, sticky="nsew", padx=(5, 0), pady=5)
            self.sci_btn.configure(fg_color=("#FF9500", "#FF9F0A"), text_color="#FFFFFF")
        else:
            self.sci_frame.grid_forget()
            self.sci_btn.configure(fg_color=("#D1D5DB", "#4B5563"), text_color=("#000000", "#FFFFFF"))
        self.update_window_size()
        
    def toggle_history_panel(self):
        self.history_visible = not self.history_visible
        if self.history_visible:
            self.history_frame.grid(row=0, column=2, sticky="nsew", padx=(0, 5), pady=5)
            self.hist_btn.configure(fg_color=("#FF9500", "#FF9F0A"), text_color="#FFFFFF")
        else:
            self.history_frame.grid_forget()
            self.hist_btn.configure(fg_color=("#E5E7EB", "#374151"), text_color=("#111827", "#F9FAFB"))
        self.update_window_size()
        
    def update_window_size(self):
        width = 360
        if self.sci_visible:
            width += 150
        if self.history_visible:
            width += 200
        self.geometry(f"{width}x550")

    def toggle_theme(self):
        current_mode = ctk.get_appearance_mode()
        if current_mode == "Dark":
            ctk.set_appearance_mode("Light")
        else:
            ctk.set_appearance_mode("Dark")
            
    def append_to_expression(self, char):
        if self.result_shown:
            prev_res = self.result_label.cget("text")
            if char in ["+", "-", "×", "÷", "^"] and prev_res != "Error":
                self.expression = prev_res
            else:
                self.expression = ""
            self.result_shown = False
            
        self.expression += char
        self.update_display()
        
    def clear_all(self):
        self.expression = ""
        self.result_shown = False
        self.update_display()
        
    def backspace(self):
        if self.result_shown:
            self.expression = ""
            self.result_shown = False
        else:
            deleted = False
            for fn in ["sin(", "cos(", "tan(", "log(", "ln(", "sqrt("]:
                if self.expression.endswith(fn):
                    self.expression = self.expression[:-len(fn)]
                    deleted = True
                    break
            if not deleted:
                self.expression = self.expression[:-1]
        self.update_display()
        
    def toggle_sign(self):
        expr = self.expression
        if not expr:
            return
        if expr.startswith("-(") and expr.endswith(")"):
            self.expression = expr[2:-1]
        else:
            self.expression = f"-({expr})"
        self.update_display()
        
    def get_eval_expression(self):
        expr = self.expression
        expr = expr.replace('×', '*')
        expr = expr.replace('÷', '/')
        expr = expr.replace('π', 'pi')
        return expr

    def update_display(self):
        self.expr_label.configure(text=self.expression)
        if not self.expression:
            self.result_label.configure(text="0")
        else:
            if not self.result_shown:
                try:
                    eval_expr = self.get_eval_expression()
                    res = safe_eval(eval_expr)
                    self.result_label.configure(text=format_result(res))
                except Exception:
                    pass

    def calculate_result(self):
        if not self.expression:
            return
            
        try:
            eval_expr = self.get_eval_expression()
            res = safe_eval(eval_expr)
            result_str = format_result(res)
            
            # Save to history list
            self.history.append({
                "expr": self.expression,
                "res": result_str
            })
            self.save_history()
            self.populate_history_view()
            
            self.result_label.configure(text=result_str)
            self.result_shown = True
        except Exception:
            self.result_label.configure(text="Error")
            self.result_shown = True

    def load_expr_from_history(self, expr):
        self.expression = expr
        self.result_shown = False
        self.update_display()

    def populate_history_view(self):
        for child in self.history_scroll.winfo_children():
            child.destroy()
            
        if not self.history:
            lbl = ctk.CTkLabel(
                self.history_scroll, 
                text="No history yet", 
                font=ctk.CTkFont(family="Segoe UI", size=12), 
                text_color="gray"
            )
            lbl.pack(pady=20)
            return
            
        for item in reversed(self.history):
            expr = item["expr"]
            res = item["res"]
            btn = ctk.CTkButton(
                self.history_scroll,
                text=f"{expr}\n= {res}",
                anchor="w",
                font=ctk.CTkFont(family="Segoe UI", size=12),
                fg_color="transparent",
                text_color=("#333333", "#CCCCCC"),
                hover_color=("#E5E7EB", "#374151"),
                height=50,
                command=lambda e=expr: self.load_expr_from_history(e)
            )
            btn.pack(fill="x", pady=2, padx=5)

    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save_history(self):
        try:
            with open(self.history_file, "w") as f:
                json.dump(self.history, f)
        except Exception as e:
            print(f"Error saving history: {e}")

    def clear_history(self):
        self.history = []
        self.save_history()
        self.populate_history_view()

    def bind_keys(self):
        self.bind("<Key>", self.on_key_press)
        
    def on_key_press(self, event):
        char = event.char
        keysym = event.keysym
        
        if char in "0123456789.+-()%":
            self.append_to_expression(char)
        elif char == "*":
            self.append_to_expression("×")
        elif char == "/":
            self.append_to_expression("÷")
        elif char == "^":
            self.append_to_expression("^")
        elif keysym == "Return" or char == "=":
            self.calculate_result()
        elif keysym == "BackSpace":
            self.backspace()
        elif keysym == "Escape":
            self.clear_all()

if __name__ == "__main__":
    app = CalculatorApp()
    app.mainloop()
