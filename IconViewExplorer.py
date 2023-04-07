import os
import numpy as np
from PyQt5.QtWidgets import QListView, QStyledItemDelegate, QWidget, QVBoxLayout, QHBoxLayout, QStyle, QApplication, QFileIconProvider
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QDrag, QColor, QTextOption, QPalette, QFontMetrics, QIcon, QPixmap
from PyQt5.QtCore import QSize, Qt, QRect, QFileInfo, QMimeData, QUrl
from PIL import Image
from PIL.Image import Resampling
import qimage2ndarray
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.ico']
def is_image(file_path):
    _, ext = os.path.splitext(file_path)
    return ext.lower() in IMAGE_EXTENSIONS
class ThumbnailListView(QListView):
    '''A custom QListView subclass that handles the display of image thumbnails using the ThumbnailModel and 
    ThumbnailItemDelegate'''
    def __init__(self, parent=None, spacing=10):
        self.iconsSpace=spacing
        super(ThumbnailListView, self).__init__(parent)
        self.setSelectionMode(self.ExtendedSelection)
        # Enable drag and drop support
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
    def sizeHintForIndex(self, index):
        return self.itemDelegate().sizeHint(self.viewOptions(), index)
    def startDrag(self, supportedActions):
        selected_indexes = self.selectedIndexes()
        # Create a QDrag object to store the selected items
        drag = QDrag(self)
        mime_data = self.model().mimeData(selected_indexes)
        drag.setMimeData(mime_data)
        drag.exec_(Qt.CopyAction)
    def get_icon_coordinates(self):
        icon_coordinates = {}
        for row in range(self.model().rowCount()):
            item_index = self.model().index(row, 0)
            item_rect = self.visualRect(item_index)
            icon_coordinates[row] = {
                "x": item_rect.center().x(),
                "y": item_rect.center().y(),
            }
        return icon_coordinates
    def reorderTheTarget(self, target_index, event, putItAfter):
        target_item = self.model().itemFromIndex(target_index)
        selected_indexes = [(index.row(), self.model().itemFromIndex(index)) for index in self.selectedIndexes()]
        selected_indexes.sort(key=lambda x: x[0])
        targetInSelected_indexes=False
        # Remove items from the model in reverse order
        for row, selected_indexesItem in reversed(selected_indexes):
            if selected_indexesItem is not target_item:
                self.model().takeRow(row)
            else:
                targetInSelected_indexes=True
        # Find the new index of the target item
        new_target_index = self.model().indexFromItem(target_item)
        if putItAfter:
            if targetInSelected_indexes:
                if self.model().item(self.model().rowCount()-1, 0) is target_item:
                    putItAfter=0
            if putItAfter:
                putItAfter=1
        else:
            putItAfter=0
        new_target_row = new_target_index.row()+putItAfter
        if targetInSelected_indexes:
            self.model().takeRow(new_target_index.row())
        for i, (_, item) in enumerate(selected_indexes):
            self.model().insertRow(new_target_row + i, item)
        event.accept()
    def dropEvent(self, event):
        if event.source() == self:
            dropPoint={'x':event.pos().x(),'y':event.pos().y()}
            lastItemIntIndex= self.model().rowCount()-1
            lastItemPoses = self.visualRect(self.model().index(lastItemIntIndex, 0))
            selectedTargetIndex=-1
            #'below all files'
            if dropPoint['y']>lastItemPoses.bottom()+self.iconsSpace/2:
                selectedTargetIndex=lastItemIntIndex
                putItAfter=True
            #'right of last row'
            elif dropPoint['y']>lastItemPoses.top()-self.iconsSpace/2:
                if dropPoint['x']>lastItemPoses.right():
                    selectedTargetIndex=lastItemIntIndex
                    putItAfter=True
            if selectedTargetIndex==-1:
                icon_coordinates = self.get_icon_coordinates()
                min_distance = float("inf")
                for i, icon in icon_coordinates.items():
                    center_x, center_y = icon['x'], icon['y']
                    distance = ((center_x - dropPoint['x']) ** 2 + (center_y - dropPoint['y']) ** 2) ** 0.5
                    if distance < min_distance:
                        selectedTargetIndex = i
                        min_distance = distance
                        putItAfter = dropPoint['x'] > center_x
            selectedTargetModelIndexObject = self.model().index(selectedTargetIndex, 0)
            self.reorderTheTarget(selectedTargetModelIndexObject, event, putItAfter)
        else:
            super(ThumbnailListView, self).dropEvent(event)
