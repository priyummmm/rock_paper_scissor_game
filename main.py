
import random
import tkinter as tk
from tkinter import font as tkfont
import math

# ----------------------------------------------------------------------
# Palette — soft pastel "Ghibli" inspired colors
# ----------------------------------------------------------------------
SKY_TOP = "#bfe3f0"        # pale sky blue
SKY_BOTTOM = "#eaf6e3"     # soft mint horizon
HILL_FAR = "#9ec9a3"       # muted sage green (distant hill)
HILL_NEAR = "#6fa876"      # deeper grass green (near hill)
HILL_NEAREST = "#4f8f5c"   # front grass ridge
CLOUD_WHITE = "#fffdf6"
SUN_GLOW = "#fff3c4"
PANEL_WOOD = "#f6e9d7"     # warm parchment/wood panel
PANEL_WOOD_EDGE = "#d9b98a"
TEXT_DARK = "#4a3f35"
TEXT_SOFT = "#6b5c4f"
ACCENT_RED = "#e08283"     # soft coral (rock)
ACCENT_BLUE = "#8ab6d6"    # soft blue (paper)
ACCENT_GREEN = "#93b48a"   # soft green (scissors)
WIN_GOLD = "#e3b23c"
LOSE_MUTED = "#c17b6a"
TIE_BLUE = "#7c93a8"

CHOICES = ["Rock", "Paper", "Scissors"]
EMOJI = {"Rock": "\U0001FAA8", "Paper": "\U0001F4DC", "Scissors": "\u2702\uFE0F"}

BEATS = {
    "Rock": "Scissors",
    "Paper": "Rock",
    "Scissors": "Paper",
}


