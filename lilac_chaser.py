import tkinter as tk
import math

# =========
# Config
# =========
CANVAS_WIDTH = 700
CANVAS_HEIGHT = 700
CONTROLS_WIDTH = 200
WIDTH = CANVAS_WIDTH + CONTROLS_WIDTH
HEIGHT = CANVAS_HEIGHT

BG_COLOR = "#808080"      # neutral gray
DOT_COLOR = "#C8A2C8"     # lilac-ish
CROSS_COLOR = "#000000"   # black

N_DOTS = 12
RING_RADIUS = 240
DOT_RADIUS = 28

CROSS_ARM = 12            # half-length of each cross arm
CROSS_WIDTH = 2

TICK_MS = 90              # lower = faster

INSTRUCTIONS = "Stare at the cross. Space: pause/resume. Esc: quit."


class LilacChaserApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Lilac Chaser with Controls")
        root.resizable(False, False)
        root.geometry(f"{WIDTH}x{HEIGHT}")

        # Main frame to hold canvas and controls
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            main_frame,
            width=CANVAS_WIDTH,
            height=CANVAS_HEIGHT,
            bg=BG_COLOR,
            highlightthickness=0,
        )
        self.canvas.pack(side=tk.LEFT)

        # Controls panel
        self.controls_frame = tk.Frame(main_frame, width=CONTROLS_WIDTH, bg="#f0f0f0")
        self.controls_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.controls_frame.pack_propagate(False)

        self.cx = CANVAS_WIDTH / 2
        self.cy = CANVAS_HEIGHT / 2

        # Draw dots once; store IDs for fast hide/show (no redraw flicker)
        self.dot_ids = []
        for i in range(N_DOTS):
            x, y = self._dot_center(i)
            dot_id = self.canvas.create_oval(
                x - DOT_RADIUS, y - DOT_RADIUS,
                x + DOT_RADIUS, y + DOT_RADIUS,
                fill=DOT_COLOR,
                outline=""
            )
            self.dot_ids.append(dot_id)

        # Fixation cross (draw after dots so it's on top)
        h = self.canvas.create_line(
            self.cx - CROSS_ARM, self.cy,
            self.cx + CROSS_ARM, self.cy,
            fill=CROSS_COLOR, width=CROSS_WIDTH
        )
        v = self.canvas.create_line(
            self.cx, self.cy - CROSS_ARM,
            self.cx, self.cy + CROSS_ARM,
            fill=CROSS_COLOR, width=CROSS_WIDTH
        )
        self.canvas.tag_raise(h)
        self.canvas.tag_raise(v)

        # Optional instruction text
        self.canvas.create_text(
            self.cx, CANVAS_HEIGHT - 20,
            text=INSTRUCTIONS,
            fill="#000000",
            font=("TkDefaultFont", 10)
        )

        # Setup controls
        self._setup_controls()

        # Animation state
        self.missing_index = 0
        self.current_tick_ms = TICK_MS
        self.clockwise = True
        self.current_bg_color = BG_COLOR
        self.current_dot_color = DOT_COLOR
        self.canvas.itemconfigure(self.dot_ids[self.missing_index], state="hidden")

        self.running = True
        self.after_id = None

        # Controls
        root.bind("<space>", self.toggle_pause)
        root.bind("<Escape>", self.quit)
        root.protocol("WM_DELETE_WINDOW", self.quit)

        self._schedule_next()

    def _dot_center(self, i: int):
        # Start at 12 o'clock, then step clockwise
        angle = (2 * math.pi) * (i / N_DOTS) - (math.pi / 2)
        x = self.cx + RING_RADIUS * math.cos(angle)
        y = self.cy + RING_RADIUS * math.sin(angle)
        return x, y

    def _setup_controls(self):
        # Speed control
        tk.Label(self.controls_frame, text="Speed", bg="#f0f0f0").pack(pady=5)
        self.speed_var = tk.IntVar(value=TICK_MS)
        speed_scale = tk.Scale(
            self.controls_frame, 
            from_=5, to=1000, 
            orient=tk.HORIZONTAL,
            variable=self.speed_var,
            command=self._update_speed
        )
        speed_scale.pack(padx=10, pady=5)

        # Direction control
        tk.Label(self.controls_frame, text="Direction", bg="#f0f0f0").pack(pady=5)
        direction_btn = tk.Button(
            self.controls_frame,
            text="Clockwise",
            command=self._toggle_direction
        )
        direction_btn.pack(pady=5)
        self.direction_btn = direction_btn

        # Dot colors
        tk.Label(self.controls_frame, text="Dot Color", bg="#f0f0f0").pack(pady=5)
        dot_colors = [("Lilac", "#C8A2C8"), ("Red", "#FF6B6B"), ("Blue", "#2196F3"), ("Green", "#4CAF50")]
        for name, color in dot_colors:
            btn = tk.Button(
                self.controls_frame,
                text=name,
                bg=color,
                command=self._make_dot_color_callback(color)
            )
            btn.pack(pady=2)

        # Background colors
        tk.Label(self.controls_frame, text="Background", bg="#f0f0f0").pack(pady=5)
        bg_colors = [("Gray", "#808080"), ("White", "#FFFFFF"), ("Black", "#000000"), ("Dark Gray", "#404040")]
        for name, color in bg_colors:
            btn = tk.Button(
                self.controls_frame,
                text=name,
                command=self._make_bg_color_callback(color)
            )
            btn.pack(pady=2)

    def _update_speed(self, value):
        self.current_tick_ms = int(value)

    def _toggle_direction(self):
        self.clockwise = not self.clockwise
        self.direction_btn.config(text="Clockwise" if self.clockwise else "Counterclockwise")

    def _make_dot_color_callback(self, color):
        return lambda: self._update_dot_color(color)

    def _update_dot_color(self, color):
        self.current_dot_color = color
        for dot_id in self.dot_ids:
            self.canvas.itemconfigure(dot_id, fill=color)

    def _make_bg_color_callback(self, color):
        return lambda: self._update_bg_color(color)

    def _update_bg_color(self, color):
        self.current_bg_color = color
        self.canvas.configure(bg=color)

    def _schedule_next(self):
        # Avoid stacking timers: only schedule if none pending
        if self.running and self.after_id is None:
            self.after_id = self.root.after(self.current_tick_ms, self.tick)

    def tick(self):
        # This scheduled callback has fired, so clear the handle first
        self.after_id = None
        if not self.running:
            return

        prev = self.missing_index
        if self.clockwise:
            self.missing_index = (self.missing_index + 1) % N_DOTS
        else:
            self.missing_index = (self.missing_index - 1) % N_DOTS

        # Show previous; hide new (the "gap" moves)
        self.canvas.itemconfigure(self.dot_ids[prev], state="normal")
        self.canvas.itemconfigure(self.dot_ids[self.missing_index], state="hidden")

        self._schedule_next()

    def toggle_pause(self, event=None):
        self.running = not self.running
        if not self.running:
            if self.after_id is not None:
                try:
                    self.root.after_cancel(self.after_id)
                except tk.TclError:
                    pass
                self.after_id = None
        else:
            self._schedule_next()

    def quit(self, event=None):
        self.running = False
        if self.after_id is not None:
            try:
                self.root.after_cancel(self.after_id)
            except tk.TclError:
                pass
            self.after_id = None
        self.root.destroy()


def main():
    root = tk.Tk()
    LilacChaserApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
