import numpy as np
import tkinter as tk
from tkinter import messagebox
from enum import Enum

SIZE = 10
PIXEL_SIZE = 20
MAX_ETALON_COUNT = 5
FONT = ("Arial", 16)

ETALONS = {"n": np.array([[1, 1, -1, -1, -1, -1, -1, -1, 1, 1],
                 [1, 1, -1, -1, -1, -1, -1, -1, 1, 1],
                 [1, 1, -1, -1, -1, -1, -1, -1, 1, 1],
                 [1, 1, -1, -1, -1, -1, -1, -1, 1, 1],
                 [1, 1,  1,  1,  1,  1,  1,  1, 1, 1],
                 [1, 1,  1,  1,  1,  1,  1,  1, 1, 1],
                 [1, 1, -1, -1, -1, -1, -1, -1, 1, 1],
                 [1, 1, -1, -1, -1, -1, -1, -1, 1, 1],
                 [1, 1, -1, -1, -1, -1, -1, -1, 1, 1],
                 [1, 1, -1, -1, -1, -1, -1, -1, 1, 1]]),

           "f": np.array([[-1, -1, -1, -1, 1, 1, -1, -1, -1, -1],
                 [-1, -1,  1,  1, 1, 1,  1,  1, -1, -1],
                 [-1,  1,  1, -1, 1, 1, -1,  1,  1, -1],
                 [ 1,  1, -1, -1, 1, 1, -1, -1,  1,  1],
                 [ 1, -1, -1, -1, 1, 1, -1, -1, -1,  1],
                 [ 1, -1, -1, -1, 1, 1, -1, -1, -1,  1],
                 [ 1,  1, -1, -1, 1, 1, -1, -1,  1,  1],
                 [-1,  1,  1, -1, 1, 1, -1,  1,  1, -1],
                 [-1, -1,  1,  1, 1, 1,  1,  1, -1, -1],
                 [-1, -1, -1, -1, 1, 1, -1, -1, -1, -1]]),

           "u": np.array([[1, 1, -1, -1, -1, -1, -1, -1, 1, 1],
                 [1, 1, -1, -1, -1, -1, -1, -1, 1, 1],
                 [1, 1, -1, -1, -1, -1, -1,  1, 1, 1],
                 [1, 1, -1, -1, -1, -1,  1,  1, 1, 1],
                 [1, 1, -1, -1, -1,  1,  1, -1, 1, 1],
                 [1, 1, -1, -1,  1,  1, -1, -1, 1, 1],
                 [1, 1, -1,  1,  1, -1, -1, -1, 1, 1],
                 [1, 1,  1,  1, -1, -1, -1, -1, 1, 1],
                 [1, 1,  1, -1, -1, -1, -1, -1, 1, 1],
                 [1, 1, -1, -1, -1, -1, -1, -1, 1, 1]])
           }

def recognize(data, weights_collection):
    weights = np.array(weights_collection.find_one().get("data"))

    x = np.array(data).reshape(-1)
    answer = x @ weights.T

    return np.where(answer > 0, 1, -1).flatten()

class Color(Enum):
    WHITE = "white"
    BLACK = "black"

def dangerous_draw(canvas, x, y, color=Color.BLACK, outline=Color.BLACK):
    x_start, y_start = x * PIXEL_SIZE, y * PIXEL_SIZE
    x_end, y_end = x_start + PIXEL_SIZE, y_start + PIXEL_SIZE
    canvas.create_rectangle(x_start, y_start, x_end, y_end, fill=color.name, outline=outline.name)

def draw(canvas, x, y, color=Color.BLACK, outline=Color.BLACK):
    if x >= SIZE or x < 0 or y >= SIZE or y < 0:
        return
    dangerous_draw(canvas, x, y, color, outline)

def clear(canvas, outline=Color.BLACK):
    for i in range(SIZE):
        for j in range(SIZE):
            draw(canvas, i, j, Color.WHITE, outline)

class Etalon:
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.pixels = np.zeros((SIZE, SIZE))

    def draw(self, x, y, color: Color):
        draw(self.canvas, x, y, color, Color.WHITE)
        self.pixels[y, x] = color == Color.BLACK

    def clear(self):
        clear(self.canvas, Color.WHITE)
        self.pixels = np.zeros((SIZE, SIZE))

