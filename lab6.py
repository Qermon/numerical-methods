import sys
import math
import csv
from dataclasses import dataclass
from typing import List, Tuple, Dict

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QFileDialog, QGroupBox, QRadioButton, QCheckBox,
    QStatusBar, QTabWidget, QGridLayout, QSplitter
)

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

def f_variant5(x: float, y: float) -> float:
    t = math.tan(x)
    if abs(t) < 1e-12:
        raise ZeroDivisionError("tg(x) близька до 0 — ділення неможливе (x ≈ k*pi).")
    return (1.0 + y) / t


def euler_method(x0: float, y0: float, xn: float, h: float) -> Tuple[np.ndarray, np.ndarray]:
    if h <= 0:
        raise ValueError("Крок h має бути > 0.")
    if xn <= x0:
        raise ValueError("xn має бути більшим за x0.")

    n = int(math.floor((xn - x0) / h))
    xs = [x0]
    ys = [y0]
    x = x0
    y = y0
    for _ in range(n):
        y = y + h * f_variant5(x, y)
        x = x + h
        xs.append(x)
        ys.append(y)

    # Якщо xn не потрапив точно — додаємо останню точку з кроком hx
    if xs[-1] < xn - 1e-12:
        hx = xn - xs[-1]
        x = xs[-1]
        y = ys[-1]
        y = y + hx * f_variant5(x, y)
        xs.append(xn)
        ys.append(y)

    return np.array(xs, dtype=float), np.array(ys, dtype=float)


def rk4_method(x0: float, y0: float, xn: float, h: float) -> Tuple[np.ndarray, np.ndarray]:
    if h <= 0:
        raise ValueError("Крок h має бути > 0.")
    if xn <= x0:
        raise ValueError("xn має бути більшим за x0.")

    n = int(math.floor((xn - x0) / h))
    xs = [x0]
    ys = [y0]
    x = x0
    y = y0

    for _ in range(n):
        k1 = f_variant5(x, y)
        k2 = f_variant5(x + h / 2.0, y + h * k1 / 2.0)
        k3 = f_variant5(x + h / 2.0, y + h * k2 / 2.0)
        k4 = f_variant5(x + h, y + h * k3)

        y = y + (h / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
        x = x + h

        xs.append(x)
        ys.append(y)

    if xs[-1] < xn - 1e-12:
        hx = xn - xs[-1]
        x = xs[-1]
        y = ys[-1]

        k1 = f_variant5(x, y)
        k2 = f_variant5(x + hx / 2.0, y + hx * k1 / 2.0)
        k3 = f_variant5(x + hx / 2.0, y + hx * k2 / 2.0)
        k4 = f_variant5(x + hx, y + hx * k3)
        y = y + (hx / 6.0) * (k1 + 2*k2 + 2*k3 + k4)

        xs.append(xn)
        ys.append(y)

    return np.array(xs, dtype=float), np.array(ys, dtype=float)


def validate_domain(x0: float, xn: float) -> None:
    """
    Обережність для tg(x): проблема при x = k*pi (tg=0) та дуже близько до них.
    Перевірка груба: дивимося чи інтервал не перетинає близько до k*pi.
    """
    eps = 1e-3  # можна змінити, якщо потрібно
    k_start = math.floor(x0 / math.pi) - 1
    k_end = math.ceil(xn / math.pi) + 1
    for k in range(k_start, k_end + 1):
        x_bad = k * math.pi
        if x0 - eps <= x_bad <= xn + eps:
            raise ValueError(
                f"Інтервал [{x0}, {xn}] проходить близько до x = {k}*pi = {x_bad:.6f}, де tg(x)=0.\n"
                f"Змініть x0/xn, щоб не потрапляти в околиці k*pi."
            )


@dataclass
class SeriesResult:
    label: str
    xs: np.ndarray
    ys: np.ndarray


class MplCanvas(FigureCanvas):
    def __init__(self):
        self.fig = plt.Figure()
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)


