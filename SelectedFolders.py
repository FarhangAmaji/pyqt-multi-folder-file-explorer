from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QAbstractItemView, QHBoxLayout, QPushButton, QFileDialog
class SelectedFolders(QWidget):
    def __init__(self, file_explorer_logic):
        super(SelectedFolders, self).__init__()

        self.file_explorer_logic = file_explorer_logic

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.folder_list = QListWidget()
        self.folder_list.setSelectionMode(QAbstractItemView.ExtendedSelection)

        button_layout = QHBoxLayout()
        self.select_folder_btn = QPushButton("Select Folder")
        self.select_folder_btn.clicked.connect(self.select_folder)
        self.remove_folder_btn = QPushButton("Remove Folder")
        self.remove_folder_btn.clicked.connect(self.remove_folder)
        self.save_folders_btn = QPushButton("Save Folders")
        self.save_folders_btn.clicked.connect(self.save_folders)
        self.load_folders_btn = QPushButton("Load Folders")
        self.load_folders_btn.clicked.connect(self.load_folders)

        button_layout.addWidget(self.select_folder_btn)
        button_layout.addWidget(self.remove_folder_btn)
        button_layout.addWidget(self.save_folders_btn)
        button_layout.addWidget(self.load_folders_btn)

        layout.addLayout(button_layout)
        layout.addWidget(self.folder_list)

        self.setLayout(layout)

    def select_folder(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        options |= QFileDialog.ShowDirsOnly
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", "", options=options)
    
        if folder:
            self.folder_list.addItem(folder)
            self.file_explorer_logic.update_selected_folders(self.get_folder_list())

    def remove_folder(self):#new version for to remove multiple folders
        selected_items = self.folder_list.selectedItems()
        if selected_items:
            for item in selected_items:
                self.folder_list.takeItem(self.folder_list.row(item))
            self.file_explorer_logic.update_selected_folders(self.get_folder_list())
    def save_folders(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Folders", "", "Folder Explorer Custom Files (*.fecf *.txt)")
        if file_name:
            if not file_name.endswith('.fecf'):
                file_name += '.fecf'
            with open(file_name, 'w') as file:
                for row in range(self.folder_list.count()):
                    file.write(self.folder_list.item(row).text() + '\n')
    def load_folders(self):#new version for " I load another .fecf file, its folders get added to current selected folders"
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Folders", "", "Folder Explorer Custom Files (*.fecf *.txt)")
        if file_name:
            with open(file_name, 'r') as file:
                folders = [line.strip() for line in file.readlines()]
                existing_folders = set(self.get_folder_list())  # Create a set of existing folders to prevent duplicates
                new_folders = []
                for folder in folders:
                    if folder not in existing_folders:
                        new_folders.append(folder)
                        existing_folders.add(folder)
                self.folder_list.addItems(new_folders)
                self.file_explorer_logic.update_selected_folders(self.get_folder_list())
    def get_folder_list(self):
        folders = []
        for row in range(self.folder_list.count()):
            folders.append(self.folder_list.item(row).text())
        return folders