class HopfieldNetwork(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Мережа Хопфілда")
        self.geometry("1150x600")
        self.resizable(width=False, height=False)

        self.filled_etalon_count = 0
        self.weights = np.zeros((SIZE * SIZE, SIZE * SIZE), dtype=float)
        self.drawing_grid = np.zeros((SIZE, SIZE))

        self._setup_drawing_frame()
        self._setup_etalons_frame()
        self._setup_buttons_frame()

    def _setup_drawing_frame(self):
        # Основна область для малювання та відображення рисунків
        main_frame = tk.Frame(self)
        main_frame.pack()

        tk.Label(main_frame, text="Малювати тут", font=FONT).grid(row=0, column=0, padx=10, pady=5)
        tk.Label(main_frame, text="Результат", font=FONT).grid(row=0, column=1, padx=10, pady=5)
        self.canvas = tk.Canvas(main_frame, width=SIZE * PIXEL_SIZE - 1, height=SIZE * PIXEL_SIZE - 1, bg="white",
                                relief="solid")
        self.canvas.grid(row=1, column=0)

        self.recognition_canvas = tk.Canvas(main_frame, width=SIZE * PIXEL_SIZE - 1, height=SIZE * PIXEL_SIZE - 1,
                                            bg="white", relief="solid")
        self.recognition_canvas.grid(row=1, column=1, padx=10)
        self._create_drawing_grid()

        self.canvas.bind("<Button-1>", self._draw_black)
        self.canvas.bind("<B1-Motion>", self._draw_black)
        self.canvas.bind("<Button-3>", self._draw_white)
        self.canvas.bind("<B3-Motion>", self._draw_white)

    def _setup_etalons_frame(self):
        # Зона з еталонами, які не можна редагувати
        etalon_frame = tk.Frame(self, height=SIZE * PIXEL_SIZE)
        etalon_frame.pack(pady=20)

        tk.Label(etalon_frame, text="Еталони", font=FONT).grid(row=0, column=2, padx=10, pady=5)

        self.etalons = []
        for i in range(MAX_ETALON_COUNT):
            canvas = tk.Canvas(etalon_frame, width=SIZE * PIXEL_SIZE - 1, height=SIZE * PIXEL_SIZE - 1, bg="white",
                               relief="solid")
            canvas.grid(row=1, column=i, padx=10)
            self.etalons.append(Etalon(canvas))

        for etalon in ETALONS.values():
            self._draw_etalon(etalon)
            self._train(etalon)

    def _setup_buttons_frame(self):
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Додати еталон", font=FONT, command=self._add_etalon).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Розпізнати", font=FONT, command=self._recognize).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Очистити поле", font=FONT, command=self._clear_drawing).grid(row=0, column=3, padx=5)
        tk.Button(button_frame, text="Очистити еталони", font=FONT, bg="red", activebackground="darkred", fg="white",
                  activeforeground="white", command=self._clear_etalons).grid(row=0, column=4, padx=5)

    def _add_etalon(self):
        self._draw_etalon(self.drawing_grid)
        self._train(self.drawing_grid)

    def _retrain_all(self):
        for etalon in ETALONS.values():
            self._train(etalon)
        self.weights /= SIZE

    def _train(self, pattern):
        flat_pattern = pattern.flatten()
        self.weights += np.outer(flat_pattern, flat_pattern) / len(flat_pattern)
        np.fill_diagonal(self.weights, 0)

    def _recognize(self, max_iterations=100):
        flat_pattern = self.drawing_grid.flatten()
        for _ in range(max_iterations):
            updated_pattern = np.sign(self.weights @ flat_pattern)
            updated_pattern[updated_pattern == 0] = -1
            if np.array_equal(flat_pattern, updated_pattern):
                break
            flat_pattern = updated_pattern

        answer = flat_pattern.reshape(self.drawing_grid.shape)
        self._draw_grid(self.recognition_canvas, answer)

    def _draw_etalon(self, etalon):
        if self.filled_etalon_count >= MAX_ETALON_COUNT:
            messagebox.showerror("Помилка", "Максимальна кількість еталонів!")
            return

        self._draw_grid(self.etalons[self.filled_etalon_count].canvas, etalon)

        rows, cols = etalon.shape
        for y in range(rows):
            for x in range(cols):
                self.etalons[self.filled_etalon_count].draw(x, y, Color.BLACK if etalon[y][x] > 0 else Color.WHITE)

        self.filled_etalon_count += 1

    def _draw_grid(self, canvas, grid):
        shape = grid.shape
        if shape[0] > SIZE or shape[1] > SIZE:
            messagebox.showerror("Помилка", "Спроба намалювати рисунок більший за площину!")
            return

        for y in range(shape[0]):
            for x in range(shape[1]):
                draw(canvas, x, y, Color.BLACK if grid[y][x] > 0 else Color.WHITE)

    def _create_drawing_grid(self):
        for i in range(SIZE):
            for j in range(SIZE):
                draw(self.canvas, i, j, Color.WHITE)

    def _draw_black(self, event):
        self._draw_on_canvas(event, Color.BLACK)

    def _draw_white(self, event):
        self._draw_on_canvas(event, Color.WHITE)

    def _draw_on_canvas(self, event, color: Color):
        # Знайти координати пікселя
        x, y = event.x // PIXEL_SIZE, event.y // PIXEL_SIZE
        if x >= SIZE or x < 0 or y >= SIZE or y < 0:
            return

        dangerous_draw(self.canvas, x, y, color)
        self.drawing_grid[y][x] = color == Color.BLACK

    def _clear_etalons(self):
        for etalon in self.etalons:
            etalon.clear()
        self.filled_etalon_count = 0
        self.weights = np.zeros((SIZE * SIZE, SIZE * SIZE))

    def _clear_drawing(self):
        self.drawing_grid = np.zeros((SIZE, SIZE))
        clear(self.canvas)


if __name__ == "__main__":
    network = HopfieldNetwork()
    network.mainloop()