class ODELab6App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лабораторна робота №6 — Чисельне розв'язування ДР (Варіант 5)")
        self.setMinimumSize(1200, 750)

        self.results: Dict[str, SeriesResult] = {}

        self._build_ui()

    def _build_ui(self):
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Готово")

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)

        title = QLabel("Лабораторна робота №6: Чисельне розв'язування ДР\nВаріант 5:  y' = (1 + y) / tg(x)")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: 700; padding: 8px;")
        main_layout.addWidget(title)

        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter, 1)

        left = QWidget()
        left_layout = QVBoxLayout(left)

        gb_inputs = QGroupBox("Введення початкових даних")
        grid = QGridLayout(gb_inputs)

        self.x0_edit = QLineEdit("0.5")
        self.xn_edit = QLineEdit("2.5")
        self.y0_edit = QLineEdit("1.0")

        for w, tip in [
            (self.x0_edit, "Введіть x₀ (початок інтервалу)"),
            (self.xn_edit, "Введіть xₙ (кінець інтервалу)"),
            (self.y0_edit, "Введіть y₀ (початкова умова y(x₀)=y₀)"),
        ]:
            w.setToolTip(tip)

        grid.addWidget(QLabel("x₀:"), 0, 0)
        grid.addWidget(self.x0_edit, 0, 1)
        grid.addWidget(QLabel("xₙ:"), 1, 0)
        grid.addWidget(self.xn_edit, 1, 1)
        grid.addWidget(QLabel("y₀:"), 2, 0)
        grid.addWidget(self.y0_edit, 2, 1)

        left_layout.addWidget(gb_inputs)

        gb_methods = QGroupBox("Методи")
        v_methods = QVBoxLayout(gb_methods)
        self.cb_euler = QCheckBox("Ейлера")
        self.cb_rk4 = QCheckBox("Рунге–Кутта 4")
        self.cb_euler.setChecked(True)
        self.cb_rk4.setChecked(True)
        self.cb_euler.setToolTip("Виконати метод Ейлера")
        self.cb_rk4.setToolTip("Виконати метод Рунге–Кутта 4-го порядку")
        v_methods.addWidget(self.cb_euler)
        v_methods.addWidget(self.cb_rk4)
        left_layout.addWidget(gb_methods)

        gb_steps = QGroupBox("Кроки диференціювання")
        v_steps = QVBoxLayout(gb_steps)
        self.cb_h01 = QCheckBox("h = 0.1")
        self.cb_h02 = QCheckBox("h = 0.2")
        self.cb_h01.setChecked(True)
        self.cb_h02.setChecked(True)
        self.cb_h01.setToolTip("Рахувати з кроком 0.1")
        self.cb_h02.setToolTip("Рахувати з кроком 0.2")
        v_steps.addWidget(self.cb_h01)
        v_steps.addWidget(self.cb_h02)
        left_layout.addWidget(gb_steps)

        btn_row = QHBoxLayout()
        self.btn_calc = QPushButton("Розрахувати")
        self.btn_plot = QPushButton("Побудувати графік")
        self.btn_save = QPushButton("Зберегти CSV")
        self.btn_clear = QPushButton("Очистити")

        self.btn_calc.setToolTip("Виконати обчислення та заповнити таблиці")
        self.btn_plot.setToolTip("Побудувати графік для розрахованих серій")
        self.btn_save.setToolTip("Зберегти результати у CSV-файл")
        self.btn_clear.setToolTip("Очистити таблиці та графік")

        self.btn_calc.clicked.connect(self.on_calculate)
        self.btn_plot.clicked.connect(self.on_plot)
        self.btn_save.clicked.connect(self.on_save_csv)
        self.btn_clear.clicked.connect(self.on_clear)

        btn_row.addWidget(self.btn_calc)
        btn_row.addWidget(self.btn_plot)
        btn_row.addWidget(self.btn_save)
        btn_row.addWidget(self.btn_clear)
        left_layout.addLayout(btn_row)

        left_layout.addStretch(1)
        splitter.addWidget(left)

        # ---------------- Right: Tabs (Tables + Plot) ----------------
        right = QWidget()
        right_layout = QVBoxLayout(right)

        self.tabs = QTabWidget()

        # Таблиці: окремо для h=0.1 та h=0.2
        self.table_h01 = QTableWidget()
        self.table_h02 = QTableWidget()
        self._setup_table(self.table_h01)
        self._setup_table(self.table_h02)

        tab1 = QWidget()
        tab1_layout = QVBoxLayout(tab1)
        tab1_layout.addWidget(QLabel("Результати для h = 0.1"))
        tab1_layout.addWidget(self.table_h01)

        tab2 = QWidget()
        tab2_layout = QVBoxLayout(tab2)
        tab2_layout.addWidget(QLabel("Результати для h = 0.2"))
        tab2_layout.addWidget(self.table_h02)

        self.tabs.addTab(tab1, "Таблиця (h=0.1)")
        self.tabs.addTab(tab2, "Таблиця (h=0.2)")

        # Графік
        plot_tab = QWidget()
        plot_layout = QVBoxLayout(plot_tab)
        self.canvas = MplCanvas()
        plot_layout.addWidget(self.canvas)
        self.tabs.addTab(plot_tab, "Графік")

        right_layout.addWidget(self.tabs, 1)
        splitter.addWidget(right)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

    def _setup_table(self, table: QTableWidget):
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["i", "xᵢ", "y (Euler)", "y (RK4)"])
        table.setToolTip("Табличне представлення результатів (x, y)")

    def _read_inputs(self) -> Tuple[float, float, float]:
        try:
            x0 = float(self.x0_edit.text().strip().replace(",", "."))
            xn = float(self.xn_edit.text().strip().replace(",", "."))
            y0 = float(self.y0_edit.text().strip().replace(",", "."))
        except ValueError:
            raise ValueError("Помилка введення: x0, xn, y0 мають бути числами.")
        validate_domain(x0, xn)
        if xn <= x0:
            raise ValueError("xn має бути більшим за x0.")
        return x0, xn, y0

    def _selected_steps(self) -> List[float]:
        steps = []
        if self.cb_h01.isChecked():
            steps.append(0.1)
        if self.cb_h02.isChecked():
            steps.append(0.2)
        if not steps:
            raise ValueError("Оберіть хоча б один крок (h=0.1 або h=0.2).")
        return steps

    def _selected_methods(self) -> Tuple[bool, bool]:
        use_euler = self.cb_euler.isChecked()
        use_rk4 = self.cb_rk4.isChecked()
        if not (use_euler or use_rk4):
            raise ValueError("Оберіть хоча б один метод (Ейлера або Рунге–Кутта 4).")
        return use_euler, use_rk4

    def on_calculate(self):
        try:
            x0, xn, y0 = self._read_inputs()
            steps = self._selected_steps()
            use_euler, use_rk4 = self._selected_methods()
        except Exception as e:
            QMessageBox.critical(self, "Помилка", str(e))
            self.status.showMessage("Помилка введення/налаштувань")
            return

        self.results.clear()
        self.table_h01.setRowCount(0)
        self.table_h02.setRowCount(0)

        try:
            for h in steps:
                e_xs = e_ys = r_xs = r_ys = None

                if use_euler:
                    e_xs, e_ys = euler_method(x0, y0, xn, h)
                    self.results[f"Euler h={h}"] = SeriesResult(f"Euler (h={h})", e_xs, e_ys)

                if use_rk4:
                    r_xs, r_ys = rk4_method(x0, y0, xn, h)
                    self.results[f"RK4 h={h}"] = SeriesResult(f"RK4 (h={h})", r_xs, r_ys)

                # Заповнення таблиці для цього h
                table = self.table_h01 if abs(h - 0.1) < 1e-12 else self.table_h02 if abs(h - 0.2) < 1e-12 else None
                if table is not None:
                    self._fill_table(table, e_xs, e_ys, r_xs, r_ys)

        except Exception as e:
            QMessageBox.critical(self, "Помилка обчислень", str(e))
            self.status.showMessage("Помилка обчислень")
            return

        self.status.showMessage("Розрахунок виконано. Можна будувати графік або зберігати CSV.")
        QMessageBox.information(self, "Готово", "Розрахунок виконано. Перейдіть на вкладку графіка або збережіть CSV.")

    def _fill_table(self, table: QTableWidget,
                    e_xs: np.ndarray, e_ys: np.ndarray,
                    r_xs: np.ndarray, r_ys: np.ndarray):
        # Вирівнюємо по довжині: беремо максимальну кількість точок
        rows = 0
        if e_xs is not None:
            rows = max(rows, len(e_xs))
        if r_xs is not None:
            rows = max(rows, len(r_xs))

        table.setRowCount(rows)

        for i in range(rows):
            # x беремо або з Euler, або з RK4 (якщо один метод вимкнений)
            x_val = None
            if e_xs is not None and i < len(e_xs):
                x_val = e_xs[i]
            elif r_xs is not None and i < len(r_xs):
                x_val = r_xs[i]

            def item(text: str) -> QTableWidgetItem:
                it = QTableWidgetItem(text)
                it.setTextAlignment(Qt.AlignCenter)
                return it

            table.setItem(i, 0, item(str(i)))
            table.setItem(i, 1, item("" if x_val is None else f"{x_val:.6f}"))

            if e_ys is not None and i < len(e_ys):
                table.setItem(i, 2, item(f"{e_ys[i]:.6f}"))
            else:
                table.setItem(i, 2, item(""))

            if r_ys is not None and i < len(r_ys):
                table.setItem(i, 3, item(f"{r_ys[i]:.6f}"))
            else:
                table.setItem(i, 3, item(""))

        table.resizeColumnsToContents()

    def on_plot(self):
        if not self.results:
            QMessageBox.warning(self, "Немає даних", "Спочатку натисніть «Розрахувати».")
            self.status.showMessage("Немає даних для графіка")
            return

        ax = self.canvas.ax
        ax.clear()

        # Малюємо всі серії, що є
        for key, series in self.results.items():
            ax.plot(series.xs, series.ys, label=series.label)

        ax.set_title("Чисельний розв'язок: y' = (1 + y) / tg(x)")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.grid(True)
        ax.legend()

        self.canvas.draw()
        self.tabs.setCurrentIndex(2)  # вкладка графіка
        self.status.showMessage("Графік побудовано")

    def on_save_csv(self):
        if not self.results:
            QMessageBox.warning(self, "Немає даних", "Немає результатів для збереження. Спочатку натисніть «Розрахувати».")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Зберегти результати", "results_variant5.csv", "CSV files (*.csv)"
        )
        if not path:
            return

        # Об’єднаємо дані в один CSV:
        # columns: series_name, i, x, y
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(["series", "i", "x", "y"])

                for key, series in self.results.items():
                    for i in range(len(series.xs)):
                        writer.writerow([series.label, i, f"{series.xs[i]:.10f}", f"{series.ys[i]:.10f}"])

        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося зберегти файл:\n{e}")
            return

        QMessageBox.information(self, "Збережено", f"Результати збережено у файл:\n{path}")
        self.status.showMessage("CSV збережено")

    def on_clear(self):
        self.results.clear()
        self.table_h01.setRowCount(0)
        self.table_h02.setRowCount(0)
        self.canvas.ax.clear()
        self.canvas.draw()
        self.status.showMessage("Очищено")


def main():
    app = QApplication(sys.argv)
    win = ODELab6App()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
