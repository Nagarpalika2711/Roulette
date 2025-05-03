import tkinter as tk
from tkinter import simpledialog, messagebox
import random

class NonBlockingAlert(tk.Toplevel):
    def __init__(self, master, title, message, bet_entries=None):
        super().__init__(master)
        self.title(title)
        self.geometry("370x320")
        self.resizable(False, False)
        self.label = tk.Label(self, text=message, wraplength=340, font=("Arial", 12))
        self.label.pack(pady=10)
        if bet_entries:
            tk.Label(self, text="Bets:", font=("Arial", 12, "bold")).pack()
            for text, color in bet_entries:
                tk.Label(self, text=text, fg=color, font=("Arial", 11)).pack(anchor="w", padx=20)
        self.button = tk.Button(self, text="OK", command=self.destroy, font=("Arial", 12, "bold"))
        self.button.pack(pady=10)
        self.protocol("WM_DELETE_WINDOW", self.destroy)

# Global game state
player_name = "Player"
balance = 0
total_wins = 0
Current_Number = -1
Previous_Number = -2
BetBucket = {}
redlist = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
interval_bets = {'1-12': (1,12), '13-24': (13,24), '25-36': (25,36)}
odd_even_bet = None
red_black_bet = None
timer_seconds = 60

def initialize_player():
    global player_name, balance
    root = tk.Tk()
    root.withdraw()
    player_name = simpledialog.askstring("Player Info", "Enter your name:") or "Player"
    while True:
        amount = simpledialog.askstring("Initial Balance", "Enter starting balance:")
        try:
            balance = float(amount)
            if balance <= 0: raise ValueError
            break
        except:
            messagebox.showerror("Error", "Invalid amount. Enter a positive number.")
    root.destroy()

def update_balance(amount):
    global balance
    balance += amount
    balance_label.config(text=f"Balance: ${balance:.2f}", fg="white")

def add_balance():
    while True:
        amount = simpledialog.askstring("Add Funds", "Enter amount to add:")
        try:
            funds = float(amount)
            if funds <= 0: raise ValueError
            update_balance(funds)
            break
        except:
            messagebox.showerror("Error", "Invalid amount. Enter a positive number.")

def get_color(number):
    if number == 0: return 'green'
    return 'red' if number in redlist else 'black'

def get_odd_even(number):
    if number == 0: return 'none'
    return 'even' if number % 2 == 0 else 'odd'

def calculate_wins():
    global Current_Number, total_wins
    wins = 0
    color = get_color(Current_Number)
    parity = get_odd_even(Current_Number)
    for bet_key, amount in BetBucket.items():
        if isinstance(bet_key, int):
            if bet_key == Current_Number:
                wins += amount * 36
        elif bet_key == color:
            wins += amount * 2
        elif bet_key == parity:
            wins += amount * 2
        elif bet_key in interval_bets:
            start, end = interval_bets[bet_key]
            if start <= Current_Number <= end:
                wins += amount * 3
    total_wins += wins
    total_wins_label.config(text=f"Total Wins: ${total_wins:.2f}")
    return wins

def generate_new_number():
    global Current_Number, BetBucket
    new_number = random.randint(0, 36)
    while new_number == Current_Number:
        new_number = random.randint(0, 36)
    Current_Number = new_number
    current_number_display.config(text=f"Current Number: {Current_Number}")
    winnings = calculate_wins()
    color = get_color(Current_Number)
    parity = get_odd_even(Current_Number)
    result_msg = f"Number: {Current_Number}\nColor: {color.capitalize()}\n"
    result_msg += f"Odd/Even: {parity.capitalize() if parity != 'none' else 'None'}\n"
    result_msg += f"Winnings: ${winnings:.2f}" if winnings > 0 else "No winnings"

    # Generate bet list with color information
    bet_entries = []
    for bet_key, amount in BetBucket.items():
        win = False
        if isinstance(bet_key, int):
            win = (bet_key == Current_Number)
        elif bet_key == color:
            win = True
        elif bet_key == parity:
            win = True
        elif bet_key in interval_bets:
            start, end = interval_bets[bet_key]
            win = (start <= Current_Number <= end)
        bet_text = f"{bet_key}: ${amount}"
        bet_entries.append((bet_text, "green" if win else "red"))

    NonBlockingAlert(window, "Round Results", result_msg, bet_entries=bet_entries)

    if winnings > 0:
        update_balance(winnings)
    BetBucket.clear()
    for number in bet_amount_labels:
        bet_amount_labels[number].config(text="0")
    for label in [*special_labels.values()]:
        label.config(text="$0")
    for label in interval_amount_labels.values():
        label.config(text="$0")
    if balance <= 0:
        NonBlockingAlert(window, "Empty Balance", "Please add funds to continue")
        add_balance()

def update_timer():
    global timer_seconds
    if timer_seconds > 0:
        timer_seconds -= 1
        timer_label.config(text=str(timer_seconds))
        window.after(1000, update_timer)
    else:
        generate_new_number()
        timer_seconds = 60
        timer_label.config(text=str(timer_seconds))
        window.after(1000, update_timer)

