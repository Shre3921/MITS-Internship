import tkinter as tk
from tkinter import ttk, messagebox
import requests


class CurrencyConverter(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Currency Converter")
        self.geometry("480x320")
        self.configure(bg="#34495e")
        self.minsize(400, 300)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Styling
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TLabel', background='#34495e', foreground='white', font=('Segoe UI', 12))
        style.configure('TEntry', font=('Segoe UI', 12))
        style.configure('TButton',
                        background='#2980b9',
                        foreground='white',
                        font=('Segoe UI', 12, 'bold'),
                        padding=8)
        style.map('TButton',
                  foreground=[('active', 'white')],
                  background=[('active', '#3498db')])

        self.currencies = []
        self.rates = {}

        self.create_widgets()
        self.fetch_currencies()

    def create_widgets(self):
        frame = ttk.Frame(self, padding=20)
        frame.grid(row=0, column=0, sticky="NSEW")

        frame.columnconfigure((0, 1), weight=1, uniform='a')

        title = ttk.Label(frame, text="Currency Converter", font=('Segoe UI', 18, 'bold'))
        title.grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(frame, text="From Currency:").grid(row=1, column=0, sticky='w', padx=5)
        ttk.Label(frame, text="To Currency:").grid(row=1, column=1, sticky='w', padx=5)

        self.from_currency = ttk.Combobox(frame, state='readonly')
        self.from_currency.grid(row=2, column=0, sticky='ew', padx=5, pady=5)

        self.to_currency = ttk.Combobox(frame, state='readonly')
        self.to_currency.grid(row=2, column=1, sticky='ew', padx=5, pady=5)

        ttk.Label(frame, text="Amount:").grid(row=3, column=0, columnspan=2, sticky='w', padx=5)
        self.amount_entry = ttk.Entry(frame)
        self.amount_entry.grid(row=4, column=0, columnspan=2, sticky='ew', padx=5, pady=5)

        self.convert_btn = ttk.Button(frame, text="Convert", command=self.convert_currency)
        self.convert_btn.grid(row=5, column=0, columnspan=2, sticky='ew', padx=5, pady=10)

        self.result_label = ttk.Label(frame, text="", font=('Segoe UI', 14, 'bold'), foreground='#2ecc71')
        self.result_label.grid(row=6, column=0, columnspan=2, pady=5)

    def fetch_currencies(self):
        self.convert_btn.config(state='disabled')
        self.result_label.config(text="Loading currencies...")
        self.update_idletasks()

        try:
            response = requests.get("https://open.er-api.com/v6/latest/USD", timeout=5)
            data = response.json()

            if data['result'] == 'success':
                self.rates = data['rates']
                self.currencies = sorted(self.rates.keys())
                self.from_currency['values'] = self.currencies
                self.to_currency['values'] = self.currencies

                self.from_currency.set("USD")
                self.to_currency.set("INR")

                self.result_label.config(text="Select currencies and enter amount.")
            else:
                messagebox.showerror("API Error", "Failed to load currency data.")
        except requests.exceptions.RequestException:
            messagebox.showerror("Network Error", "Unable to connect to the currency API.")
        finally:
            self.convert_btn.config(state='normal')

    def convert_currency(self):
        from_cur = self.from_currency.get()
        to_cur = self.to_currency.get()
        amount_str = self.amount_entry.get().strip()

        if not from_cur or not to_cur:
            messagebox.showwarning("Input Error", "Please select both currencies.")
            return

        try:
            amount = float(amount_str)
            if amount < 0:
                raise ValueError("Negative amount")
        except ValueError:
            messagebox.showwarning("Input Error", "Enter a valid positive number.")
            return

        try:
            usd_amount = amount / self.rates[from_cur] if from_cur != "USD" else amount
            converted = usd_amount * self.rates[to_cur]
            self.result_label.config(text=f"{amount:.2f} {from_cur} = {converted:.2f} {to_cur}")
        except Exception as e:
            messagebox.showerror("Conversion Error", f"Failed to convert currency.\n{e}")


if __name__ == "__main__":
    app = CurrencyConverter()
    app.mainloop()
