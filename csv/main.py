from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QTableView, QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
import pandas as pd
import sys


class CsvEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Редактор lessons.csv")
        self.resize(800, 600)

        self.lesson_types = pd.read_csv('lesson_type.csv')
        self.lessons = pd.read_csv('lessons.csv')
        self.subjects = pd.read_csv('subjects.csv')
        self.subjects_dict = self.subjects.set_index('id')['name'].to_dict()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        controls_layout = QHBoxLayout()
        self.layout.addLayout(controls_layout)

        self.combo = QComboBox()
        self.combo.addItems(self.subjects['name'].dropna().tolist())
        controls_layout.addWidget(self.combo)

        self.load_button = QPushButton("Загрузить")
        controls_layout.addWidget(self.load_button)
        self.load_button.clicked.connect(self.load_lessons_for_subject)

        self.table = QTableView()
        self.layout.addWidget(self.table)

        self.load_lessons_to_table(self.lessons)  # Изначально загрузить все

        self.save_button = QPushButton("Сохранить изменения в lessons.csv")
        self.layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_lessons)


    def load_lessons_to_table(self, df):
        model = QStandardItemModel(self)
        headers = list(df.columns)
        # Изменим заголовок subject на "Предмет"
        display_headers = ['Предмет' if h == 'subject' else h for h in headers]
        model.setHorizontalHeaderLabels(display_headers)

        for _, row in df.iterrows():
            items = []
            for col in headers:
                val = row[col]
                if col == 'subject':
                    val = self.subjects_dict.get(val, "") if pd.notna(val) else ""
                else:
                    val = "" if pd.isna(val) else str(val)
                item = QStandardItem(val)
                item.setEditable(True)
                items.append(item)
            model.appendRow(items)

        self.table.setModel(model)


    def load_lessons_for_subject(self):
        selected_subject_name = self.combo.currentText()
        # Получаем id предмета по названию из словаря subjects
        subject_id = None
        for id_, name in self.subjects_dict.items():
            if name == selected_subject_name:
                subject_id = id_
                break

        if subject_id is None:
            QMessageBox.warning(self, "Предупреждение", "Выберите корректный предмет")
            return

        # Фильтруем строки lessons по выбранному subject_id
        filtered = self.lessons[self.lessons['subject'] == subject_id]

        self.load_lessons_to_table(filtered)


    def save_lessons(self):
        model = self.table.model()
        rows = model.rowCount()
        cols = model.columnCount()
        data = []
        reverse_subjects = {v: k for k, v in self.subjects_dict.items()}

        for row in range(rows):
            record = {}
            for col in range(cols):
                index = model.index(row, col)
                header = model.headerData(col, Qt.Orientation.Horizontal)
                value = model.data(index)
                if header == 'Предмет':
                    record['subject'] = reverse_subjects.get(value, "")
                else:
                    record[header] = value
            data.append(record)

        df = pd.DataFrame(data)
        if 'Предмет' in df.columns:
            df.rename(columns={'Предмет': 'subject'}, inplace=True)
        try:
            df.to_csv('lessons.csv', index=False)
            QMessageBox.information(self, "Успех", "Данные успешно сохранены в lessons.csv")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = CsvEditor()
    editor.show()
    sys.exit(app.exec())
