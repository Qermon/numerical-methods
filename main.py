import numpy as np
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog, Button, Label

# Поліном Лагранжа
def lagrange_polynomial(x_points, y_points, x):
    n = len(x_points)
    result = 0.0

    for i in range(n):
        term = y_points[i]
        for j in range(n):
            if i != j:
                term *= (x - x_points[j]) / (x_points[i] - x_points[j])
        result += term

    return result


def choose_file():
    Tk().withdraw()
    return filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])


def process_data():
    file_path = choose_file()
    if not file_path:
        return

    data = np.loadtxt(file_path, delimiter=',')
    x_data = data[:, 0]
    y_data = data[:, 1]

    xmin = np.min(x_data)
    xmax = np.max(x_data)

    a = xmin
    b = xmax
    h = (b - a) / 10

    x_nodes = np.array([a + h * i for i in range(11)])
    y_nodes = np.array([lagrange_polynomial(x_data, y_data, xi) for xi in x_nodes])

    # Вивід результатів
    result_text = "Значення у вузлах інтерполяції:\n"
    for i in range(11):
        result_text += f"x{i} = {x_nodes[i]:.3f}, f(x{i}) = {y_nodes[i]:.3f}\n"

    result_label.config(text=result_text)

    # Побудова графіка
    x_plot = np.linspace(xmin, xmax, 400)
    y_plot = [lagrange_polynomial(x_data, y_data, x) for x in x_plot]

    plt.figure()
    plt.plot(x_plot, y_plot, label="Поліном Лагранжа", color="red")
    plt.scatter(x_data, y_data, color="blue", label="Вузли")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.title("Інтерполяція поліномом Лагранжа")
    plt.legend()
    plt.grid(True)
    plt.show()


def exit_program():
    root.quit()
root = Tk()
root.title("Лабораторна робота №4 – Інтерполяція")

Button(root, text="Вибрати файл і побудувати", command=process_data).pack(pady=15)
Button(root, text="Вихід", command=exit_program).pack(pady=5)

result_label = Label(root, text="", justify="left", font=("Courier", 10))
result_label.pack(pady=10)

root.mainloop()
