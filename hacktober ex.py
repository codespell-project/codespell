import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QHeaderView, QVBoxLayout, QWidget, QLineEdit


class FilterableTable(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Filterable Table")
        self.setGeometry(100, 100, 800, 400)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.table = QTableWidget(self)
        self.layout.addWidget(self.table)

        self.filter_input = QLineEdit(self)
        self.layout.addWidget(self.filter_input)
        self.filter_input.textChanged.connect(self.filter_data)

        # Sample data
        self.data = [
            ["Alice", "25", "Engineer"],
            ["Bob", "30", "Designer"],
            ["Charlie", "28", "Developer"],
            ["David", "35", "Manager"],
        ]

        self.table.setColumnCount(len(self.data[0]))
        self.table.setRowCount(len(self.data))
        self.table.setHorizontalHeaderLabels(["Name", "Age", "Job"])

        for row, row_data in enumerate(self.data):
            for col, cell_data in enumerate(row_data):
                item = QTableWidgetItem(cell_data)
                self.table.setItem(row, col, item)

        self.table.setDragEnabled(True)
        self.table.setAcceptDrops(True)
        self.table.setDragDropMode(QTableWidget.InternalMove)
        self.table.horizontalHeader().setSectionsMovable(True)
        self.table.horizontalHeader().setSortIndicatorShown(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def filter_data(self):
        filter_text = self.filter_input.text()
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if filter_text.lower() in item.text().lower():
                    item.setHidden(False)
                else:
                    item.setHidden(True)


def main():
    app = QApplication(sys.argv)
    window = FilterableTable()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
