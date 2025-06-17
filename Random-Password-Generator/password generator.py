import secrets
import string
import math
import tkinter as tk
from tkinter import ttk, messagebox

SIMILAR_CHARS = set('il1Lo0O')

def get_entropy(charset_length: int, password_length: int) -> float:
    if charset_length == 0:
        return 0.0
    return round(math.log2(charset_length) * password_length, 1)

def strength_classification(entropy_bits: float) -> str:
    if entropy_bits < 28:
        return "Very Weak"
    elif entropy_bits < 36:
        return "Weak"
    elif entropy_bits < 60:
        return "Moderate"
    elif entropy_bits < 128:
        return "Strong"
    else:
        return "Very Strong"

class ResponsivePasswordGenerator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Responsive Password Generator")
        self.configure(bg="#121212")
        self.minsize(400, 400)
        self.create_styles()
        self.create_widgets()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)  # Results expands

    def create_styles(self):
        style = ttk.Style(self)
        style.theme_use('clam')

        style.configure('TFrame', background='#121212')
        style.configure('Card.TFrame', background='#1f2937', relief='raised', borderwidth=1)
        style.configure('TLabel', background='#121212', foreground='#e0e0e0', font=('Segoe UI', 11))
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'))
        style.configure('Strength.TLabel', font=('Segoe UI', 10, 'italic'), foreground='#94a3b8')
        style.configure('TButton',
                        background='#2563eb', foreground='white', font=('Segoe UI', 12, 'bold'),
                        padding=8)
        style.map('TButton',
                  background=[('active', '#1e40af'), ('disabled', "#f84b3b")])
        style.configure('TCheckbutton', background='#121212', foreground="#eae0e0", font=('Segoe UI', 11))

    def create_widgets(self):
        # Header
        header = ttk.Label(self, text="Responsive Password Generator", style='Title.TLabel')
        header.grid(row=0, column=0, padx=20, pady=(16,8), sticky='W')

        # Form Frame
        form_frame = ttk.Frame(self, style='TFrame')
        form_frame.grid(row=1, column=0, padx=20, sticky='EW')
        form_frame.grid_columnconfigure(1, weight=1)

        # Password length
        ttk.Label(form_frame, text="Password Length (6-128):").grid(row=0, column=0, sticky='W', pady=6)
        self.length_var = tk.IntVar(value=16)
        self.length_spin = ttk.Spinbox(form_frame, from_=6, to=128, width=5, textvariable=self.length_var,
                                       font=('Segoe UI', 11))
        self.length_spin.grid(row=0, column=1, sticky='W', pady=6, padx=(8,0))

        # Number of passwords
        ttk.Label(form_frame, text="Number of Passwords (1-10):").grid(row=1, column=0, sticky='W', pady=6)
        self.quantity_var = tk.IntVar(value=3)
        self.quantity_spin = ttk.Spinbox(form_frame, from_=1, to=10, width=5, textvariable=self.quantity_var,
                                         font=('Segoe UI', 11))
        self.quantity_spin.grid(row=1, column=1, sticky='W', pady=6, padx=(8,0))

        # Checkboxes Frame
        check_frame = ttk.LabelFrame(self, text="Include Characters", style='TFrame')
        check_frame.grid(row=2, column=0, padx=20, pady=16, sticky='EW')
        check_frame.grid_columnconfigure((0,1), weight=1)

        self.include_upper = tk.BooleanVar(value=True)
        self.include_lower = tk.BooleanVar(value=True)
        self.include_digits = tk.BooleanVar(value=True)
        self.include_symbols = tk.BooleanVar(value=True)
        self.exclude_similar = tk.BooleanVar(value=False)

        ttk.Checkbutton(check_frame, text="Uppercase (A-Z)", variable=self.include_upper, style='TCheckbutton').grid(row=0, column=0, sticky='W', padx=8, pady=4)
        ttk.Checkbutton(check_frame, text="Lowercase (a-z)", variable=self.include_lower, style='TCheckbutton').grid(row=1, column=0, sticky='W', padx=8, pady=4)
        ttk.Checkbutton(check_frame, text="Numbers (0-9)", variable=self.include_digits, style='TCheckbutton').grid(row=0, column=1, sticky='W', padx=8, pady=4)
        ttk.Checkbutton(check_frame, text="Symbols (!@#$...)", variable=self.include_symbols, style='TCheckbutton').grid(row=1, column=1, sticky='W', padx=8, pady=4)
        ttk.Checkbutton(check_frame, text="Exclude Similar (i, l, 1, L, o, 0, O)", variable=self.exclude_similar, style='TCheckbutton').grid(row=2, column=0, columnspan=2, sticky='W', padx=8, pady=6)

        # Generate Button
        self.generate_btn = ttk.Button(self, text="Generate Passwords", command=self.generate_passwords)
        self.generate_btn.grid(row=3, column=0, pady=10, padx=20, sticky='EW')

        # Results Frame with Scrollable Canvas
        self.results_frame = ttk.Frame(self, style='Card.TFrame')
        self.results_frame.grid(row=4, column=0, padx=20, pady=(0,20), sticky='NSEW')
        self.rowconfigure(4, weight=1)
        self.results_frame.rowconfigure(0, weight=1)
        self.results_frame.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self.results_frame, bg="#1f2937", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky='NSEW')
        self.scrollbar = ttk.Scrollbar(self.results_frame, orient='vertical', command=self.canvas.yview)
        self.scrollbar.grid(row=0, column=1, sticky='NS')
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Frame inside canvas
        self.inner_frame = ttk.Frame(self.canvas, style='Card.TFrame')
        self.canvas.create_window((0,0), window=self.inner_frame, anchor='nw')

        # Bind configure event to update scrollregion
        self.inner_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    def build_charset(self):
        charset = ''
        if self.include_upper.get():
            charset += string.ascii_uppercase
        if self.include_lower.get():
            charset += string.ascii_lowercase
        if self.include_digits.get():
            charset += string.digits
        if self.include_symbols.get():
            charset += "!@#$%^&*()-_=+[]{}|;:,.<>?/~`"
        if self.exclude_similar.get():
            charset = ''.join(ch for ch in charset if ch not in SIMILAR_CHARS)
        return charset

    def generate_single_password(self, length, charset):
        return ''.join(secrets.choice(charset) for _ in range(length)) if charset else ''

    def clear_results(self):
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

    def copy_to_clipboard(self, pwd):
        self.clipboard_clear()
        self.clipboard_append(pwd)
        messagebox.showinfo("Copied!", "Password copied to clipboard!")

    def generate_passwords(self):
        length = self.length_var.get()
        quantity = self.quantity_var.get()

        if not (6 <= length <= 128):
            messagebox.showerror("Invalid Input", "Password length must be between 6 and 128.")
            return

        if not (1 <= quantity <= 10):
            messagebox.showerror("Invalid Input", "Number of passwords must be between 1 and 10.")
            return

        charset = self.build_charset()

        if not charset:
            messagebox.showerror("Invalid Input", "Select at least one character set.")
            return

        self.clear_results()

        for i in range(quantity):
            pwd = self.generate_single_password(length, charset)
            entropy = get_entropy(len(charset), length)
            strength = strength_classification(entropy)

            frame = ttk.Frame(self.inner_frame, style='Card.TFrame', padding=8)
            frame.pack(fill='x', pady=6)

            pwd_label = ttk.Label(frame, text=pwd, font=('Consolas', 14), foreground='#e0e0e0', background='#1f2937')
            pwd_label.pack(side='left', fill='x', expand=True)

            info_label = ttk.Label(frame, text=f"Entropy: {entropy} bits | {strength}", font=('Segoe UI', 10, 'italic'), foreground='#94a3b8', background='#1f2937')
            info_label.pack(side='left', padx=10)

            copy_btn = ttk.Button(frame, text="Copy", command=lambda p=pwd: self.copy_to_clipboard(p))
            copy_btn.pack(side='right')

if __name__ == '__main__':
    app = ResponsivePasswordGenerator()
    app.mainloop()
