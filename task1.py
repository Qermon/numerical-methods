import tkinter as tk
from tkinter import ttk, messagebox
import sympy as sp

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


def parse_fx(expr: str):
    x = sp.symbols('x')
    allowed = {
        'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
        'exp': sp.exp, 'log': sp.log, 'sqrt': sp.sqrt,
        'asin': sp.asin, 'acos': sp.acos, 'atan': sp.atan,
        'sinh': sp.sinh, 'cosh': sp.cosh, 'tanh': sp.tanh,
        'abs': sp.Abs, 'pi': sp.pi, 'E': sp.E
    }
    f_expr = sp.sympify(expr, locals=allowed)
    df_expr = sp.diff(f_expr, x)
    f = sp.lambdify(x, f_expr, modules='math')
    df = sp.lambdify(x, df_expr, modules='math')
    return f, df


def bisection(f, a, b, eps, max_iter=10_000):
    fa, fb = f(a), f(b)
    if fa == 0: return a, 0
    if fb == 0: return b, 0
    if fa * fb > 0:
        raise ValueError("На [a,b] немає зміни знаку.")
    it = 0
    while (b - a)/2 > eps and it < max_iter:
        c = (a + b) / 2
        fc = f(c)
        if fc == 0:
            return c, it
        if fa * fc < 0:
            b, fb = c, fc
        else:
            a, fa = c, fc
        it += 1
    return (a + b) / 2, it


def newton(f, df, x0, eps, max_iter=10_000):
    x = float(x0)
    for it in range(1, max_iter+1):
        dfx = df(x)
        if dfx == 0:
            raise ZeroDivisionError("f'(x)=0 в методі Ньютона.")
        x_new = x - f(x)/dfx
        if abs(x_new - x) < eps:
            return x_new, it
        x = x_new
    return x, max_iter


def simple_iterations(f, x0, eps, lam=0.1, max_iter=10_000):
    x = float(x0)
    for it in range(1, max_iter+1):
        x_new = x - lam * f(x)
        if abs(x_new - x) < eps:
            return x_new, it
        x = x_new
    return x, max_iter


