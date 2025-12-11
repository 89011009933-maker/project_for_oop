import sys
import sqlite3
from PyQt5 import QtWidgets, QtCore, QtGui


class Database:
    def __init__(self):
        self.conn = sqlite3.connect('configurations.db')
        self.cursor = self.conn.cursor()
        self.init_db()

    def init_db(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT DEFAULT "user"
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS saved_configurations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                configuration TEXT,
                is_approved INTEGER DEFAULT 0,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        self.conn.commit()

        # Добавляем администратора
        self.cursor.execute('''
            INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)
        ''', ('admin', 'admin123', 'admin'))
        self.conn.commit()

    def register_user(self, username, password):
        try:
            self.cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def authenticate_user(self, username, password):
        self.cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        return self.cursor.fetchone()

    def save_configuration(self, user_id, configuration):
        try:
            self.cursor.execute('INSERT INTO saved_configurations (user_id, configuration) VALUES (?, ?)', (user_id, configuration))
            self.conn.commit()
        except Exception as e:
            print(f"Ошибка при сохранении конфигурации: {e}")

    def view_saved_configurations(self, user_id):
        self.cursor.execute('SELECT configuration FROM saved_configurations WHERE user_id = ?', (user_id,))
        return self.cursor.fetchall()

    def view_all_configurations(self):
        self.cursor.execute('''
            SELECT users.username, saved_configurations.configuration
            FROM saved_configurations
            JOIN users ON saved_configurations.user_id = users.id
        ''')
        return self.cursor.fetchall()

    def view_all_configurations_for_edit(self):
        self.cursor.execute('''
            SELECT id, users.username, saved_configurations.configuration
            FROM saved_configurations
            JOIN users ON saved_configurations.user_id = users.id
        ''')
        return self.cursor.fetchall()

    def edit_configuration(self, config_id, new_configuration):
        try:
            self.cursor.execute('''
                UPDATE saved_configurations
                SET configuration = ?
                WHERE id = ?
            ''', (new_configuration, config_id))
            self.conn.commit()
        except Exception as e:
            print(f"Ошибка при редактировании конфигурации: {e}")

    def close(self):
        self.conn.close()


class BaseWindow(QtWidgets.QWidget):
    def __init__(self, title):
        super().__init__()
        self.setWindowTitle(title)
        self.setWindowIcon(QtGui.QIcon("full kursovoi/icon.ico"))  # Устанавливаем иконку
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowMaximizeButtonHint)
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2c3e50, stop:1 #34495e);
                color: #ecf0f1;
                font-family: "Segoe UI", sans-serif;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3498db, stop:1 #2980b9);
                color: #ecf0f1;
                border-radius: 10px;
                padding: 15px;
                font-size: 16px;
                min-width: 200px;
                max-width: 200px;
                min-height: 50px;
                max-height: 50px;
                border: 2px solid #2980b9;
                box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);
                text-align: center;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2980b9, stop:1 #3498db);
                border: 2px solid #3498db;
                box-shadow: 0px 6px 8px rgba(0, 0, 0, 0.3);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2980b9, stop:1 #3498db);
                border: 2px solid #3498db;
                box-shadow: inset 0px 4px 6px rgba(0, 0, 0, 0.2);
            }
            QLineEdit {
                background-color: #34495e;
                color: #ecf0f1;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                border: 1px solid #2c3e50;
                box-shadow: inset 0px 2px 4px rgba(0, 0, 0, 0.2);
                max-width: 200px; /* Уменьшаем ширину полей ввода */
            }
            QLabel {
                color: #ecf0f1;
                font-size: 16px;
                font-weight: bold;
            }
            QMessageBox {
                background-color: #34495e;
                color: #ecf0f1;
                border-radius: 10px;
                padding: 20px;
            }
            QMessageBox QLabel {
                color: #ecf0f1;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3498db, stop:1 #2980b9);
                color: #ecf0f1;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                border: 1px solid #2980b9;
                box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.2);
            }
            QMessageBox QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2980b9, stop:1 #3498db);
                border: 1px solid #3498db;
                box-shadow: 0px 3px 5px rgba(0, 0, 0, 0.3);
            }
            QMessageBox QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2980b9, stop:1 #3498db);
                border: 1px solid #3498db;
                box-shadow: inset 0px 2px 4px rgba(0, 0, 0, 0.2);
            }
            QListWidget {
                background-color: #34495e;
                color: #ecf0f1;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                border: 1px solid #2c3e50;
                box-shadow: inset 0px 2px 4px rgba(0, 0, 0, 0.2);
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #2c3e50;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: #ecf0f1;
            }
        """)

        # Кнопка "Закрыть"
        self.close_button = QtWidgets.QPushButton("Закрыть", self)
        self.close_button.clicked.connect(self.close)

        # Основной макет
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.close_button)

    def showEvent(self, event):
        # Показываем окно на весь экран
        self.showFullScreen()
        super().showEvent(event)


class MainWindow(BaseWindow):
    def __init__(self):
        super().__init__("Конфигурации ПК РАНХиГС")
        self.db = Database()

        # Добавляем надпись "Конфигуратор ПК РАНХиГС"
        self.title_label = QtWidgets.QLabel("Конфигуратор ПК РАНХиГС", self)
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)  # Выравниваем по центру
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")  # Увеличиваем размер и жирность текста

        # Поля для ввода данных
        self.username_input = QtWidgets.QLineEdit(self)
        self.password_input = QtWidgets.QLineEdit(self)
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)

        # Кнопки
        self.register_button = QtWidgets.QPushButton("Регистрация", self)
        self.login_button = QtWidgets.QPushButton("Вход", self)

        self.register_button.clicked.connect(self.register)
        self.login_button.clicked.connect(self.login)

        # Макет для полей и кнопок
        layout = QtWidgets.QVBoxLayout(self)

        # Добавляем надпись в макет
        layout.addWidget(self.title_label)

        # Группируем поля ввода вместе
        input_layout = QtWidgets.QHBoxLayout()
        input_layout.addWidget(QtWidgets.QLabel("Имя пользователя:"))
        input_layout.addWidget(self.username_input)
        input_layout.addWidget(QtWidgets.QLabel("Пароль:"))
        input_layout.addWidget(self.password_input)
        layout.addLayout(input_layout)

        # Кнопки регистрации и входа
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.register_button)
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.close_button)  # Добавляем кнопку "Закрыть" справа
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Добавляем кнопку "Закрыть" внизу
        layout.addWidget(self.close_button)

        self.layout.addLayout(layout)

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if self.db.register_user(username, password):
            QtWidgets.QMessageBox.information(self, "Успех", "Регистрация успешна!")
        else:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Ошибка: имя пользователя уже существует.")

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        user = self.db.authenticate_user(username, password)
        if user is None:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Ошибка: неверные учетные данные.")
        else:
            user_id = user[0]
            user_role = user[3]  # Роль пользователя ('user' или 'admin')
            if user_role == 'admin':
                self.admin_panel()  # Переход на панель администратора
            else:
                self.select_build_type(user_id)

    def admin_panel(self):
        # Кнопка для просмотра всех конфигураций
        view_all_button = QtWidgets.QPushButton("Просмотреть все конфигурации", self)
        view_all_button.clicked.connect(self.view_all_configurations_for_edit)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(view_all_button)
        self.setLayout(layout)

    def view_all_configurations_for_edit(self):
        configurations = self.db.view_all_configurations_for_edit()
        if configurations:
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("Редактирование конфигураций")
            dialog.setGeometry(100, 100, 800, 600)
            dialog.setWindowFlags(dialog.windowFlags() | QtCore.Qt.WindowMaximizeButtonHint)

            layout = QtWidgets.QVBoxLayout(dialog)

            # Список конфигураций
            config_list = QtWidgets.QListWidget()
            for config in configurations:
                config_list.addItem(f"ID: {config[0]}, Пользователь: {config[1]}, Конфигурация: {config[2]}")
            layout.addWidget(config_list)

            # Поле для ввода новой конфигурации
            new_config_input = QtWidgets.QLineEdit(dialog)
            new_config_input.setPlaceholderText("Введите новую конфигурацию")
            layout.addWidget(new_config_input)

            # Кнопка для сохранения изменений
            save_button = QtWidgets.QPushButton("Сохранить изменения", dialog)
            save_button.clicked.connect(lambda: self.save_edited_configuration(config_list, new_config_input))
            layout.addWidget(save_button)

            # Кнопка "Назад"
            back_button = QtWidgets.QPushButton("Назад", dialog)
            back_button.clicked.connect(dialog.close)  # Закрываем текущее окно
            layout.addWidget(back_button)

            dialog.exec_()
        else:
            QtWidgets.QMessageBox.information(self, "Информация", "Нет сохраненных конфигураций.")

    def save_edited_configuration(self, config_list, new_config_input):
        selected_item = config_list.currentItem()
        if selected_item:
            config_id = selected_item.text().split(",")[0].split(":")[1].strip()
            new_configuration = new_config_input.text()
            self.db.edit_configuration(config_id, new_configuration)
            QtWidgets.QMessageBox.information(self, "Успех", "Конфигурация успешно обновлена!")
        else:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Выберите конфигурацию для редактирования.")

    def select_build_type(self, user_id):
        build_type, ok = QtWidgets.QInputDialog.getItem(self, "Выбор сборки",
                                                        "Выберите тип сборки:",
                                                        ["Готовая сборка", "Сборка по комплектующим", "Просмотр сохраненных конфигураций"],
                                                        0, False)
        if ok:
            if build_type == "Готовая сборка":
                self.select_budget(user_id, False)
            elif build_type == "Сборка по комплектующим":
                self.select_budget(user_id, True)
            elif build_type == "Просмотр сохраненных конфигураций":
                self.view_saved_configurations(user_id)

    def select_budget(self, user_id, custom_build):
        budgets = [800, 1200, 2000]
        budget, ok = QtWidgets.QInputDialog.getItem(self, "Выбор бюджета", "Выберите бюджет:", [str(b) for b in budgets], 0, False)
        if ok:
            budget = int(budget)
            if not custom_build:  # Если выбрана готовая сборка
                self.show_ready_builds(budget, user_id)
            else:
                self.select_processor(budget, user_id)

    def show_ready_builds(self, budget, user_id):
        configurations = self.get_configurations(budget)
        if configurations:
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("Выбор готовой сборки")
            dialog.setGeometry(100, 100, 800, 600)
            dialog.setWindowFlags(dialog.windowFlags() | QtCore.Qt.WindowMaximizeButtonHint)

            layout = QtWidgets.QVBoxLayout(dialog)

            # Список готовых конфигураций
            config_list = QtWidgets.QListWidget()
            for cfg in configurations:
                config_list.addItem(f"{cfg['processor']} - {cfg['videocard']} - {cfg['memory']} - {cfg['motherboard']} ({cfg['price']}$)\n"
                                   f"Плюсы: {cfg['pros']}\n"
                                   f"Минусы: {cfg['cons']}\n")
            layout.addWidget(config_list)

            # Кнопка для сохранения выбранной конфигурации
            save_button = QtWidgets.QPushButton("Сохранить", dialog)
            save_button.setMinimumWidth(390)  # Увеличиваем ширину кнопки
            save_button.setMinimumHeight(80)  # Увеличиваем высоту кнопки
            save_button.clicked.connect(lambda: self.save_selected_configuration(config_list, user_id))
            layout.addWidget(save_button)

            # Кнопка "Назад"
            back_button = QtWidgets.QPushButton("Назад", dialog)
            back_button.clicked.connect(dialog.close)  # Закрываем текущее окно
            layout.addWidget(back_button)

            dialog.exec_()
        else:
            QtWidgets.QMessageBox.information(self, "Информация", "Нет доступных готовых конфигураций для выбранного бюджета.")

    def save_selected_configuration(self, config_list, user_id):
        selected_item = config_list.currentItem()
        if selected_item:
            try:
                selected_config = selected_item.text()
                # Разбираем выбранную конфигурацию
                parts = selected_config.split(" - ")
                if len(parts) < 4:
                    raise ValueError("Неверный формат конфигурации")

                configuration = {
                    "processor": parts[0],
                    "videocard": parts[1],
                    "memory": parts[2],
                    "motherboard": parts[3].split(" (")[0],
                    "price": parts[3].split(" (")[1].split("$)")[0],
                    "power_supply": self.get_power_supply(parts[1])  # Добавляем блок питания
                }
                # Сохраняем конфигурацию в базу данных
                self.db.save_configuration(user_id, str(configuration))
                QtWidgets.QMessageBox.information(self, "Успех",
                                                  "Готовая конфигурация сохранена:\n" + str(configuration))

                # Вывод всех комплектующих
                self.show_all_components(configuration)
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Ошибка", f"Ошибка при сохранении конфигурации: {e}")
        else:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Выберите конфигурацию для сохранения.")

    def select_processor(self, budget, user_id):
        processors = {
            800: ["Intel Core i5-12400f", "AMD Ryzen 5 5600", "Intel Core i3-12100", "AMD Athlon 3000G"],
            1200: ["Intel Core i5-13600", "AMD Ryzen 7 5800X", "Intel Core i7-12700K", "AMD Ryzen 5 7600"],
            2000: ["Intel Core i7-13700K", "AMD Ryzen 9 5900X", "Intel Core i9-12900K", "AMD Ryzen 7 5800X3D"]
        }

        dialog = QtWidgets.QInputDialog(self)
        processor, ok = dialog.getItem(self, "Выбор процессора", "Выберите процессор:", processors[budget], 0, False)
        if ok:
            self.select_motherboard(processor, budget, user_id)
        else:
            # Если пользователь нажал "Отмена", возвращаемся на предыдущий шаг
            self.select_budget(user_id, True)

    def select_motherboard(self, processor, budget, user_id):
        # Словарь с совместимыми материнскими платами для каждого процессора
        motherboards = {
            "Intel Core i5-12400f": [
                ("GIGABYTE H610M", "16GB DDR4", "NVIDIA GTX 3060", 470),
                ("ASUS PRIME B560M", "16GB DDR4", "AMD Radeon RX 6800", 500),
                ("MSI PRO B660M-A", "16GB DDR4", "NVIDIA GTX 1660 Super", 550)
            ],
            "Intel Core i5-13600": [
                ("GIGABYTE B660M", "16GB DDR4", "NVIDIA GTX 3060", 500),
                ("ASUS PRIME Z690-P", "16GB DDR4", "AMD Radeon RX 6800", 600),
                ("MSI PRO Z690-A", "16GB DDR4", "NVIDIA GTX 1660 Super", 550)
            ],
            "AMD Ryzen 5 5600": [
                ("MSI B550M PRO-VDH", "16GB DDR4", "AMD Radeon RX 6800", 550),
                ("ASRock B550M-HDV", "16GB DDR4", "NVIDIA RTX 3060", 550),
                ("MSI B550M PRO", "16GB DDR4", "NVIDIA RTX 3070", 650),
            ],
            "AMD Ryzen 7 5800X": [
                ("GIGABYTE B550 AORUS ELITE", "16GB DDR4", "NVIDIA GTX 3060", 600),
                ("ASUS TUF GAMING B550-PLUS", "16GB DDR4", "AMD Radeon RX 6800", 650),
                ("MSI MAG B550 TOMAHAWK", "16GB DDR4", "NVIDIA GTX 1660 Super", 650)
            ],
            "Intel Core i3-12100": [
                ("ASUS PRIME H610M-A", "8GB DDR4", "NVIDIA GTX 1650", 400),
                ("GIGABYTE H610M", "8GB DDR4", "NVIDIA GTX 1650", 420)
            ],
            "AMD Athlon 3000G": [
                ("ASRock A320M-HDV", "8GB DDR4", "Integrated Vega 3", 300),
                ("MSI A320M PRO-VDH", "8GB DDR4", "Integrated Vega 3", 320)
            ],
            "Intel Core i7-12700K": [
                ("ASUS ROG STRIX Z690-E", "32GB DDR5", "NVIDIA RTX 3080", 800),
                ("GIGABYTE Z690 AORUS ELITE", "32GB DDR5", "NVIDIA RTX 3070", 750),
                ("MSI MEG Z690 UNIFY", "32GB DDR5", "NVIDIA RTX 3090", 900)
            ],
            "AMD Ryzen 5 7600": [
                ("MSI B650M PRO-VDH", "16GB DDR5", "NVIDIA RTX 3060 Ti", 600),
                ("ASUS TUF GAMING B650-PLUS", "16GB DDR5", "NVIDIA RTX 3070", 650),
                ("GIGABYTE B650 AORUS ELITE", "16GB DDR5", "NVIDIA RTX 3080", 700)
            ],
            "Intel Core i7-13700K": [
                ("ASUS ROG MAXIMUS Z790 HERO", "32GB DDR5", "NVIDIA RTX 4080", 1000),
                ("GIGABYTE Z790 AORUS MASTER", "32GB DDR5", "NVIDIA RTX 4070", 950),
                ("MSI MEG Z790 ACE", "32GB DDR5", "NVIDIA RTX 4090", 1100)
            ],
            "AMD Ryzen 9 5900X": [
                ("ASUS ROG CROSSHAIR X570-E", "32GB DDR4", "NVIDIA RTX 3080", 900),
                ("GIGABYTE X570 AORUS MASTER", "32GB DDR4", "NVIDIA RTX 3070", 850),
                ("MSI MEG X570 UNIFY", "32GB DDR4", "NVIDIA RTX 3090", 1000)
            ],
            "Intel Core i9-12900K": [
                ("ASUS ROG MAXIMUS Z690 EXTREME", "64GB DDR5", "NVIDIA RTX 4090", 1500),
                ("GIGABYTE Z690 AORUS XTREME", "64GB DDR5", "NVIDIA RTX 4080", 1400),
                ("MSI MEG Z690 GODLIKE", "64GB DDR5", "NVIDIA RTX 4090", 1600)
            ],
            "AMD Ryzen 7 5800X3D": [
                ("ASUS ROG CROSSHAIR X570-E", "32GB DDR4", "NVIDIA RTX 3080", 900),
                ("GIGABYTE X570 AORUS MASTER", "32GB DDR4", "NVIDIA RTX 3070", 850),
                ("MSI MEG X570 UNIFY", "32GB DDR4", "NVIDIA RTX 3090", 1000)
            ]
        }

        if processor in motherboards:
            options = motherboards[processor]
            dialog = QtWidgets.QInputDialog(self)
            selected_motherboard, ok = dialog.getItem(self, "Выбор материнской платы", "Выберите материнскую плату:",
                                                      [opt[0] for opt in options], 0, False)
            if ok:
                for opt in options:
                    if opt[0] == selected_motherboard:
                        self.select_videocard(processor, budget, user_id, opt)
            else:
                # Если пользователь нажал "Отмена", возвращаемся на предыдущий шаг
                self.select_processor(budget, user_id)
        else:
            QtWidgets.QMessageBox.warning(self, "Ошибка", f"Нет доступных материнских плат для процессора {processor}.")
            self.select_processor(budget, user_id)

    def select_videocard(self, processor, budget, user_id, motherboard_option):
        motherboard, memory, videocard, power_supply = motherboard_option
        videocard_options = {
            800: ["NVIDIA GTX 1650", "NVIDIA GTX 1080ti", "AMD Radeon RX 6600"],
            1200: ["NVIDIA 2070 Super", "AMD Radeon RX 6800", "NVIDIA RTX 3060 Ti"],
            2000: ["NVIDIA RTX 3090", "NVIDIA RTX 4070 super", "AMD Radeon RX 7800 XT"]
        }

        videocard, ok = QtWidgets.QInputDialog.getItem(self, "Выбор видеокарты", "Выберите видеокарту:", videocard_options[budget], 0, False)
        if ok:
            self.select_memory(processor, motherboard, videocard, user_id)
        else:
            # Если пользователь нажал "Отмена", возвращаемся на предыдущий шаг
            self.select_motherboard(processor, budget, user_id)

    def select_memory(self, processor, motherboard, videocard, user_id):
        memory_options = ["8GB DDR4", "16GB DDR4", "32GB DDR4", "16GB DDR5", "32GB DDR5"]
        memory, ok = QtWidgets.QInputDialog.getItem(self, "Выбор оперативной памяти", "Выберите оперативную память:", memory_options, 0, False)
        if ok:
            self.select_power_supply(processor, motherboard, videocard, memory, user_id)
        else:
            # Если пользователь нажал "Отмена", возвращаемся на предыдущий шаг
            self.select_videocard(processor,  user_id, (motherboard, memory, videocard, None))

    def select_power_supply(self, processor, motherboard, videocard, memory, user_id):
        power_supply_options = ["500W", "650W", "750W", "1000W"]
        power_supply, ok = QtWidgets.QInputDialog.getItem(self, "Выбор блока питания", "Выберите блок питания:",
                                                          power_supply_options, 0, False)
        if not ok:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Блок питания не выбран. Пожалуйста, выберите блок питания.")
            return

        configuration = {
            "processor": processor,
            "motherboard": motherboard,
            "memory": memory,
            "videocard": videocard,
            "power_supply": power_supply
        }
        self.db.save_configuration(user_id, str(configuration))
        QtWidgets.QMessageBox.information(self, "Успех", "Конфигурация сохранена:\n" + str(configuration))

        # Вывод всех комплектующих
        self.show_all_components(configuration)

    def show_all_components(self, configuration):
        # Вывод всех комплектующих в диалоговом окне
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Ваша конфигурация")
        dialog.setGeometry(100, 100, 600, 400)
        dialog.setWindowFlags(dialog.windowFlags() | QtCore.Qt.WindowMaximizeButtonHint)

        layout = QtWidgets.QVBoxLayout(dialog)

        # Добавляем текстовое поле с комплектующими
        components_text = f"Процессор: {configuration['processor']}\n" \
                          f"Материнская плата: {configuration['motherboard']}\n" \
                          f"Оперативная память: {configuration['memory']}\n" \
                          f"Видеокарта: {configuration['videocard']}\n" \
                          f"Блок питания: {configuration['power_supply']}"

        components_label = QtWidgets.QLabel(components_text, dialog)
        components_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(components_label)

        # Кнопка "Закрыть"
        close_button = QtWidgets.QPushButton("Закрыть", dialog)
        close_button.clicked.connect(dialog.close)
        layout.addWidget(close_button)

        dialog.exec_()

    @staticmethod
    def get_power_supply(videocard):
        # Логика выбора блока питания в зависимости от видеокарты
        if "RTX 4090" in videocard:
            return "1000W"
        elif "RTX 4080" in videocard:
            return "850W"
        elif "RTX 3090" in videocard:
            return "850W"
        elif "RTX 3080" in videocard:
            return "750W"
        elif "RTX 3070" in videocard:
            return "750W"
        elif "RTX 3060" in videocard:
            return "650W"
        elif "RTX 3060 Ti" in videocard:
            return "650W"
        elif "GTX 1660" in videocard:
            return "500W"
        elif "GTX 1650" in videocard:
            return "500W"
        else:
            return "500W"  # По умолчанию

    @staticmethod
    def get_configurations(budget):
        configurations = {
            800: [
                {
                    "processor": "Intel Core i5-12400f",
                    "videocard": "NVIDIA GTX 3060",
                    "memory": "16GB DDR4",
                    "motherboard": "GIGABYTE H610M",
                    "chipset": "H610M",
                    "price": 800,
                    "pros": "Хорошая производительность в играх.",
                    "cons": "Ограниченные возможности для апгрейда.",
                    "description": "Идеальная сборка для геймеров, которые хотят получить хорошую производительность в играх на средних настройках.",
                    "power_supply": "650W"
                },
                {
                    "processor": "AMD Ryzen 5 5600",
                    "videocard": "NVIDIA rtx3060",
                    "memory": "16GB DDR4",
                    "motherboard": "MSI B550M PRO-VDH",
                    "chipset": "B550",
                    "price": 750,
                    "pros": "Отличная цена/производительность.",
                    "cons": "Ограниченная производительность в графически требовательных играх.",
                    "description": "Бюджетная сборка с отличным соотношением цены и производительности.",
                    "power_supply": "650W"
                },
                {
                    "processor": "Intel Core i3-12100",
                    "videocard": "NVIDIA GTX 1650",
                    "memory": "8GB DDR4",
                    "motherboard": "ASUS PRIME H610M-A",
                    "chipset": "H610",
                    "price": 600,
                    "pros": "Бюджетная сборка для офисных задач.",
                    "cons": "Не подходит для современных игр.",
                    "description": "Подходит для офисных задач и легких игр.",
                    "power_supply": "500W"
                },
                {
                    "processor": "AMD Athlon 3000G",
                    "videocard": "Integrated Vega 3",
                    "memory": "8GB DDR4",
                    "motherboard": "ASRock A320M-HDV",
                    "chipset": "A320",
                    "price": 350,
                    "pros": "Очень низкая цена.",
                    "cons": "Слабая производительность.",
                    "description": "Минимальная сборка для базовых задач.",
                    "power_supply": "300W"
                },
                {
                    "processor": "Intel Pentium Gold G6400",
                    "videocard": "NVIDIA GTX 1650",
                    "memory": "8GB DDR4",
                    "motherboard": "Gigabyte H410M",
                    "chipset": "H410",
                    "price": 400,
                    "pros": "Хорошая производительность для базовых задач.",
                    "cons": "Не подходит для серьезных игр.",
                    "description": "Подходит для офисных задач и легких игр.",
                    "power_supply": "500W"
                },
                {
                    "processor": "AMD Ryzen 3 3200G",
                    "videocard": "Integrated Vega 8",
                    "memory": "16GB DDR4",
                    "motherboard": "MSI A320M PRO-VDH",
                    "chipset": "A320",
                    "price": 450,
                    "pros": "Подходит для легких игр.",
                    "cons": "Не хватает мощности для современных игр.",
                    "description": "Подходит для легких игр и офисных задач.",
                    "power_supply": "500W"
                }
            ],
            1200: [
                {
                    "processor": "Intel Core i5-13600",
                    "videocard": "NVIDIA RTX 4060",
                    "memory": "16GB DDR4",
                    "motherboard": "GIGABYTE B760 DS3H DDR4",
                    "chipset": "B760",
                    "price": 1150,
                    "pros": "Высокая производительность в играх и многопоточности.",
                    "cons": "Высокая цена, потребление энергии.",
                    "description": "Сборка для геймеров, которые хотят получить максимальную производительность в играх.",
                    "power_supply": "750W"
                },
                {
                    "processor": "AMD Ryzen 7 5800X",
                    "videocard": "AMD Radeon RX 6800 XT",
                    "memory": "16GB DDR4",
                    "motherboard": "GIGABYTE B550 AORUS ELITE",
                    "chipset": "B550",
                    "price": 1200,
                    "pros": "Отличная производительность в многопоточности.",
                    "cons": "Может перегреваться без хорошего охлаждения.",
                    "description": "Сборка для геймеров и профессионалов, которые хотят получить максимальную производительность.",
                    "power_supply": "750W"
                },
                {
                    "processor": "AMD Ryzen 5 7500f ",
                    "videocard": " NVIDIA RTX 4060",
                    "memory": "16GB DDR4",
                    "motherboard": "GIGABYTE B650 EAGLE AX",
                    "chipset": "B550",
                    "price": 1200,
                    "pros": "Отличная производительность в многопоточности.",
                    "cons": "можно использовать стоковое охлаждение.",
                    "description": "Сборка для геймеров, которые хотят получить хорошую производительность в играх.",
                    "power_supply": "650W"
                },
                {
                    "processor": "Intel Core i5-12400",
                    "videocard": "NVIDIA GTX 1660 Super",
                    "memory": "16GB DDR4",
                    "motherboard": "ASUS TUF Gaming B560M-PLUS",
                    "chipset": "B560",
                    "price": 1100,
                    "pros": "Хорошая производительность в играх.",
                    "cons": "Не поддерживает DDR5.",
                    "description": "Сборка для геймеров, которые хотят получить хорошую производительность в играх.",
                    "power_supply": "650W"
                },
                {
                    "processor": "AMD Ryzen 5 7600",
                    "videocard": "NVIDIA RTX 3060 Ti",
                    "memory": "16GB DDR5",
                    "motherboard": "MSI B650M PRO-VDH",
                    "chipset": "B650",
                    "price": 1200,
                    "pros": "Отличная производительность в играх и приложениях.",
                    "cons": "Высокая цена на видеокарту.",
                    "description": "Сборка для геймеров, которые хотят получить максимальную производительность в играх.",
                    "power_supply": "750W"
                },
                {
                    "processor": "Intel Core i5-12400F",
                    "videocard": "AMD Radeon RX 6600",
                    "memory": "16GB DDR4",
                    "motherboard": "MSI PRO B660M-A",
                    "chipset": "B660",
                    "price": 1150,
                    "pros": "Отличная производительность в играх.",
                    "cons": "Ограниченные возможности для апгрейда.",
                    "description": "Сборка для геймеров, которые хотят получить хорошую производительность в играх.",
                    "power_supply": "650W"
                }
            ],
            2000: [
                {
                    "processor": "Intel Core i7-13700K",
                    "videocard": "NVIDIA RTX 4070 super",
                    "memory": "32GB DDR5",
                    "motherboard": " MSI PRO Z790-A",
                    "chipset": "Z790",
                    "price": 1900,
                    "pros": "Выдающаяся производительность в играх и приложениях.",
                    "cons": "Высокая цена, потребление энергии.",
                    "description": "Сборка для геймеров и профессионалов, которые хотят получить максимальную производительность.",
                    "power_supply": "850W"
                },
                {
                    "processor": "AMD Ryzen 9 5900X",
                    "videocard": "NVIDIA RTX 4070 super",
                    "memory": "32GB DDR4",
                    "motherboard": "MSI MAG X570 TOMAHAWK",
                    "chipset": "X570",
                    "price": 2000,
                    "pros": "Отличная производительность в многозадачности и играх.",
                    "cons": "Высокая стоимость, требует хорошего охлаждения.",
                    "description": "Сборка для геймеров и профессионалов, которые хотят получить максимальную производительность.",
                    "power_supply": "850W"
                },
                {
                    "processor": "Intel Core i9-12900K",
                    "videocard": "NVIDIA RTX 4080",
                    "memory": "32GB DDR5",
                    "motherboard": "ASUS ROG STRIX Z690-E",
                    "chipset": "Z690",
                    "price": 2000,
                    "pros": "Максимальная производительность для игр и работы.",
                    "cons": "Очень высокая цена.",
                    "description": "Сборка для геймеров и профессионалов, которые хотят получить максимальную производительность.",
                    "power_supply": "1000W"
                },
                {
                    "processor": "AMD Ryzen 7 5800X3D",
                    "videocard": "AMD Radeon RX 6800 XT",
                    "memory": "32GB DDR4",
                    "motherboard": "ASRock X570 Taichi",
                    "chipset": "X570",
                    "price": 2000,
                    "pros": "Отличная производительность в играх и приложениях.",
                    "cons": "Высокая цена, требует качественного охлаждения.",
                    "description": "Сборка для геймеров и профессионалов, которые хотят получить максимальную производительность.",
                    "power_supply": "850W"
                },
                {
                    "processor": "Intel Core i7-12700K",
                    "videocard": "NVIDIA RTX 4070",
                    "memory": "32GB DDR5",
                    "motherboard": "GIGABYTE Z690 AORUS ELITE",
                    "chipset": "Z690",
                    "price": 2000,
                    "pros": "Отличная производительность в играх и многозадачности.",
                    "cons": "Высокая стоимость.",
                    "description": "Сборка для геймеров и профессионалов, которые хотят получить максимальную производительность.",
                    "power_supply": "850W"
                },
                {
                    "processor": "AMD Ryzen 9 7900X",
                    "videocard": "NVIDIA RTX 4070 Ti",
                    "memory": "32GB DDR5",
                    "motherboard": "ASUS ROG STRIX B650E-F",
                    "chipset": "B650E",
                    "price": 2000,
                    "pros": "Идеально подходит для работы и игр.",
                    "cons": "Высокая цена.",
                    "description": "Сборка для геймеров и профессионалов, которые хотят получить максимальную производительность.",
                    "power_supply": "850W"
                }
            ],
            float('inf'): [
                {
                    "processor": "Intel Core i7-13700K",
                    "videocard": "NVIDIA RTX 4080",
                    "memory": "64GB DDR5",
                    "motherboard": "ASUS ROG MAXIMUS Z690 HERO",
                    "chipset": "Z690",
                    "price": 3000,
                    "pros": "Максимальная производительность, отличная для игр и работы.",
                    "cons": "Очень высокая цена.",
                    "description": "Сборка для геймеров и профессионалов, которые хотят получить максимальную производительность.",
                    "power_supply": "1000W"
                },
                {
                    "processor": "AMD Ryzen 9 7950X",
                    "videocard": "NVIDIA RTX 4090",
                    "memory": "64GB DDR5",
                    "motherboard": " ASUS TUF GAMING B650-PLUS",
                    "chipset": "B650",
                    "price": 4000,
                    "pros": "Выдающаяся производительность, отличная для профессиональной работы.",
                    "cons": "Высокая цена, требует качественного охлаждения, желательно водяное 3 секционное",
                    "description": "Сборка для геймеров и профессионалов, которые хотят получить максимальную производительность.",
                    "power_supply": "1000W"
                },
                {
                    "processor": "Intel Core i9-13900K",
                    "videocard": "NVIDIA RTX 4090",
                    "memory": "64GB DDR5",
                    "motherboard": "MSI MEG Z690 UNIFY",
                    "chipset": "Z690",
                    "price": 4500,
                    "pros": "Лучшая производительность на данный момент.",
                    "cons": "Очень высокая цена.",
                    "description": "Сборка для геймеров и профессионалов, которые хотят получить максимальную производительность.",
                    "power_supply": "1000W"
                },
                {
                    "processor": "AMD Ryzen 9 7950X3D",
                    "videocard": "NVIDIA RTX 4080 Ti",
                    "memory": "64GB DDR5",
                    "motherboard": "ASUS ROG CROSSHAIR X670E HERO",
                    "chipset": "X670E",
                    "price": 4800,
                    "pros": "Отличная производительность в играх и приложениях.",
                    "cons": "Высокая цена, требует качественного охлаждения.",
                    "description": "Сборка для геймеров и профессионалов, которые хотят получить максимальную производительность.",
                    "power_supply": "1000W"
                },
                {
                    "processor": "Intel Core i9-14900KS",
                    "videocard": "NVIDIA RTX 4090",
                    "memory": "128GB DDR5",
                    "motherboard": "ASUS ROG MAXIMUS Z790 EXTREME",
                    "chipset": "Z690",
                    "price": 5000,
                    "pros": "Максимальная производительность для игр и профессиональной работы.",
                    "cons": "Очень высокая цена.",
                    "description": "Сборка для геймеров и профессионалов, которые хотят получить максимальную производительность.",
                    "power_supply": "1000W"
                },
                {
                    "processor": "AMD Ryzen Threadripper 5990X",
                    "videocard": "NVIDIA RTX 4090",
                    "memory": "128GB DDR5",
                    "motherboard": "ASUS ROG ZENITH II EXTREME",
                    "chipset": "TRX40",
                    "price": 6000,
                    "pros": "Идеально подходит для профессионального использования и игр.",
                    "cons": "Экстремально высокая цена.",
                    "description": "Сборка для геймеров и профессионалов, которые хотят получить максимальную производительность.",
                    "power_supply": "1200W"
                }
            ]
        }
        return configurations.get(budget, [])

    def view_saved_configurations(self, user_id):
        configurations = self.db.view_saved_configurations(user_id)
        if configurations:
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("Сохраненные конфигурации")
            dialog.setGeometry(100, 100, 800, 600)
            dialog.setWindowFlags(dialog.windowFlags() | QtCore.Qt.WindowMaximizeButtonHint)

            layout = QtWidgets.QVBoxLayout(dialog)

            # Список сохраненных конфигураций
            config_list = QtWidgets.QListWidget()
            for config in configurations:
                config_list.addItem(config[0])  # Отображаем только текст конфигурации
            layout.addWidget(config_list)

            # Кнопка "Назад"
            back_button = QtWidgets.QPushButton("Назад", dialog)
            back_button.clicked.connect(dialog.close)  # Закрываем текущее окно
            layout.addWidget(back_button)

            dialog.exec_()
        else:
            QtWidgets.QMessageBox.information(self, "Информация", "Нет сохраненных конфигураций.")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())