class ThumbnailItemDelegate(QStyledItemDelegate):
    '''
    A custom item delegate for displaying image thumbnails in a QListView with appropriate styling and text wrapping.
    The ThumbnailItemDelegate class is a subclass of QStyledItemDelegate which customizes the appearance and layout
    of items in a QListView.
    The ThumbnailItemDelegate is set as the delegate for the ThumbnailListView using the setItemDelegate method.
    '''
    def paint(self, painter, option, index):
        '''
        The paint method is called by the QListView when it needs to paint an item in the view. 
        It takes three arguments: painter is a QPainter object used to paint the item, option contains the style 
        options for the item, and index is the model index for the item. In this method, the delegate paints an icon
        and wrapped text for each item.
        '''
        icon_rect = QRect(option.rect.left(), option.rect.top(), 128, 128)
        text_rect = QRect(option.rect.left(), option.rect.top() + 128, 128, option.rect.height() - 128)
        icon = index.data(Qt.DecorationRole)
        text = index.data(Qt.DisplayRole)
        wrapped_text = self.wrap_text(text, 128, option.font)
        painter.save()
        if icon is not None:
            painter.drawPixmap(icon_rect, icon.pixmap(128, 128))
        # Draw semi-transparent blue highlight on top of the icon
        if option.state & QStyle.State_Selected:
            painter.setBrush(QColor(51, 153, 255, 51))  # Adjust the last value (51) to control opacity (0-255)
            painter.setPen(Qt.NoPen)
            painter.drawRect(icon_rect)
        # Draw the text using QStyle
        style = QApplication.style()
        text_option = QTextOption(Qt.AlignTop | Qt.AlignHCenter | Qt.TextWordWrap)
        style.drawItemText(painter, text_rect, text_option.alignment(), option.palette, True, wrapped_text, QPalette.Text if option.state & QStyle.State_Selected else QPalette.WindowText)
        painter.restore()
    def wrap_text(self, text, max_width, font):
        '''
        The wrap_text method is a helper method that takes a string text, a maximum width max_width, and a font 
        and returns a new string with line breaks inserted to wrap the text to the maximum width.
        This method is called from the paint method to wrap the text for display.
        '''
        if text is None:
            return ""
        font_metrics = QFontMetrics(font)
        wrapped_text = ""
        line = ""
        for char in text:
            line += char
            if font_metrics.horizontalAdvance(line) > max_width:
                wrapped_text += '\n' + char
                line = char
            else:
                wrapped_text += char
        return wrapped_text
    def sizeHint(self, option, index):
        '''
        The sizeHint method is called by the QListView to determine the size of each item in the view.
        It takes two arguments: option contains the style options for the item, and index is the model index for the
        item. In this method, the delegate calculates the height of the item based on the wrapped text and 
        returns a QSize object with the width and height of the item.
        '''
        text = index.data(Qt.DisplayRole)
        wrapped_text = self.wrap_text(text, 128, option.font)
        font_metrics = QFontMetrics(option.font)
        text_height = font_metrics.boundingRect(
            0, 0, 128, 0,
            Qt.TextWordWrap | Qt.AlignTop | Qt.AlignHCenter,
            wrapped_text
        ).height()
        return QSize(128, 128 + text_height)
class ThumbnailModel(QStandardItemModel):
    '''A custom model for displaying image thumbnails in a QListView'''
    def __init__(self, files=[], icon_size=128):
        super(ThumbnailModel, self).__init__()
        self.icon_size = icon_size
        self.files = files
        self.load_files(self.files)

    def update_files(self, new_files):
        self.files = new_files
        self.removeRows(0, self.rowCount())
        self.load_files(new_files)

    def load_files(self, files):
        for file_path in files:
            if os.path.isfile(file_path):
                file_name = os.path.basename(file_path)
                item = QStandardItem(file_name)
                item.setData(os.path.dirname(file_path), Qt.UserRole)  # Store the folder path in UserRole
                thumbnail = self.create_thumbnail(file_path)
                item.setIcon(QIcon(thumbnail))
                self.appendRow(item)
    def create_thumbnail(self, file_path):
        'feature: create image of file for thumbnail'
        if is_image(file_path):
            try:
                image = Image.open(file_path)
                image.thumbnail((self.icon_size, self.icon_size), Resampling.LANCZOS)
                image_array = np.array(image)
                qimage = qimage2ndarray.array2qimage(image_array)
                pixmap = QPixmap.fromImage(qimage)
                return pixmap
            except Exception as e:
                print(f"Error loading image: {e}")
        else:
            # Get the default icon for the file type
            icon_provider = QFileIconProvider()
            file_icon = icon_provider.icon(QFileInfo(file_path))
            pixmap = file_icon.pixmap(self.icon_size)
            return pixmap
    def mimeTypes(self):
        return ['text/uri-list']
    def mimeData(self, indexes):
        mime_data = QMimeData()
        urls = []
        for index in indexes:
            if index.isValid():
                file_path = os.path.join(index.data(Qt.UserRole), index.data(Qt.DisplayRole))
                urls.append(QUrl.fromLocalFile(file_path))
        mime_data.setUrls(urls)
        return mime_data
class IconViewExplorer(QWidget):
    def __init__(self, file_explorer_logic):
        super(IconViewExplorer, self).__init__()

        self.file_explorer_logic = file_explorer_logic
        self.file_explorer_logic.updated_files_signal.connect(self.update_files)
        self.iconsSpace=10
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.list_view = ThumbnailListView(self, self.iconsSpace)
        self.list_view.setStyleSheet("QListView::item { width: 128px;  word-wrap: break-word;}"
                                      "QListView::item:selected { background-color: #3399FF; }")
        self.list_view.setItemDelegate(ThumbnailItemDelegate())
        self.list_view.setSpacing(self.iconsSpace)
        self.list_view.setUniformItemSizes(False)
        self.list_view.setViewMode(QListView.IconMode)
        self.list_view.setResizeMode(QListView.Adjust)
        self.thumbnail_model = ThumbnailModel(self.file_explorer_logic.files_to_be_shown)
        self.list_view.setModel(self.thumbnail_model)
        self.list_view.setIconSize(QSize(128, 128))

        layout.addWidget(self.list_view)

        self.setLayout(layout)

    def update_files(self, files):
        self.thumbnail_model.update_files(files)