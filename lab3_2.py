import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class ExpRegressionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лаб №3 - Експоненціальна регресія (Варіант 5)")
        self.root.geometry("1000x600")

        # Дані варіанту 5: y = ae^(bx)
        self.x_data = [1, 2, 3, 4, 5, 6, 7, 8]
        self.y_data = [0.3, 0.49, 0.59, 0.65, 0.71, 0.75, 0.77, 0.81]

        self.setup_ui()

    def setup_ui(self):
        # Ліва панель - дані
        left = ttk.Frame(self.root, padding=10)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(left, text="Дані варіанту 5:", font=('Arial', 11, 'bold')).pack()

        # Таблиця
        self.tree = ttk.Treeview(left, columns=('n', 'x', 'y'), show='headings', height=10)
        self.tree.heading('n', text='№')
        self.tree.heading('x', text='x')
        self.tree.heading('y', text='y')
        self.tree.column('n', width=50)
        self.tree.column('x', width=80)
        self.tree.column('y', width=80)
        self.tree.pack(pady=10)

        for i, (x, y) in enumerate(zip(self.x_data, self.y_data), 1):
            self.tree.insert('', tk.END, values=(i, x, y))

        ttk.Button(left, text="Розрахувати", command=self.calculate).pack(pady=5)

        # Результати
        ttk.Label(left, text="Результати:").pack(pady=(20, 5))
        self.result_text = tk.Text(left, height=8, width=35)
        self.result_text.pack()

        # Права панель - графік
        right = ttk.Frame(self.root, padding=10)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(6, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, right)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def calculate(self):
        try:
            x = np.array(self.x_data)
            y = np.array(self.y_data)

            # Лінеаризація: ln(y) = ln(a) + bx
            ln_y = np.log(y)

            # МНК для лінійної регресії
            n = len(x)
            sum_x = np.sum(x)
            sum_lny = np.sum(ln_y)
            sum_x_lny = np.sum(x * ln_y)
            sum_x2 = np.sum(x ** 2)

            # Коефіцієнти
            b = (n * sum_x_lny - sum_x * sum_lny) / (n * sum_x2 - sum_x ** 2)
            ln_a = (sum_lny - b * sum_x) / n
            a = np.exp(ln_a)

            # Розрахункові значення
            y_calc = a * np.exp(b * x)

            # R²
            ss_res = np.sum((y - y_calc) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r2 = 1 - (ss_res / ss_tot)

            # Виведення результатів
            self.result_text.delete(1.0, tk.END)
            result = f"""
Рівняння: y = ae^(bx)

Коефіцієнти:
  a = {a:.6f}
  b = {b:.6f}

Рівняння:
  y = {a:.4f}*e^({b:.4f}x)

Якість моделі:
  R² = {r2:.6f} ({r2 * 100:.2f}%)
"""
            self.result_text.insert(1.0, result)

            # Графік
            self.ax.clear()
            self.ax.scatter(x, y, color='blue', s=80, label='Дані', zorder=5)
            x_smooth = np.linspace(x.min(), x.max(), 100)
            y_smooth = a * np.exp(b * x_smooth)
            self.ax.plot(x_smooth, y_smooth, 'r-', linewidth=2,
                         label=f'y = {a:.3f}e^({b:.3f}x)')
            self.ax.set_xlabel('x')
            self.ax.set_ylabel('y')
            self.ax.set_title('Експоненціальна регресія')
            self.ax.legend()
            self.ax.grid(True, alpha=0.3)
            self.canvas.draw()

        except Exception as e:
            messagebox.showerror("Помилка", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpRegressionApp(root)
    root.mainloop()