import sys
import os
from PyQt5.QtWidgets import QMainWindow, QSplitter, QApplication, QVBoxLayout, QWidget
from PyQt5.QtCore import QObject, pyqtSignal, Qt
os.chdir(os.path.dirname(os.path.realpath(__file__)))
from SelectedFolders import SelectedFolders
from IconViewExplorer import IconViewExplorer
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.file_explorer_logic = FileExplorerLogic()

        # Create the main layout
        main_layout = QVBoxLayout()

        # Create instances of selectedFolders and IconViewExplorer classes
        self.selected_folders = SelectedFolders(self.file_explorer_logic)
        self.icon_view_explorer = IconViewExplorer(self.file_explorer_logic)

        # Add the panes to a QSplitter
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.selected_folders)
        splitter.addWidget(self.icon_view_explorer)

        # Add the splitter to the main layout
        main_layout.addWidget(splitter)

        # Create a container widget and set it as the central widget
        container_widget = QWidget()
        container_widget.setLayout(main_layout)
        self.setCentralWidget(container_widget)
class FileExplorerLogic(QObject):
    updated_files_signal = pyqtSignal(list)

    def __init__(self):
        super(FileExplorerLogic, self).__init__()
        self.selected_folders = []
        self.files_to_be_shown = []

    def update_selected_folders(self, new_folders):
        self.selected_folders = new_folders
        self.update_files_to_be_shown()

    def update_files_to_be_shown(self):
        self.files_to_be_shown = []
        for folder in self.selected_folders:
            if os.path.exists(folder):
                for file_name in os.listdir(folder):
                    file_path = os.path.join(folder, file_name)
                    if os.path.isfile(file_path):
                        self.files_to_be_shown.append(file_path)
        self.updated_files_signal.emit(self.files_to_be_shown)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())