# Drag and drop system
current_dragged_coin_value = None
floating_label = None

def start_drag(event, value):
    global current_dragged_coin_value, floating_label
    current_dragged_coin_value = value
    floating_label = tk.Label(window, text=f"${value}", bg="gold", fg="white",
                            font=("Arial", 14), relief="raised")
    floating_label.update_idletasks()
    w = floating_label.winfo_reqwidth()
    h = floating_label.winfo_reqheight()
    x = window.winfo_pointerx() - window.winfo_rootx()
    y = window.winfo_pointery() - window.winfo_rooty()
    floating_label.place(x=x - w//2, y=y - h//2)

def drag_motion(event):
    if floating_label:
        w = floating_label.winfo_reqwidth()
        h = floating_label.winfo_reqheight()
        x = window.winfo_pointerx() - window.winfo_rootx()
        y = window.winfo_pointery() - window.winfo_rooty()
        floating_label.place(x=x - w//2, y=y - h//2)

def end_drag(event):
    global current_dragged_coin_value, floating_label
    if floating_label:
        floating_label.place_forget()
        x = window.winfo_pointerx()
        y = window.winfo_pointery()
        widget = window.winfo_containing(x, y)
        floating_label.destroy()
        floating_label = None

        if widget and current_dragged_coin_value:
            if hasattr(widget, 'number_id'):
                place_bet(widget.number_id, current_dragged_coin_value)
            elif hasattr(widget, 'bet_type'):
                place_special_bet(widget.bet_type, current_dragged_coin_value)
        current_dragged_coin_value = None

def place_bet(number, amount):
    if amount > balance:
        messagebox.showerror("Error", "Insufficient funds")
        return
    BetBucket[number] = BetBucket.get(number, 0) + amount
    bet_amount_labels[number].config(text=str(BetBucket[number]))
    update_balance(-amount)

def place_special_bet(bet_type, amount):
    global odd_even_bet, red_black_bet
    if amount > balance:
        messagebox.showerror("Error", "Insufficient funds")
        return
    if bet_type in ['odd', 'even']:
        if odd_even_bet and odd_even_bet != bet_type:
            messagebox.showwarning("Conflict", "Cannot bet both odd/even")
            return
        odd_even_bet = bet_type
    elif bet_type in ['red', 'black']:
        if red_black_bet and red_black_bet != bet_type:
            messagebox.showwarning("Conflict", "Cannot bet both colors")
            return
        red_black_bet = bet_type
    elif bet_type in interval_bets:
        current_intervals = [bt for bt in BetBucket if bt in interval_bets]
        if len(current_intervals) >= 2 and bet_type not in current_intervals:
            messagebox.showwarning("Conflict", "Maximum 2 interval bets allowed")
            return
    BetBucket[bet_type] = BetBucket.get(bet_type, 0) + amount
    if bet_type in interval_amount_labels:
        interval_amount_labels[bet_type].config(text=f"${BetBucket[bet_type]}")
    elif bet_type in special_labels:
        special_labels[bet_type].config(text=f"${BetBucket[bet_type]}")
    update_balance(-amount)

def clear_bet(number):
    if number in BetBucket:
        update_balance(BetBucket[number])
        del BetBucket[number]
    bet_amount_labels[number].config(text="0")

def clear_special_bet(bet_type):
    global odd_even_bet, red_black_bet
    if bet_type in BetBucket:
        update_balance(BetBucket[bet_type])
        del BetBucket[bet_type]
    if bet_type in interval_amount_labels:
        interval_amount_labels[bet_type].config(text="$0")
    elif bet_type in special_labels:
        special_labels[bet_type].config(text="$0")
    if bet_type in ['odd', 'even']:
        odd_even_bet = None
    elif bet_type in ['red', 'black']:
        red_black_bet = None

# --- GUI SETUP ---
initialize_player()

window = tk.Tk()
window.title(f"Roulette - {player_name}")
window.configure(bg="#228B22")

balance_label = tk.Label(window, text=f"Balance: ${balance:.2f}", 
                        font=("Arial", 14, "bold"), fg="white", bg="#228B22")
balance_label.pack(pady=5)

total_wins_label = tk.Label(window, text=f"Total Wins: ${total_wins:.2f}", 
                           font=("Arial", 12), fg="white", bg="#228B22")
total_wins_label.pack()

timer_number_frame = tk.Frame(window, bg="#228B22")
timer_number_frame.pack(pady=10)

timer_label = tk.Label(timer_number_frame, text="60", 
                      font=("Arial", 16, "bold"), fg="white", bg="#228B22")
timer_label.pack(side=tk.LEFT, padx=(0, 20))

current_number_display = tk.Label(timer_number_frame, text="Current Number: -", 
                                 font=("Arial", 18, "bold"), bg="#228B22", fg="white")
current_number_display.pack(side=tk.LEFT)

frame_container = tk.Frame(window, bg="#228B22")
frame_container.pack()

# Number grid
bet_frame = tk.Frame(frame_container, bg="#228B22")
bet_frame.pack(side=tk.LEFT, padx=20, pady=10)

bet_amount_labels = {}
for number in range(1, 37):
    row = (number-1) // 12
    col = (number-1) % 12
    cell = tk.Frame(bet_frame, bd=1, relief="solid", bg="#228B22")
    cell.grid(row=row, column=col, padx=2, pady=2)
    bg = "red" if number in redlist else "black"
    num_label = tk.Label(cell, text=str(number), bg=bg, fg="white", width=4,
                         font=("Arial", 18, "bold"))
    num_label.pack()
    num_label.number_id = number
    bet_amt_lbl = tk.Label(cell, text="0", width=5, font=("Arial", 12), bg="#228B22", fg="white")
    bet_amt_lbl.pack()
    bet_amount_labels[number] = bet_amt_lbl
    tk.Button(cell, text="Clear", 
            command=lambda n=number: clear_bet(n),
            bg="#ff6666", activebackground="#ff9999",
            font=("Arial", 10, "bold"), fg="white").pack(pady=1)

# --- INTERVAL BET BUTTONS UNDER THE NUMBER GRID ---
interval_frame = tk.Frame(window, bg="#228B22")
interval_frame.pack(side=tk.TOP, pady=(0, 0), fill=tk.X)

interval_labels = {}
interval_amount_labels = {}

interval_bet_defs = [
    ('1-12', 0, 4),
    ('13-24', 4, 4),
    ('25-36', 8, 4)
]
for bet, col_start, span in interval_bet_defs:
    container = tk.Frame(interval_frame, bg="#228B22")
    container.grid(row=0, column=col_start, columnspan=span, sticky='nsew')
    btn = tk.Button(
        container,
        text=bet,
        bg="#90ee90",
        font=("Arial", 18, "bold"),
        height=2,
        relief="raised"
    )
    btn.pack(fill=tk.BOTH, expand=True)
    btn.bet_type = bet
    btn.bind("<ButtonRelease-1>", end_drag)
    interval_labels[bet] = btn
    amount_frame = tk.Frame(container, bg="#228B22")
    amount_frame.pack(fill=tk.X)
    lbl = tk.Label(amount_frame, text="$0", font=("Arial", 12, "bold"), bg="#228B22", fg="black")
    lbl.pack(side=tk.LEFT, padx=5)
    interval_amount_labels[bet] = lbl
    clear_btn = tk.Button(
        amount_frame,
        text="Clear",
        bg="#ff6666",
        font=("Arial", 10, "bold"),
        command=lambda bt=bet: clear_special_bet(bt),
        fg="white"
    )
    clear_btn.pack(side=tk.LEFT)

for i in range(12):
    interval_frame.grid_columnconfigure(i, weight=1)

# --- SPECIAL BETS PANEL (ODD/EVEN, RED/BLACK) ---
special_frame = tk.Frame(frame_container, bg="#228B22")
special_frame.pack(side=tk.LEFT, padx=20, pady=10, fill=tk.BOTH, expand=True)

special_labels = {}
bet_types = [
    ('odd', 'Odd'), ('even', 'Even'),
    ('red', 'Red'), ('black', 'Black')
]

for idx, (bet_type, text) in enumerate(bet_types):
    frame = tk.Frame(special_frame, bg="#228B22")
    frame.pack(pady=8, fill=tk.BOTH, expand=True)
    if bet_type == 'red':
        btn = tk.Button(frame, text=text, width=12, height=2, font=("Arial", 16, "bold"),
                        bg="red", fg="white", activebackground="#ff3333")
    elif bet_type == 'black':
        btn = tk.Button(frame, text=text, width=12, height=2, font=("Arial", 16, "bold"),
                        bg="black", fg="white", activebackground="#333333")
    else:
        btn = tk.Button(frame, text=text, width=12, height=2, font=("Arial", 16, "bold"), fg="black")
    btn.bet_type = bet_type
    btn.pack(side=tk.LEFT, padx=4)
    btn.bind("<ButtonRelease-1>", end_drag)
    label = tk.Label(frame, text="$0", width=6, font=("Arial", 14), bg="#228B22", fg="black")
    label.pack(side=tk.LEFT, padx=4)
    special_labels[bet_type] = label
    tk.Button(frame, text="Clear", 
            command=lambda bt=bet_type: clear_special_bet(bt),
            bg="#ff6666", activebackground="#ff9999",
            font=("Arial", 10, "bold"), fg="white").pack(side=tk.LEFT, padx=2)

# Coin panel
coin_frame = tk.Frame(window, bg="#228B22")
coin_frame.pack(pady=20)

for value in [1, 5, 10, 25]:
    coin = tk.Label(coin_frame, text=f"${value}", bg="gold", fg="white",
                  font=("Arial", 14), relief="raised", padx=5, pady=2)
    coin.pack(side=tk.LEFT, padx=10)
    coin.bind("<ButtonPress-1>", lambda e, v=value: start_drag(e, v))
    coin.bind("<B1-Motion>", drag_motion)
    coin.bind("<ButtonRelease-1>", end_drag)

# Start game
update_timer()
window.mainloop()




