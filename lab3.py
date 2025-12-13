import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import json


class RegressionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторна робота №3 - Лінійна регресія (Варіант 5)")
        self.root.geometry("1200x700")

        # Встановлення іконки (за замовчуванням)
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass

        # Дані варіанту 5
        self.x_data = [1, 2, 3, 4, 5, 6, 7, 8]
        self.y_data = [0.3, 0.49, 0.59, 0.65, 0.71, 0.75, 0.77, 0.81]

        # Результати регресії
        self.a = None
        self.b = None
        self.regression_line = None

        # Створення головного меню
        self.create_menu()

        # Створення рядка стану
        self.create_status_bar()

        # Створення основного інтерфейсу
        self.create_main_interface()

    def create_menu(self):
        """Створення головного меню"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Зберегти результати", command=self.save_results)
        file_menu.add_separator()
        file_menu.add_command(label="Вихід", command=self.root.quit)

        # Меню "Допомога"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Допомога", menu=help_menu)

    def create_status_bar(self):
        """Створення рядка стану"""
        self.status_bar = tk.Label(self.root, text="Готово до роботи",
                                   bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_status(self, message):
        """Оновлення рядка стану"""
        self.status_bar.config(text=message)
        self.root.update_idletasks()

    def create_main_interface(self):
        """Створення основного інтерфейсу"""
        # Головний контейнер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Ліва панель - введення даних
        left_frame = ttk.LabelFrame(main_frame, text="Введення початкових даних",
                                    padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Таблиця даних
        self.create_data_table(left_frame)

        # Кнопки управління
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="Розрахувати регресію",
                   command=self.calculate_regression).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Очистити",
                   command=self.clear_results).pack(side=tk.LEFT, padx=5)

        # Права панель - результати
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Панель результатів
        results_frame = ttk.LabelFrame(right_frame, text="Результати розрахунку",
                                       padding="10")
        results_frame.pack(fill=tk.X, pady=(0, 10))

        self.results_text = tk.Text(results_frame, height=8, width=50)
        self.results_text.pack(fill=tk.BOTH, expand=True)

        # Панель графіка
        graph_frame = ttk.LabelFrame(right_frame, text="Графік регресії",
                                     padding="10")
        graph_frame.pack(fill=tk.BOTH, expand=True)

        self.create_plot(graph_frame)

    def create_data_table(self, parent):
        """Створення таблиці для введення даних"""
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Заголовок
        ttk.Label(table_frame, text="Експериментальні дані (Варіант 5):",
                  font=('Arial', 10, 'bold')).pack(pady=5)

        # Створення Treeview для таблиці
        columns = ('index', 'x', 'y')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings',
                                 height=10)

        self.tree.heading('index', text='№')
        self.tree.heading('x', text='x')
        self.tree.heading('y', text='y')

        self.tree.column('index', width=50, anchor=tk.CENTER)
        self.tree.column('x', width=100, anchor=tk.CENTER)
        self.tree.column('y', width=100, anchor=tk.CENTER)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL,
                                  command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Заповнення таблиці даними
        self.populate_table()

        # Кнопки редагування
        edit_frame = ttk.Frame(parent)
        edit_frame.pack(fill=tk.X, pady=10)

        ttk.Button(edit_frame, text="Редагувати значення",
                   command=self.edit_value).pack(side=tk.LEFT, padx=5)
        ttk.Button(edit_frame, text="Відновити дані варіанту",
                   command=self.restore_default_data).pack(side=tk.LEFT, padx=5)

    def populate_table(self):
        """Заповнення таблиці даними"""
        # Очистка таблиці
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Додавання даних
        for i, (x, y) in enumerate(zip(self.x_data, self.y_data), 1):
            self.tree.insert('', tk.END, values=(i, x, y))

    def edit_value(self):
        """Редагування вибраного значення"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Увага", "Виберіть рядок для редагування")
            return

        item = selected[0]
        values = self.tree.item(item)['values']

        # Діалогове вікно для редагування
        dialog = tk.Toplevel(self.root)
        dialog.title("Редагування значення")
        dialog.geometry("300x150")

        ttk.Label(dialog, text=f"Точка №{values[0]}").pack(pady=10)

        ttk.Label(dialog, text="Значення x:").pack()
        x_entry = ttk.Entry(dialog)
        x_entry.insert(0, str(values[1]))
        x_entry.pack(pady=5)

        ttk.Label(dialog, text="Значення y:").pack()
        y_entry = ttk.Entry(dialog)
        y_entry.insert(0, str(values[2]))
        y_entry.pack(pady=5)

        def save_edit():
            try:
                new_x = float(x_entry.get())
                new_y = float(y_entry.get())

                idx = int(values[0]) - 1
                self.x_data[idx] = new_x
                self.y_data[idx] = new_y

                self.populate_table()
                dialog.destroy()
                self.update_status("Значення оновлено")
            except ValueError:
                messagebox.showerror("Помилка", "Введіть коректні числові значення")

        ttk.Button(dialog, text="Зберегти", command=save_edit).pack(pady=10)

    def restore_default_data(self):
        """Відновлення даних за замовчуванням"""
        self.x_data = [1, 2, 3, 4, 5, 6, 7, 8]
        self.y_data = [0.3, 0.49, 0.59, 0.65, 0.71, 0.75, 0.77, 0.81]
        self.populate_table()
        self.update_status("Дані відновлено до значень варіанту 5")

    def create_plot(self, parent):
        """Створення області для графіка"""
        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.figure, parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def calculate_regression(self):
        """Розрахунок лінійної регресії методом найменших квадратів"""
        try:
            self.update_status("Виконується розрахунок...")

            n = len(self.x_data)
            x = np.array(self.x_data)
            y = np.array(self.y_data)

            # Розрахунок коефіцієнтів методом найменших квадратів
            # y = a + bx
            sum_x = np.sum(x)
            sum_y = np.sum(y)
            sum_xy = np.sum(x * y)
            sum_x2 = np.sum(x ** 2)

            # Коефіцієнт b
            self.b = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)

            # Коефіцієнт a
            self.a = (sum_y - self.b * sum_x) / n

            # Розрахунок значень регресії
            self.regression_line = self.a + self.b * x

            # Розрахунок похибок
            residuals = y - self.regression_line
            ss_res = np.sum(residuals ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)

            # Коефіцієнт детермінації R²
            r_squared = 1 - (ss_res / ss_tot)

            # Середньоквадратична похибка
            mse = np.sqrt(ss_res / n)

            # Відображення результатів
            self.display_results(r_squared, mse)

            # Побудова графіка
            self.plot_regression()

            self.update_status("Розрахунок завершено успішно")

        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка при розрахунку: {str(e)}")
            self.update_status("Помилка розрахунку")

    def display_results(self, r_squared, mse):
        """Відображення результатів розрахунку"""
        self.results_text.delete(1.0, tk.END)

        results = f"""
РЕЗУЛЬТАТИ РЕГРЕСІЙНОГО АНАЛІЗУ
{'=' * 50}

Рівняння регресії:
y = {self.a:.6f} + {self.b:.6f}x

Коефіцієнти:
  a (зміщення) = {self.a:.6f}
  b (нахил) = {self.b:.6f}

Показники якості:
  R² (коефіцієнт детермінації) = {r_squared:.6f}
  Середньоквадратична похибка = {mse:.6f}

Інтерпретація:
  R² = {r_squared:.2%} варіації y пояснюється моделлю
"""

        self.results_text.insert(1.0, results)

    def plot_regression(self):
        """Побудова графіка регресії"""
        self.ax.clear()

        x = np.array(self.x_data)
        y = np.array(self.y_data)

        # Експериментальні точки
        self.ax.scatter(x, y, color='blue', s=100, label='Експериментальні дані',
                        zorder=5)

        # Лінія регресії
        self.ax.plot(x, self.regression_line, color='red', linewidth=2,
                     label=f'y = {self.a:.4f} + {self.b:.4f}x', zorder=3)

        self.ax.set_xlabel('x', fontsize=12)
        self.ax.set_ylabel('y', fontsize=12)
        self.ax.set_title('Лінійна регресія методом найменших квадратів',
                          fontsize=12, fontweight='bold')
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)

        self.canvas.draw()

    def clear_results(self):
        """Очищення результатів"""
        self.results_text.delete(1.0, tk.END)
        self.ax.clear()
        self.canvas.draw()
        self.a = None
        self.b = None
        self.regression_line = None
        self.update_status("Результати очищено")

    def save_results(self):
        """Збереження результатів у файл"""
        if self.a is None or self.b is None:
            messagebox.showwarning("Увага", "Спочатку виконайте розрахунок регресії")
            return

        # Вибір файлу для збереження
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Текстові файли", "*.txt"),
                       ("JSON файли", "*.json"),
                       ("Всі файли", "*.*")]
        )

        if not filename:
            return

        try:
            if filename.endswith('.json'):
                # Збереження у JSON
                data = {
                    'x_data': self.x_data,
                    'y_data': self.y_data,
                    'regression': {
                        'a': float(self.a),
                        'b': float(self.b),
                        'equation': f'y = {self.a:.6f} + {self.b:.6f}x'
                    },
                    'regression_values': self.regression_line.tolist()
                }

                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            else:
                # Збереження у текстовий файл
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.results_text.get(1.0, tk.END))
                    f.write("\n\nТаблиця значень:\n")
                    f.write("=" * 50 + "\n")
                    f.write(f"{'№':>5} {'x':>10} {'y':>10} {'y_reg':>10} {'Похибка':>10}\n")
                    f.write("=" * 50 + "\n")

                    for i, (x, y, y_reg) in enumerate(zip(self.x_data, self.y_data,
                                                          self.regression_line), 1):
                        error = y - y_reg
                        f.write(f"{i:>5} {x:>10.2f} {y:>10.4f} {y_reg:>10.4f} "
                                f"{error:>10.6f}\n")

            messagebox.showinfo("Успіх", f"Результати збережено у файл:\n{filename}")
            self.update_status(f"Результати збережено: {filename}")

        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка при збереженні: {str(e)}")


def main():
    root = tk.Tk()
    app = RegressionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()