import random
import string
import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор случайных паролей")
        self.root.geometry("700x500")
        self.root.resizable(False, False)

        # Файл для хранения истории
        self.history_file = "password_history.json"
        self.history = self.load_history()

        # Переменные для виджетов
        self.password_length = tk.IntVar(value=12)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_letters = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=True)

        # Создание интерфейса
        self.create_widgets()
        self.update_history_table()

        # Обработка закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        # Рамка настроек
        settings_frame = ttk.LabelFrame(self.root, text="Настройки пароля", padding=10)
        settings_frame.pack(fill="x", padx=10, pady=5)

        # Ползунок длины пароля
        ttk.Label(settings_frame, text="Длина пароля:").grid(row=0, column=0, sticky="w", pady=5)
        self.length_scale = ttk.Scale(settings_frame, from_=4, to=32, variable=self.password_length,
                                      orient="horizontal", command=self.update_length_label)
        self.length_scale.grid(row=0, column=1, padx=10, sticky="ew")
        self.length_label = ttk.Label(settings_frame, text=f"{self.password_length.get()}")
        self.length_label.grid(row=0, column=2, padx=5)

        # Чекбоксы
        ttk.Checkbutton(settings_frame, text="Цифры (0-9)", variable=self.use_digits).grid(row=1, column=0, sticky="w", pady=5)
        ttk.Checkbutton(settings_frame, text="Буквы (A-Z, a-z)", variable=self.use_letters).grid(row=1, column=1, sticky="w", pady=5)
        ttk.Checkbutton(settings_frame, text="Спецсимволы (!@#$%^&* и т.д.)", variable=self.use_symbols).grid(row=1, column=2, sticky="w", pady=5)

        # Кнопка генерации
        ttk.Button(settings_frame, text="Сгенерировать пароль", command=self.generate_password).grid(row=2, column=0, columnspan=3, pady=10)

        # Рамка для отображения сгенерированного пароля
        result_frame = ttk.LabelFrame(self.root, text="Сгенерированный пароль", padding=10)
        result_frame.pack(fill="x", padx=10, pady=5)

        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(result_frame, textvariable=self.password_var, font=("Courier", 12), state="readonly")
        self.password_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ttk.Button(result_frame, text="Копировать", command=self.copy_to_clipboard).pack(side="right")

        # Таблица истории
        history_frame = ttk.LabelFrame(self.root, text="История паролей", padding=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("timestamp", "password")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=10)
        self.history_tree.heading("timestamp", text="Дата и время")
        self.history_tree.heading("password", text="Пароль")
        self.history_tree.column("timestamp", width=150)
        self.history_tree.column("password", width=300)
        self.history_tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.history_tree.configure(yscrollcommand=scrollbar.set)

        # Кнопки управления историей
        buttons_frame = ttk.Frame(history_frame)
        buttons_frame.pack(side="bottom", fill="x", pady=5)
        ttk.Button(buttons_frame, text="Очистить историю", command=self.clear_history).pack(side="right", padx=5)

    def update_length_label(self, event=None):
        self.length_label.config(text=f"{int(self.password_length.get())}")

    def generate_password(self):
        # Проверка, что выбран хотя бы один тип символов
        if not (self.use_digits.get() or self.use_letters.get() or self.use_symbols.get()):
            messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов!")
            return

        length = int(self.password_length.get())
        # Минимальная и максимальная длина уже заданы ползунком, но на всякий случай проверим
        if length < 4:
            length = 4
            self.password_length.set(4)
            self.update_length_label()
        elif length > 32:
            length = 32
            self.password_length.set(32)
            self.update_length_label()

        # Формируем пул символов
        chars = ""
        if self.use_digits.get():
            chars += string.digits
        if self.use_letters.get():
            chars += string.ascii_letters
        if self.use_symbols.get():
            chars += string.punctuation  # стандартные спецсимволы

        # Генерация пароля
        password = ''.join(random.choice(chars) for _ in range(length))

        # Отображение пароля
        self.password_var.set(password)

        # Сохранение в историю
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.append({"timestamp": timestamp, "password": password})
        self.update_history_table()
        self.save_history()

    def copy_to_clipboard(self):
        password = self.password_var.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Копирование", "Пароль скопирован в буфер обмена!")
        else:
            messagebox.showwarning("Внимание", "Нет сгенерированного пароля для копирования.")

    def update_history_table(self):
        # Очищаем таблицу
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        # Заполняем историю (от новых к старым)
        for entry in reversed(self.history):
            self.history_tree.insert("", "end", values=(entry["timestamp"], entry["password"]))

    def clear_history(self):
        if messagebox.askyesno("Очистка истории", "Вы уверены, что хотите удалить всю историю паролей?"):
            self.history.clear()
            self.update_history_table()
            self.save_history()

    def save_history(self):
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {e}")

    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить историю: {e}")
                return []
        return []

    def on_closing(self):
        self.save_history()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()