# --------- GUI ---------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ЛР1 — Приклад 5: x^2 - sin(5x) = 0")
        self.geometry("980x650")

        # Параметри за замовчуванням під приклад 5
        self.fx = tk.StringVar(value="x**2 - sin(5*x)")
        self.a = tk.StringVar(value="0.5")
        self.b = tk.StringVar(value="0.7")
        self.x0 = tk.StringVar(value="0.6")
        self.lam = tk.StringVar(value="0.1")
        self.eps_list = tk.StringVar(value="0.0001")

        # Діапазон для ГРАФІКА (окремо від [a,b])
        self.pA = tk.StringVar(value="-1.0")
        self.pB = tk.StringVar(value="1.0")

        self.use_bis = tk.BooleanVar(value=True)
        self.use_new = tk.BooleanVar(value=True)
        self.use_it = tk.BooleanVar(value=True)

        self.results = []  # збережемо після "Розв'язати"
        self._build_ui()

    def _build_ui(self):
        frm = ttk.LabelFrame(self, text="Параметри (приклад 5)")
        frm.pack(fill=tk.X, padx=8, pady=6)

        ttk.Label(frm, text="f(x) =").grid(row=0, column=0, sticky="e", padx=4, pady=4)
        ttk.Entry(frm, textvariable=self.fx, width=45).grid(row=0, column=1, columnspan=4, sticky="we", padx=4, pady=4)

        ttk.Label(frm, text="[a, b] =").grid(row=1, column=0, sticky="e", padx=4, pady=4)
        ttk.Entry(frm, textvariable=self.a, width=10).grid(row=1, column=1, sticky="w")
        ttk.Entry(frm, textvariable=self.b, width=10).grid(row=1, column=2, sticky="w")

        ttk.Label(frm, text="x0 =").grid(row=1, column=3, sticky="e")
        ttk.Entry(frm, textvariable=self.x0, width=10).grid(row=1, column=4, sticky="w")

        ttk.Label(frm, text="λ =").grid(row=2, column=0, sticky="e", padx=4, pady=4)
        ttk.Entry(frm, textvariable=self.lam, width=10).grid(row=2, column=1, sticky="w")

        ttk.Label(frm, text="ε (через кому):").grid(row=2, column=2, sticky="e")
        ttk.Entry(frm, textvariable=self.eps_list, width=18).grid(row=2, column=3, sticky="w")

        # Поля для ДІАПАЗОНУ ГРАФІКА
        ttk.Label(frm, text="[pA, pB] для графіка:").grid(row=3, column=0, sticky="e")
        ttk.Entry(frm, textvariable=self.pA, width=10).grid(row=3, column=1, sticky="w")
        ttk.Entry(frm, textvariable=self.pB, width=10).grid(row=3, column=2, sticky="w")

        ttk.Checkbutton(frm, text="Бісекція", variable=self.use_bis).grid(row=4, column=1, padx=4)
        ttk.Checkbutton(frm, text="Ньютон", variable=self.use_new).grid(row=4, column=2, padx=4)
        ttk.Checkbutton(frm, text="Прості ітерації", variable=self.use_it).grid(row=4, column=3, padx=4)

        # Дві кнопки: Розв'язати (без побудови), Побудувати графік
        btns = ttk.Frame(frm)
        btns.grid(row=5, column=0, columnspan=5, pady=6)
        ttk.Button(btns, text="Розв'язати", command=self.solve).pack(side=tk.LEFT, padx=6)
        ttk.Button(btns, text="Побудувати графік", command=self.draw_only).pack(side=tk.LEFT, padx=6)

        paned = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        # Таблиця
        tbl_frame = ttk.LabelFrame(paned, text="Результати")
        self.table = ttk.Treeview(tbl_frame, columns=("m", "eps", "n", "x", "fx"), show="headings", height=18)
        for col, head, w, anchor in [
            ("m", "Метод", 150, "w"),
            ("eps", "ε", 90, "center"),
            ("n", "Ітерацій", 90, "center"),
            ("x", "x*", 200, "e"),
            ("fx", "f(x*)", 200, "e"),
        ]:
            self.table.heading(col, text=head)
            self.table.column(col, width=w, anchor=anchor)
        self.table.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        paned.add(tbl_frame, weight=1)

        # Полотно графіка
        plot_frame = ttk.LabelFrame(paned, text="Графік f(x)")
        self.fig = Figure(figsize=(6, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("f(x)")
        self.ax.grid(True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        paned.add(plot_frame, weight=1)

        self.status = tk.StringVar(value="Готово.")
        ttk.Label(self, textvariable=self.status, relief="sunken", anchor="w").pack(fill=tk.X, padx=0, pady=(0,4))

    def _inputs(self):
        expr = self.fx.get().strip()
        a = float(self.a.get())
        b = float(self.b.get())
        x0 = float(self.x0.get())
        lam = float(self.lam.get())
        eps_vals = [float(e.strip()) for e in self.eps_list.get().split(",") if e.strip()]
        pA = float(self.pA.get())
        pB = float(self.pB.get())
        return expr, a, b, x0, lam, eps_vals, pA, pB

    def solve(self):
        """Розв'язати З БУДЬ-ЯКОЮ ПОБУДОВОЮ ГРАФІКА. Лише заповнює таблицю й зберігає results."""
        for iid in self.table.get_children():
            self.table.delete(iid)
        self.results = []

        try:
            expr, a, b, x0, lam, eps_vals, pA, pB = self._inputs()
            f, df = parse_fx(expr)
        except Exception as e:
            messagebox.showerror("Помилка вводу", str(e))
            return

        for eps in eps_vals:
            if self.use_bis.get():
                try:
                    x_star, n = bisection(f, a, b, eps)
                    self.results.append(("Бісекція", eps, n, x_star, f(x_star)))
                except Exception as e:
                    self.results.append(("Бісекція", eps, "-", "-", f"Помилка: {e}"))
            if self.use_new.get():
                try:
                    x_star, n = newton(f, df, x0, eps)
                    self.results.append(("Ньютон", eps, n, x_star, f(x_star)))
                except Exception as e:
                    self.results.append(("Ньютон", eps, "-", "-", f"Помилка: {e}"))
            if self.use_it.get():
                try:
                    x_star, n = simple_iterations(f, x0, eps, lam)
                    self.results.append(("Прості ітерації", eps, n, x_star, f(x_star)))
                except Exception as e:
                    self.results.append(("Прості ітерації", eps, "-", "-", f"Помилка: {e}"))

        for m, eps, n, x_star, fx in self.results:
            if isinstance(x_star, (int, float)):
                self.table.insert("", tk.END, values=(m, f"{eps:g}", n, f"{x_star:.10g}", f"{fx:.3e}"))
            else:
                self.table.insert("", tk.END, values=(m, f"{eps:g}", n, x_star, fx))

        # НЕ малюємо графік тут!
        self.status.set("Розв'язано. Щоб побудувати графік, натисніть «Побудувати графік».")

    def draw_graph_only(self, f, pA, pB):
        self.ax.clear()
        self.ax.grid(True)
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("f(x)")

        N = 800
        xs = [pA + i*(pB-pA)/N for i in range(N+1)]
        ys = []
        for x in xs:
            try:
                ys.append(f(x))
            except Exception:
                ys.append(float('nan'))
        self.ax.plot(xs, ys, label="f(x)")
        self.ax.axhline(0, linewidth=1)

        if self.results:
            plotted = set()
            for m, eps, n, x_star, fx in self.results:
                if isinstance(x_star, (int, float)):
                    key = round(x_star, 8)
                    if key in plotted:
                        continue
                    plotted.add(key)
                    try:
                        self.ax.plot([x_star], [f(x_star)], marker="o", markersize=6, label=f"{m}, ε={eps:g}")
                    except Exception:
                        pass

        self.ax.legend(loc="best")
        self.canvas.draw()
        self.status.set("Графік оновлено.")

    def draw_only(self):
        """Побудувати графік за полями [pA,pB]. Малює навіть без попередніх обчислень."""
        try:
            f, _ = parse_fx(self.fx.get().strip())
            pA = float(self.pA.get())
            pB = float(self.pB.get())
        except Exception as e:
            messagebox.showerror("Помилка вводу", str(e))
            return
        self.draw_graph_only(f, pA, pB)


if __name__ == "__main__":
    App().mainloop()