class GhibliRPS(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Wind Valley — Rock, Paper, Scissors")
        self.geometry("880x680")
        self.minsize(760, 600)
        self.configure(bg=SKY_TOP)

        self.player_score = 0
        self.computer_score = 0
        self.round_num = 0

        # Fonts — fall back gracefully if fancy fonts aren't installed
        self.title_font = self._pick_font(
            ["Papyrus", "Georgia", "Comic Sans MS"], size=30, weight="bold"
        )
        self.header_font = self._pick_font(
            ["Georgia", "Comic Sans MS"], size=16, weight="bold"
        )
        self.body_font = self._pick_font(["Georgia", "Verdana"], size=13)
        self.big_emoji_font = self._pick_font(["Segoe UI Emoji", "Arial"], size=54)
        self.result_font = self._pick_font(
            ["Georgia", "Comic Sans MS"], size=20, weight="bold"
        )
        self.button_font = self._pick_font(
            ["Georgia", "Comic Sans MS"], size=14, weight="bold"
        )

        # Background scenery canvas (fills the whole window, redraws on resize)
        self.bg_canvas = tk.Canvas(self, highlightthickness=0, bd=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_canvas.bind("<Configure>", self._on_resize)

        self._cloud_offsets = [0, 220, 480, 680]
        self._build_scene_static = True  # scenery is redrawn fully each resize

        # Foreground UI sits above the canvas
        self._build_ui()

        # Gentle cloud drift animation
        self._animate_clouds()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _pick_font(self, candidates, size, weight="normal"):
        available = set(tkfont.families())
        for name in candidates:
            if name in available:
                return tkfont.Font(family=name, size=size, weight=weight)
        return tkfont.Font(size=size, weight=weight)

    def _on_resize(self, event):
        self._draw_scenery(event.width, event.height)

    def _draw_scenery(self, w, h):
        c = self.bg_canvas
        c.delete("scenery")

        # --- Sky gradient (approximated with thin horizontal bands) ---
        steps = 40
        for i in range(steps):
            t = i / steps
            r1, g1, b1 = self._hex_to_rgb(SKY_TOP)
            r2, g2, b2 = self._hex_to_rgb(SKY_BOTTOM)
            r = int(r1 + (r2 - r1) * t)
            g = int(g1 + (g2 - g1) * t)
            b = int(b1 + (b2 - b1) * t)
            color = f"#{r:02x}{g:02x}{b:02x}"
            y0 = int(h * 0.55 * (i / steps))
            y1 = int(h * 0.55 * ((i + 1) / steps)) + 1
            c.create_rectangle(0, y0, w, y1, fill=color, outline="", tags="scenery")

        # --- Soft sun glow, upper right ---
        sx, sy, sr = w * 0.82, h * 0.16, 70
        for i in range(5, 0, -1):
            c.create_oval(
                sx - sr * i / 3, sy - sr * i / 3, sx + sr * i / 3, sy + sr * i / 3,
                fill=SUN_GLOW, outline="", stipple="gray25", tags="scenery"
            )
        c.create_oval(sx - 26, sy - 26, sx + 26, sy + 26, fill="#fff9e0",
                      outline="", tags="scenery")

        # --- Clouds ---
        for base_x in self._cloud_offsets:
            self._draw_cloud(c, (base_x % (w + 300)) - 100, h * 0.14, 1.0)
            self._draw_cloud(c, ((base_x + 150) % (w + 300)) - 100, h * 0.24, 0.7)

        # --- Rolling hills (layered) ---
        self._draw_hill(c, h, 0.62, HILL_FAR, wobble=0.05)
        self._draw_hill(c, h, 0.74, HILL_NEAR, wobble=0.08)
        self._draw_hill(c, h, 0.88, HILL_NEAREST, wobble=0.11)

        # send scenery behind everything
        c.tag_lower("scenery")

    def _draw_cloud(self, c, x, y, scale=1.0):
        puffs = [(0, 0, 22), (18, -8, 18), (-18, -6, 16), (34, 2, 14), (-32, 4, 13)]
        for dx, dy, r in puffs:
            r *= scale
            c.create_oval(
                x + dx * scale - r, y + dy * scale - r,
                x + dx * scale + r, y + dy * scale + r,
                fill=CLOUD_WHITE, outline="", tags="scenery"
            )

    def _draw_hill(self, c, h, base_frac, color, wobble=0.05):
        w = self.bg_canvas.winfo_width() or 880
        base_y = h * base_frac
        points = [(-20, h + 20)]
        segs = 10
        for i in range(segs + 1):
            x = -20 + (w + 40) * (i / segs)
            y = base_y + math.sin(i * 1.3 + base_frac * 10) * (h * wobble)
            points.append((x, y))
        points.append((w + 20, h + 20))
        flat = [coord for pt in points for coord in pt]
        c.create_polygon(flat, fill=color, outline="", smooth=True, tags="scenery")

    @staticmethod
    def _hex_to_rgb(hexstr):
        hexstr = hexstr.lstrip("#")
        return tuple(int(hexstr[i:i + 2], 16) for i in (0, 2, 4))

    def _animate_clouds(self):
        self._cloud_offsets = [(o + 0.4) for o in self._cloud_offsets]
        w = self.bg_canvas.winfo_width() or 880
        h = self.bg_canvas.winfo_height() or 680
        if w > 10 and h > 10:
            self._draw_scenery(w, h)
        self.after(60, self._animate_clouds)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        # Title banner
        self.title_label = tk.Label(
            self, text="\U0001F343  Wind Valley  \U0001F343",
            font=self.title_font, fg=TEXT_DARK, bg=SKY_TOP
        )
        self.title_label.place(relx=0.5, y=46, anchor="center")
        self.bg_canvas.tk_raise(self.title_label) if False else None

        self.subtitle_label = tk.Label(
            self, text="a gentle game of Rock, Paper, Scissors",
            font=self.body_font, fg=TEXT_SOFT, bg=SKY_TOP
        )
        self.subtitle_label.place(relx=0.5, y=82, anchor="center")

        # Scoreboard panel (wooden sign look)
        self.score_frame = tk.Frame(self, bg=PANEL_WOOD, highlightbackground=PANEL_WOOD_EDGE,
                                     highlightthickness=3)
        self.score_frame.place(relx=0.5, y=126, anchor="center", width=420, height=54)

        self.score_label = tk.Label(
            self.score_frame, text=self._score_text(),
            font=self.header_font, fg=TEXT_DARK, bg=PANEL_WOOD
        )
        self.score_label.pack(expand=True, fill="both")

        # Battle stage — two "cards" showing player & computer choices
        self.stage_frame = tk.Frame(self, bg="")
        self.stage_frame.place(relx=0.5, y=270, anchor="center", width=680, height=190)

        self.player_card = self._make_card(self.stage_frame, "You")
        self.player_card["outer"].place(x=0, y=0, width=280, height=190)

        self.vs_label = tk.Label(
            self.stage_frame, text="VS", font=self.header_font,
            fg=TEXT_SOFT, bg=SKY_TOP
        )
        self.vs_label.place(x=300, y=80, width=80, height=30)

        self.computer_card = self._make_card(self.stage_frame, "Totoro")
        self.computer_card["outer"].place(x=400, y=0, width=280, height=190)

        # Result banner
        self.result_label = tk.Label(
            self, text="Choose your move to begin \u2728",
            font=self.result_font, fg=TEXT_DARK, bg=SKY_TOP
        )
        self.result_label.place(relx=0.5, y=390, anchor="center")

        # Choice buttons
        self.buttons_frame = tk.Frame(self, bg=SKY_TOP)
        self.buttons_frame.place(relx=0.5, y=460, anchor="center")

        self.choice_buttons = {}
        colors = {"Rock": ACCENT_RED, "Paper": ACCENT_BLUE, "Scissors": ACCENT_GREEN}
        for i, choice in enumerate(CHOICES):
            btn = tk.Button(
                self.buttons_frame,
                text=f"{EMOJI[choice]}\n{choice}",
                font=self.button_font,
                fg="white",
                bg=colors[choice],
                activebackground=self._darken(colors[choice]),
                activeforeground="white",
                relief="flat",
                bd=0,
                width=8,
                height=3,
                cursor="hand2",
                command=lambda ch=choice: self.play_round(ch),
            )
            btn.grid(row=0, column=i, padx=14)
            self._add_hover(btn, colors[choice])
            self.choice_buttons[choice] = btn

        # Round history panel
        self.history_frame = tk.Frame(self, bg=PANEL_WOOD, highlightbackground=PANEL_WOOD_EDGE,
                                       highlightthickness=3)
        self.history_frame.place(relx=0.5, y=560, anchor="center", width=680, height=90)

        self.history_label = tk.Label(
            self.history_frame, text="Round history will appear here \U0001F33F",
            font=self.body_font, fg=TEXT_SOFT, bg=PANEL_WOOD,
            justify="left", anchor="w", wraplength=650
        )
        self.history_label.pack(expand=True, fill="both", padx=14, pady=8)
        self.history = []

        # Reset button, tucked bottom-right
        self.reset_btn = tk.Button(
            self, text="\U0001F343 New Journey", font=self.body_font,
            fg="white", bg=TIE_BLUE, activebackground=self._darken(TIE_BLUE),
            activeforeground="white", relief="flat", bd=0, cursor="hand2",
            command=self.reset_game
        )
        self.reset_btn.place(relx=0.5, y=628, anchor="center", width=160, height=34)
        self._add_hover(self.reset_btn, TIE_BLUE)

    def _make_card(self, parent, label_text):
        outer = tk.Frame(parent, bg=PANEL_WOOD, highlightbackground=PANEL_WOOD_EDGE,
                          highlightthickness=3)
        name_label = tk.Label(outer, text=label_text, font=self.header_font,
                               fg=TEXT_DARK, bg=PANEL_WOOD)
        name_label.pack(pady=(10, 0))
        emoji_label = tk.Label(outer, text="\u2753", font=self.big_emoji_font,
                                fg=TEXT_DARK, bg=PANEL_WOOD)
        emoji_label.pack(expand=True)
        move_label = tk.Label(outer, text="waiting...", font=self.body_font,
                               fg=TEXT_SOFT, bg=PANEL_WOOD)
        move_label.pack(pady=(0, 10))
        return {"outer": outer, "name": name_label, "emoji": emoji_label, "move": move_label}

    def _add_hover(self, widget, base_color):
        lighter = self._lighten(base_color)

        def on_enter(e):
            widget.configure(bg=lighter)

        def on_leave(e):
            widget.configure(bg=base_color)

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    @staticmethod
    def _darken(hexstr, factor=0.82):
        r, g, b = GhibliRPS._hex_to_rgb(hexstr)
        r, g, b = int(r * factor), int(g * factor), int(b * factor)
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def _lighten(hexstr, factor=1.15):
        r, g, b = GhibliRPS._hex_to_rgb(hexstr)
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _score_text(self):
        return f"\U0001F343  You: {self.player_score}      Round: {self.round_num}      Totoro: {self.computer_score}  \U0001F343"

    # ------------------------------------------------------------------
    # Game logic
    # ------------------------------------------------------------------
    def play_round(self, player_choice):
        computer_choice = random.choice(CHOICES)
        self.round_num += 1

        self.player_card["emoji"].configure(text=EMOJI[player_choice])
        self.player_card["move"].configure(text=player_choice)
        self.computer_card["emoji"].configure(text=EMOJI[computer_choice])
        self.computer_card["move"].configure(text=computer_choice)

        if player_choice == computer_choice:
            outcome = "tie"
            result_text = f"A gentle tie \u2014 both chose {player_choice}."
            color = TIE_BLUE
        elif BEATS[player_choice] == computer_choice:
            outcome = "win"
            self.player_score += 1
            result_text = f"You win this round! {player_choice} beats {computer_choice}. \U0001F31F"
            color = WIN_GOLD
        else:
            outcome = "lose"
            self.computer_score += 1
            result_text = f"Totoro wins this round. {computer_choice} beats {player_choice}. \U0001F343"
            color = LOSE_MUTED

        self.result_label.configure(text=result_text, fg=color)
        self.score_label.configure(text=self._score_text())

        self.history.insert(0, f"Round {self.round_num}: You {player_choice} vs Totoro {computer_choice} \u2192 "
                                f"{'Tie' if outcome=='tie' else ('You won' if outcome=='win' else 'Totoro won')}")
        self.history = self.history[:3]
        self.history_label.configure(text="\n".join(self.history))

        self._pulse(self.result_label)

    def _pulse(self, widget, step=0):
        # tiny scale-ish pulse effect using font size, purely decorative
        sizes = [22, 24, 22, 20]
        if step < len(sizes):
            widget.configure(font=tkfont.Font(family=self.result_font.actual("family"),
                                               size=sizes[step], weight="bold"))
            self.after(70, lambda: self._pulse(widget, step + 1))
        else:
            widget.configure(font=self.result_font)

    def reset_game(self):
        self.player_score = 0
        self.computer_score = 0
        self.round_num = 0
        self.score_label.configure(text=self._score_text())
        self.result_label.configure(text="Choose your move to begin \u2728", fg=TEXT_DARK)
        self.player_card["emoji"].configure(text="\u2753")
        self.player_card["move"].configure(text="waiting...")
        self.computer_card["emoji"].configure(text="\u2753")
        self.computer_card["move"].configure(text="waiting...")
        self.history = []
        self.history_label.configure(text="Round history will appear here \U0001F33F")


if __name__ == "__main__":
    app = GhibliRPS()
    app.mainloop()