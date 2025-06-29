import tkinter as tk
import random

# Globals
difficulty = None
window = None
buttons = []
board = []
player_score = 0
ai_score = 0
score_label = None
cell_colors = []
overlay_canvas = None

# --- Utility Functions ---
def check_win(b, player):
    for i in range(3):
        if all(b[i][j] == player for j in range(3)) or all(b[j][i] == player for j in range(3)):
            return True
    if all(b[i][i] == player for i in range(3)) or all(b[i][2 - i] == player for i in range(3)):
        return True
    return False

def add_hover_effects(btn, base_color):
    def on_enter(e): btn.config(bg="#cccccc")
    def on_leave(e): btn.config(bg=base_color)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

def confetti_effect():
    for _ in range(30):
        x = random.randint(10, window.winfo_width()-10)
        y = random.randint(10, window.winfo_height()-10)
        size = random.randint(5, 12)
        color = random.choice(["#FFC0CB", "#FFD700", "#ADFF2F", "#00BFFF", "#FF4500"])
        dot = overlay_canvas.create_oval(x, y, x + size, y + size, fill=color, outline="")
        overlay_canvas.after(random.randint(500, 1500), lambda d=dot: overlay_canvas.delete(d))

def show_result_overlay(message):
    global overlay_canvas
    w, h = window.winfo_width(), window.winfo_height()
    overlay_canvas = tk.Canvas(window, width=w, height=h, bg='black', highlightthickness=0)
    overlay_canvas.place(x=0, y=0)
    overlay_canvas.create_rectangle(0, 0, w, h, fill='black', stipple='gray50')

    emoji = "🎉" if "You" in message else "🤖" if "AI" in message else "😐"
    overlay_canvas.create_text(w//2, h//2 - 30, text=f"{emoji} {message}", font=("Helvetica", 24, "bold"), fill="white")

    play_again_btn = tk.Button(window, text="🔁 Play Again", font=("Helvetica", 12, "bold"), bg="white", fg="black", command=restart_game)
    overlay_canvas.create_window(w//2, h//2 + 20, window=play_again_btn)

    confetti_effect()
    for row in buttons:
        for btn in row:
            btn.config(state="disabled")

# --- Game Logic ---
def ai_move():
    global ai_score
    move = None
    empty = [(i, j) for i in range(3) for j in range(3) if board[i][j] == ""]
    if difficulty == "easy":
        move = random.choice(empty)
    elif difficulty == "medium":
        if random.random() < 0.5:
            move = random.choice(empty)
        else:
            if board[1][1] == "":
                move = (1, 1)
            else:
                corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
                move = next(((i, j) for i, j in corners if board[i][j] == ""), None) or random.choice(empty)
    else:
        best_score = -float("inf")
        for i, j in empty:
            board[i][j] = "O"
            score = minimax(board, 0, False)
            board[i][j] = ""
            if score > best_score:
                best_score = score
                move = (i, j)

    if move:
        i, j = move
        board[i][j] = "O"
        buttons[i][j].config(text="O", state="disabled", disabledforeground="blue")
        if check_win(board, "O"):
            ai_score += 1
            update_score()
            show_result_overlay("AI Won!")
        elif all(cell != "" for row in board for cell in row):
            show_result_overlay("It's a Draw!")

def minimax(b, depth, is_max):
    if check_win(b, "O"): return 1
    if check_win(b, "X"): return -1
    if all(cell != "" for row in b for cell in row): return 0

    best = -float("inf") if is_max else float("inf")
    for i in range(3):
        for j in range(3):
            if b[i][j] == "":
                b[i][j] = "O" if is_max else "X"
                score = minimax(b, depth+1, not is_max)
                b[i][j] = ""
                best = max(best, score) if is_max else min(best, score)
    return best

def on_click(i, j):
    global player_score
    if board[i][j] == "":
        board[i][j] = "X"
        buttons[i][j].config(text="X", state="disabled", disabledforeground="black")
        if check_win(board, "X"):
            player_score += 1
            update_score()
            show_result_overlay("You Won!")
        elif all(cell != "" for row in board for cell in row):
            show_result_overlay("It's a Draw!")
        else:
            ai_move()

def restart_game():
    global board, overlay_canvas
    board = [["" for _ in range(3)] for _ in range(3)]

    color_palettes = {
        "easy": ["#FFEBEE", "#E3F2FD", "#E8F5E9", "#FFF3E0", "#F3E5F5", "#E0F7FA", "#FCE4EC", "#F9FBE7", "#EDE7F6"],
        "medium": ["#FFC1C1", "#FFB6C1", "#ADD8E6", "#E6E6FA", "#DDA0DD", "#FFDAB9", "#B0E0E6", "#FFFACD", "#E0FFFF"],
        "hard": ["#70555A", "#915857", "#607D79", "#E7DC7B", "#ACCDAD", "#865F67", "#8E4A49", "#527570", "#F2E78A"]
    }
    themed_colors = color_palettes.get(difficulty, color_palettes["medium"])
    random.shuffle(themed_colors)

    idx = 0
    for i in range(3):
        for j in range(3):
            buttons[i][j].config(text="", state="normal", bg=themed_colors[idx], font=("Helvetica", 28), fg="black")
            add_hover_effects(buttons[i][j], themed_colors[idx])
            idx += 1

    if overlay_canvas:
        overlay_canvas.destroy()

def update_score():
    score_label.config(text=f"Player (X): {player_score}    AI (O): {ai_score}")

def change_difficulty():
    def set_diff_and_restart(level):
        nonlocal diff_window
        global difficulty
        difficulty = level
        diff_window.destroy()
        restart_game()

    diff_window = tk.Toplevel(window)
    diff_window.title("Select Difficulty")
    diff_window.configure(bg="#2e2e2e")
    tk.Label(diff_window, text="Choose Difficulty", font=("Helvetica", 14, "bold"), fg="white", bg="#2e2e2e").pack(pady=10)
    for level in ["easy", "medium", "hard"]:
        tk.Button(diff_window, text=level.capitalize(), font=("Helvetica", 12), command=lambda l=level: set_diff_and_restart(l)).pack(pady=5)

def build_main_window():
    global window, buttons, board, score_label, cell_colors
    window = tk.Tk()
    window.title("Tic Tac Toe")
    window.configure(bg="#2e2e2e")

    board[:] = [["" for _ in range(3)] for _ in range(3)]
    buttons[:] = [[None for _ in range(3)] for _ in range(3)]
    cell_colors[:] = ["#FFC1C1", "#FFB6C1", "#ADD8E6", "#E6E6FA", "#DDA0DD", "#FFDAB9", "#B0E0E6", "#FFFACD", "#E0FFFF"]
    random.shuffle(cell_colors)

    idx = 0
    for i in range(3):
        for j in range(3):
            btn = tk.Button(window, text="", font=('Helvetica', 28), width=5, height=2, bg=cell_colors[idx], fg="black", command=lambda r=i, c=j: on_click(r, c))
            btn.grid(row=i, column=j, padx=5, pady=5)
            buttons[i][j] = btn
            add_hover_effects(btn, cell_colors[idx])
            idx += 1

    tk.Button(window, text="Restart 🔁", font=("Helvetica", 12), bg="#444444", fg="white", command=restart_game).grid(row=3, column=0, columnspan=3, pady=5)
    tk.Button(window, text="Change Difficulty ⚙️", font=("Helvetica", 12), bg="#444444", fg="white", command=change_difficulty).grid(row=4, column=0, columnspan=3, pady=5)
    score_label = tk.Label(window, text=f"Player (X): {player_score}    AI (O): {ai_score}", font=("Helvetica", 14, "bold"), bg="#2e2e2e", fg="white")
    score_label.grid(row=5, column=0, columnspan=3, pady=10)

def start_game(level):
    global difficulty
    difficulty = level.lower()
    diff_win.destroy()
    build_main_window()


diff_win = tk.Tk()
diff_win.title("Select Difficulty")
diff_win.geometry("300x200")
diff_win.configure(bg="#2e2e2e")

tk.Label(diff_win, text="Choose Difficulty", font=("Helvetica", 16, "bold"), bg="#2e2e2e", fg="white").pack(pady=20)
tk.Button(diff_win, text="Easy", width=15, font=("Helvetica", 12), command=lambda: start_game("Easy")).pack(pady=5)
tk.Button(diff_win, text="Medium", width=15, font=("Helvetica", 12), command=lambda: start_game("Medium")).pack(pady=5)
tk.Button(diff_win, text="Hard", width=15, font=("Helvetica", 12), command=lambda: start_game("Hard")).pack(pady=5)

diff_win.mainloop()
