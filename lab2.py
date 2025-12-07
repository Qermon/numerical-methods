import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QTableWidget, QTableWidgetItem, QComboBox,
                             QStatusBar, QMessageBox, QFileDialog, QTabWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import pandas as pd


class NumericalIntegrationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Лабораторна робота 2: Чисельні методи обчислення інтегралів')
        self.setGeometry(100, 100, 1200, 800)

        # Створення статусного рядка
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage('Готово до роботи')

        # Центральний віджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Основний layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Заголовок
        title_label = QLabel('Обчислення визначених інтегралів чисельними методами')
        title_label.setStyleSheet('font-size: 16pt; font-weight: bold; color: #2c3e50;')
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Вибір функції
        function_layout = QHBoxLayout()
        function_label = QLabel('Оберіть функцію:')
        self.function_combo = QComboBox()
        self.function_combo.addItems([
            '№5: 1) dx/√(2x+3)',
            '№5: 2) √x·cos(x²)·dx',
            '№5: 3) dx/√(3x²-0.4)'
        ])
        self.function_combo.currentIndexChanged.connect(self.update_status)
        function_layout.addWidget(function_label)
        function_layout.addWidget(self.function_combo)
        function_layout.addStretch()
        main_layout.addLayout(function_layout)

        # Введення меж інтегрування
        limits_layout = QHBoxLayout()

        self.lower_limit_label = QLabel('Нижня межа (a):')
        self.lower_limit_input = QLineEdit()
        self.lower_limit_input.setText('0.8')
        self.lower_limit_input.textChanged.connect(lambda: self.update_status_hint('Введіть нижню межу інтегрування'))

        self.upper_limit_label = QLabel('Верхня межа (b):')
        self.upper_limit_input = QLineEdit()
        self.upper_limit_input.setText('1.4')
        self.upper_limit_input.textChanged.connect(lambda: self.update_status_hint('Введіть верхню межу інтегрування'))

        limits_layout.addWidget(self.lower_limit_label)
        limits_layout.addWidget(self.lower_limit_input)
        limits_layout.addWidget(self.upper_limit_label)
        limits_layout.addWidget(self.upper_limit_input)
        limits_layout.addStretch()
        main_layout.addLayout(limits_layout)

        # Кнопки керування
        buttons_layout = QHBoxLayout()

        self.calculate_btn = QPushButton('Обчислити інтеграл')
        self.calculate_btn.clicked.connect(self.calculate_integrals)
        self.calculate_btn.setStyleSheet('background-color: #3498db; color: white; padding: 10px; font-size: 12pt;')
        self.calculate_btn.enterEvent = lambda e: self.statusBar.showMessage('Розрахувати інтеграл всіма методами')

        self.save_btn = QPushButton('Зберегти результати')
        self.save_btn.clicked.connect(self.save_results)
        self.save_btn.setStyleSheet('background-color: #2ecc71; color: white; padding: 10px; font-size: 12pt;')
        self.save_btn.enterEvent = lambda e: self.statusBar.showMessage('Зберегти результати у файл')

        self.clear_btn = QPushButton('Очистити')
        self.clear_btn.clicked.connect(self.clear_results)
        self.clear_btn.setStyleSheet('background-color: #e74c3c; color: white; padding: 10px; font-size: 12pt;')
        self.clear_btn.enterEvent = lambda e: self.statusBar.showMessage('Очистити всі результати')

        buttons_layout.addWidget(self.calculate_btn)
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.clear_btn)
        main_layout.addLayout(buttons_layout)

        # Табуляція для результатів
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Вкладка з таблицею
        table_widget = QWidget()
        table_layout = QVBoxLayout()
        table_widget.setLayout(table_layout)

        # Таблиця результатів
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels(['N', 'Аналіт. значення',
                                                      'Метод прямокутників',
                                                      'Метод трапецій',
                                                      'Метод Монте-Карло'])
        self.results_table.setRowCount(5)

        # Заповнення значень N
        n_values = [10, 20, 50, 100, 1000]
        for i, n in enumerate(n_values):
            self.results_table.setItem(i, 0, QTableWidgetItem(str(n)))

        table_layout.addWidget(QLabel('Результати розрахунку:'))
        table_layout.addWidget(self.results_table)
        self.tabs.addTab(table_widget, "Таблиця результатів")

        # Вкладка з графіком
        graph_widget = QWidget()
        graph_layout = QVBoxLayout()
        graph_widget.setLayout(graph_layout)

        self.figure = plt.figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        graph_layout.addWidget(self.canvas)
        self.tabs.addTab(graph_widget, "Графік")

        self.results_data = []

    def update_status(self):
        self.statusBar.showMessage(f'Обрана функція: {self.function_combo.currentText()}')

    def update_status_hint(self, hint):
        self.statusBar.showMessage(hint)

    def get_function(self, choice):
        """Повертає функцію для інтегрування"""
        if choice == 0:  # dx/√(2x+3)
            return lambda x: 1 / np.sqrt(2 * x + 3)
        elif choice == 1:  # √x·cos(x²)·dx
            return lambda x: np.sqrt(x) * np.cos(x ** 2)
        elif choice == 2:  # dx/√(3x²-0.4)
            return lambda x: 1 / np.sqrt(3 * x ** 2 - 0.4)

    def analytical_integral(self, choice, a, b):
        """Обчислює аналітичне значення інтегралу"""
        if choice == 0:  # ∫dx/√(2x+3) = √(2x+3)
            return np.sqrt(2 * b + 3) - np.sqrt(2 * a + 3)
        else:
            # Для інших функцій використовуємо чисельне значення з високою точністю
            from scipy import integrate
            func = self.get_function(choice)
            result, _ = integrate.quad(func, a, b)
            return result

    def rectangle_method(self, func, a, b, n):
        """Метод прямокутників (середніх точок)"""
        h = (b - a) / n
        result = 0
        for i in range(n):
            x_mid = a + (i + 0.5) * h
            result += func(x_mid)
        return result * h

    def trapezoid_method(self, func, a, b, n):
        """Метод трапецій"""
        h = (b - a) / n
        result = (func(a) + func(b)) / 2
        for i in range(1, n):
            result += func(a + i * h)
        return result * h

    def monte_carlo_method(self, func, a, b, n):
        """Метод Монте-Карло"""
        x_random = np.random.uniform(a, b, n)
        y_values = func(x_random)
        return (b - a) * np.mean(y_values)

    def calculate_integrals(self):
        try:
            # Отримання параметрів
            a = float(self.lower_limit_input.text())
            b = float(self.upper_limit_input.text())
            choice = self.function_combo.currentIndex()

            if a >= b:
                QMessageBox.warning(self, 'Помилка', 'Нижня межа повинна бути менше верхньої!')
                return

            # Перевірка допустимості меж для функції
            if choice == 0 and a < -1.5:
                QMessageBox.warning(self, 'Помилка', 'Для функції №1 потрібно x > -1.5')
                return
            if choice == 2 and abs(a) < np.sqrt(0.4 / 3):
                QMessageBox.warning(self, 'Помилка', 'Для функції №3 потрібно |x| > √(0.4/3) ≈ 0.365')
                return

            func = self.get_function(choice)
            analytical = self.analytical_integral(choice, a, b)

            n_values = [10, 20, 50, 100, 1000]
            self.results_data = []

            for i, n in enumerate(n_values):
                rect = self.rectangle_method(func, a, b, n)
                trap = self.trapezoid_method(func, a, b, n)
                mc = self.monte_carlo_method(func, a, b, n)

                self.results_table.setItem(i, 1, QTableWidgetItem(f'{analytical:.8f}'))
                self.results_table.setItem(i, 2, QTableWidgetItem(f'{rect:.8f}'))
                self.results_table.setItem(i, 3, QTableWidgetItem(f'{trap:.8f}'))
                self.results_table.setItem(i, 4, QTableWidgetItem(f'{mc:.8f}'))

                self.results_data.append({
                    'N': n,
                    'Аналітичне': analytical,
                    'Прямокутники': rect,
                    'Трапеції': trap,
                    'Монте-Карло': mc,
                    'Похибка_прямокутники': abs(rect - analytical),
                    'Похибка_трапеції': abs(trap - analytical),
                    'Похибка_МК': abs(mc - analytical)
                })

            self.plot_results()
            self.statusBar.showMessage('Розрахунок завершено успішно!')

        except ValueError:
            QMessageBox.warning(self, 'Помилка', 'Введіть коректні числові значення!')
        except Exception as e:
            QMessageBox.critical(self, 'Помилка', f'Виникла помилка: {str(e)}')

    def plot_results(self):
        """Побудова графіків"""
        self.figure.clear()

        if not self.results_data:
            return

        n_values = [d['N'] for d in self.results_data]
        errors_rect = [d['Похибка_прямокутники'] for d in self.results_data]
        errors_trap = [d['Похибка_трапеції'] for d in self.results_data]
        errors_mc = [d['Похибка_МК'] for d in self.results_data]

        # Графік похибок
        ax1 = self.figure.add_subplot(121)
        ax1.plot(n_values, errors_rect, 'o-', label='Прямокутники', linewidth=2)
        ax1.plot(n_values, errors_trap, 's-', label='Трапеції', linewidth=2)
        ax1.plot(n_values, errors_mc, '^-', label='Монте-Карло', linewidth=2)
        ax1.set_xlabel('Кількість розбиттів (N)')
        ax1.set_ylabel('Абсолютна похибка')
        ax1.set_title('Залежність похибки від N')
        ax1.set_xscale('log')
        ax1.set_yscale('log')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Графік значень інтегралу
        ax2 = self.figure.add_subplot(122)
        analytical = self.results_data[0]['Аналітичне']
        values_rect = [d['Прямокутники'] for d in self.results_data]
        values_trap = [d['Трапеції'] for d in self.results_data]
        values_mc = [d['Монте-Карло'] for d in self.results_data]

        ax2.axhline(y=analytical, color='r', linestyle='--', label='Аналітичне значення', linewidth=2)
        ax2.plot(n_values, values_rect, 'o-', label='Прямокутники', linewidth=2)
        ax2.plot(n_values, values_trap, 's-', label='Трапеції', linewidth=2)
        ax2.plot(n_values, values_mc, '^-', label='Монте-Карло', linewidth=2)
        ax2.set_xlabel('Кількість розбиттів (N)')
        ax2.set_ylabel('Значення інтегралу')
        ax2.set_title('Збіжність методів')
        ax2.set_xscale('log')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        self.figure.tight_layout()
        self.canvas.draw()

    def save_results(self):
        """Збереження результатів у файл"""
        if not self.results_data:
            QMessageBox.warning(self, 'Помилка', 'Немає результатів для збереження!')
            return

        filename, _ = QFileDialog.getSaveFileName(self, 'Зберегти результати', '',
                                                  'Excel файли (*.xlsx);;CSV файли (*.csv);;Всі файли (*)')

        if filename:
            try:
                df = pd.DataFrame(self.results_data)

                if filename.endswith('.xlsx'):
                    df.to_excel(filename, index=False)
                else:
                    df.to_csv(filename, index=False)

                self.statusBar.showMessage(f'Результати збережено: {filename}')
                QMessageBox.information(self, 'Успіх', f'Результати успішно збережено в {filename}')
            except Exception as e:
                QMessageBox.critical(self, 'Помилка', f'Не вдалося зберегти файл: {str(e)}')

    def clear_results(self):
        """Очищення результатів"""
        for i in range(5):
            for j in range(1, 5):
                self.results_table.setItem(i, j, QTableWidgetItem(''))

        self.results_data = []
        self.figure.clear()
        self.canvas.draw()
        self.statusBar.showMessage('Результати очищено')


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = NumericalIntegrationApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()