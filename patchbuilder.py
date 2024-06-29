import sys
import re
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QTextEdit, QProgressBar, QHBoxLayout
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
import datetime

class FileProcessor(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)

    def __init__(self, input_file, output_file, keywords):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file
        self.keywords = keywords

    def contains_all_keywords(self, statement, keywords):
        # Check if the statement contains all of the keywords
        return all(keyword in statement for keyword in keywords)

    def run(self):
        with open(self.input_file, 'r') as infile:
            content = infile.read()

        # Split the content into statements based on semicolon delimiter
        statements = re.split(r'(;\s*)', content)

        # Prepare the list to store the filtered statements and delimiters
        filtered_statements = []

        # Iterate through the statements and delimiters in pairs
        for i in range(0, len(statements), 2):
            statement = statements[i]
            delimiter = statements[i + 1] if i + 1 < len(statements) else ''

            # Check if the statement contains all the keywords
            if not self.contains_all_keywords(statement, self.keywords):
                # Add the statement and its delimiter to the list
                filtered_statements.append(statement)
                filtered_statements.append(delimiter)

            # Update progress
            progress = int((i / len(statements)) * 100)
            self.progress.emit(progress)

        # Join the filtered statements and delimiters back into a single string
        filtered_content = ''.join(filtered_statements)

        # Write the filtered content to the output file
        with open(self.output_file, 'w') as outfile:
            outfile.write(filtered_content)

        self.finished.emit(self.output_file)

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Patch Generator'
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(100, 100, 600, 400)

        # Set the window icon
        self.setWindowIcon(QIcon('app_icon.ico'))
        
        layout = QVBoxLayout()

        self.label = QLabel('Select a SQL file to process:')
        layout.addWidget(self.label)

        self.openButton = QPushButton('Open SQL File')
        self.openButton.clicked.connect(self.openFileNameDialog)
        layout.addWidget(self.openButton)

        self.saveButton = QPushButton('Save Processed File As')
        self.saveButton.clicked.connect(self.saveFileDialog)
        self.saveButton.setEnabled(False)
        layout.addWidget(self.saveButton)

        self.progressBar = QProgressBar(self)
        layout.addWidget(self.progressBar)
        
        self.log = QTextEdit(self)
        self.log.setReadOnly(True)
        layout.addWidget(self.log)
        
        self.exitButton = QPushButton('Exit')
        self.exitButton.clicked.connect(self.close)

        self.label = QLabel('Help&Support @ sultan.m@gsl.in')
        layout.addWidget(self.label)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.exitButton)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(self, "Open SQL File", "", "SQL Files (*.sql);;All Files (*)", options=options)
        if fileName:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.input_file = fileName
            self.log.append(f"Time: {timestamp}")
            self.log.append(f"Selected input file: {fileName}")
            self.saveButton.setEnabled(True)

    def saveFileDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Save Processed File As", "", "SQL Files (*.sql);;All Files (*)", options=options)
        if fileName:
            self.output_file = fileName
            self.log.append(f"Selected output file: {fileName}")
            self.processFile()

    def processFile(self):
        keywords = ["ALTER", "OWNER TO gslpgadmin"]
        self.processor = FileProcessor(self.input_file, self.output_file, keywords)
        self.processor.progress.connect(self.updateProgress)
        self.processor.finished.connect(self.processingFinished)
        self.processor.start()

    def updateProgress(self, value):
        self.progressBar.setValue(value)

    def processingFinished(self, output_file):
        self.log.append(f"Processing finished.")
        self.log.append("-"*112)
        self.progressBar.setValue(100)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
