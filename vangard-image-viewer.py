import sys
import os
import glob
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QSplitter, QScrollArea, QLabel, QListWidget, QListWidgetItem,
    QSizePolicy, QToolBar,
    QDialog, QLineEdit, QPushButton, QDialogButtonBox, QFileDialog, QMessageBox,
    QStatusBar
)
from PySide6.QtGui import QPixmap, QIcon, QImageReader, QAction, QImage
from PySide6.QtCore import Qt, QSize, QFileSystemWatcher, QTimer

# --- Initial Configuration ---
INITIAL_MONITOR_PATTERNS = [
    "images/**/*",
]
Path("images/subdir").mkdir(parents=True, exist_ok=True)


THUMBNAIL_SIZE = QSize(100, 100)
SUPPORTED_IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp"]


class AddWatchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Watch Location")
        self.setMinimumWidth(450)
        self.layout = QVBoxLayout(self)
        self.info_label = QLabel(
            "Enter a glob pattern (e.g., /path/to/images/**/* or C:\\Pictures\\*.jpg)\n"
            "OR select a directory to watch all its images recursively."
        )
        self.layout.addWidget(self.info_label)
        self.pattern_edit = QLineEdit()
        self.pattern_edit.setPlaceholderText("Type glob pattern here or use button below")
        self.layout.addWidget(self.pattern_edit)
        self.select_dir_button = QPushButton("Select Directory (generates pattern: your_dir/**/*)")
        self.select_dir_button.clicked.connect(self.select_directory)
        self.layout.addWidget(self.select_dir_button)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)
        self.pattern_edit.setFocus()

    def select_directory(self):
        start_dir = str(Path.home())
        if not Path(start_dir).exists(): start_dir = os.getcwd()
        directory = QFileDialog.getExistingDirectory(self, "Select Directory to Monitor", start_dir)
        if directory:
            pattern = (Path(directory) / "**/*").as_posix()
            self.pattern_edit.setText(pattern)

    def get_pattern(self):
        pattern = self.pattern_edit.text().strip()
        return pattern if pattern else None


class ImageBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Browser with File Monitoring")
        self.setGeometry(100, 100, 1200, 800)

        self.monitor_patterns = list(INITIAL_MONITOR_PATTERNS)
        self.watched_dirs = set()
        self.current_displayed_image_path = None

        # --- Toolbar ---
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setIconSize(QSize(22, 22))
        self.addToolBar(self.toolbar)
        add_icon_path = "icons/folder-plus.png"
        quit_icon_path = "icons/application-exit.png"
        add_watch_icon = QIcon.fromTheme("folder-new", QIcon(add_icon_path if Path(add_icon_path).exists() else ""))
        add_watch_action = QAction(add_watch_icon, "Add Watch Location", self)
        add_watch_action.setStatusTip("Add a new directory or glob pattern to monitor")
        add_watch_action.triggered.connect(self.open_add_watch_dialog)
        self.toolbar.addAction(add_watch_action)
        self.toolbar.addSeparator()
        quit_icon = QIcon.fromTheme("application-exit", QIcon(quit_icon_path if Path(quit_icon_path).exists() else ""))
        quit_action = QAction(quit_icon, "Quit", self)
        quit_action.setShortcut(Qt.CTRL | Qt.Key_Q)
        quit_action.setStatusTip("Quit the application")
        quit_action.triggered.connect(self.close)
        self.toolbar.addAction(quit_action)

        # --- Central Widget & Splitter ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.splitter)

        # Left Pane (Thumbnails) - Already correctly scrolling QListWidget
        self.left_pane_widget = QWidget()
        self.left_layout = QVBoxLayout(self.left_pane_widget)
        self.left_layout.setContentsMargins(0,0,0,0)
        self.thumbnail_list_widget = QListWidget()
        self.thumbnail_list_widget.setIconSize(THUMBNAIL_SIZE)
        self.thumbnail_list_widget.setViewMode(QListWidget.IconMode)
        self.thumbnail_list_widget.setResizeMode(QListWidget.Adjust)
        self.thumbnail_list_widget.setMovement(QListWidget.Static)
        self.thumbnail_list_widget.itemClicked.connect(self.on_thumbnail_clicked)
        self.left_layout.addWidget(self.thumbnail_list_widget)

        # Right Pane (Full Image)
        self.right_pane_scroll_area = QScrollArea()
        # --- CHANGE 1: Disable widget resizing by the scroll area ---
        self.right_pane_scroll_area.setWidgetResizable(False)

        self.image_display_label = QLabel("Click a thumbnail to view image")
        self.image_display_label.setAlignment(Qt.AlignCenter)
        # We still want it to expand if the scroll area is bigger than the image,
        # but its *minimum* size should be the image size for scrolling.
        # Default QSizePolicy.Preferred is usually fine here, but let's ensure vertical preferred too.
        self.image_display_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        self.right_pane_scroll_area.setWidget(self.image_display_label)

        self.splitter.addWidget(self.left_pane_widget)
        self.splitter.addWidget(self.right_pane_scroll_area)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 4)

        # --- Status Bar ---
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.sb_file_label = QLabel()
        self.sb_file_label.setMinimumWidth(250)
        self.status_bar.addWidget(self.sb_file_label)
        self.sb_dims_label = QLabel()
        self.sb_dims_label.setMinimumWidth(120)
        self.status_bar.addWidget(self.sb_dims_label)
        self.sb_format_label = QLabel()
        self.sb_format_label.setMinimumWidth(100)
        self.status_bar.addWidget(self.sb_format_label)
        self.sb_size_label = QLabel()
        self.sb_size_label.setMinimumWidth(120)
        self.status_bar.addWidget(self.sb_size_label)
        self.sb_meta_label = QLabel()
        self.sb_meta_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.status_bar.addWidget(self.sb_meta_label, 1)
        self._update_status_bar_info()

        self.processed_files = set()
        self.path_to_item_map = {}
        self.file_watcher = QFileSystemWatcher(self)
        self.file_watcher.directoryChanged.connect(self.on_directory_changed)
        self.dir_change_timer = QTimer(self)
        self.dir_change_timer.setSingleShot(True)
        self.dir_change_timer.setInterval(500)
        self.dir_change_timer.timeout.connect(self.handle_watched_paths_scan)

        self.initial_scan_and_watch()

    def _update_status_bar_info(self, file_path_str=None, image: QImage=None, img_format_str=None, error_message=None):
        if error_message:
            self.status_bar.showMessage(error_message, 5000)
            self.sb_file_label.setText("")
            self.sb_file_label.setToolTip("")
            self.sb_dims_label.setText("")
            self.sb_format_label.setText("")
            self.sb_size_label.setText("")
            self.sb_meta_label.setText("")
            return

        self.status_bar.clearMessage()

        if file_path_str and image and not image.isNull():
            p = Path(file_path_str)
            self.sb_file_label.setText(f"File: {p.name}")
            self.sb_file_label.setToolTip(file_path_str)
            self.sb_dims_label.setText(f"Dims: {image.width()}x{image.height()}")
            self.sb_format_label.setText(f"Format: {img_format_str or 'N/A'}")

            try:
                file_size_bytes = p.stat().st_size
                if file_size_bytes < 1024: file_size_display = f"{file_size_bytes} B"
                elif file_size_bytes < 1024 * 1024: file_size_display = f"{file_size_bytes / 1024:.1f} KB"
                else: file_size_display = f"{file_size_bytes / (1024 * 1024):.1f} MB"
                self.sb_size_label.setText(f"FS Size: {file_size_display}")
            except FileNotFoundError:
                self.sb_size_label.setText("FS Size: N/A (deleted?)")

            metadata_parts = [f"{key}: {image.text(key)}" for key in image.textKeys()]
            metadata_display = "; ".join(metadata_parts) if metadata_parts else ""

            max_meta_len = 100
            if len(metadata_display) > max_meta_len:
                metadata_display = metadata_display[:max_meta_len-3] + "..."

            self.sb_meta_label.setText(f"Meta: {metadata_display}" if metadata_display else "")

        else:
            self.sb_file_label.setText("")
            self.sb_file_label.setToolTip("")
            self.sb_dims_label.setText("")
            self.sb_format_label.setText("")
            self.sb_size_label.setText("")
            self.sb_meta_label.setText("")


    def on_thumbnail_clicked(self, item: QListWidgetItem):
        file_path = item.data(Qt.UserRole)
        self.current_displayed_image_path = None

        if not file_path:
            self.image_display_label.setText("Invalid item clicked.")
            # --- CHANGE 2: Clear image and reset label size for blank state ---
            self.image_display_label.setPixmap(QPixmap()) # Clear any previous image
            self.image_display_label.adjustSize() # Adjust size to empty pixmap (minimal)
            self._update_status_bar_info()
            return

        reader = QImageReader(file_path)
        reader.setAutoTransform(True)

        if not reader.canRead():
            err_msg = reader.errorString() or "Cannot read image format."
            display_err = f"Cannot read image: {Path(file_path).name}\n({err_msg})"
            self.image_display_label.setText(display_err)
            # --- CHANGE 2: Clear image and reset label size for error state ---
            self.image_display_label.setPixmap(QPixmap())
            self.image_display_label.adjustSize()
            self._update_status_bar_info(error_message=f"Read error: {err_msg}")
            return

        img_format_bytes = reader.format()
        img_format_str = img_format_bytes.data().decode(errors='replace').upper() if not img_format_bytes.isNull() and img_format_bytes.data() else "N/A"

        image = reader.read()
        if image.isNull():
            err_msg = reader.errorString() or "Unknown error loading image."
            display_err = f"Error loading image: {Path(file_path).name}\n({err_msg})"
            self.image_display_label.setText(display_err)
            # --- CHANGE 2: Clear image and reset label size for error state ---
            self.image_display_label.setPixmap(QPixmap())
            self.image_display_label.adjustSize()
            self._update_status_bar_info(error_message=f"Load error: {err_msg}")
            return

        # Success path
        pixmap = QPixmap.fromImage(image)
        self.image_display_label.setPixmap(pixmap)
        # --- CHANGE 2: Explicitly adjust label size after setting pixmap ---
        self.image_display_label.adjustSize()

        self.current_displayed_image_path = file_path
        self._update_status_bar_info(file_path_str=file_path, image=image, img_format_str=img_format_str)


    def open_add_watch_dialog(self):
        dialog = AddWatchDialog(self)
        if dialog.exec() == QDialog.Accepted:
            new_pattern = dialog.get_pattern()
            if new_pattern:
                if new_pattern not in self.monitor_patterns:
                    self.add_new_watch_pattern(new_pattern)
                else:
                    QMessageBox.information(self, "Pattern Exists",
                                            f"The pattern '{new_pattern}' is already being monitored.")
            else:
                QMessageBox.warning(self, "No Pattern", "No pattern was entered.")

    def add_new_watch_pattern(self, pattern_str):
        print(f"Adding new watch pattern: {pattern_str}")
        self.monitor_patterns.append(pattern_str)
        print(f"Scanning newly added pattern: {pattern_str}")
        self.scan_directories([pattern_str])
        new_dir_to_watch_str = self._get_base_dir_for_pattern(pattern_str)
        if new_dir_to_watch_str:
            abs_new_dir_to_watch = str(Path(new_dir_to_watch_str).resolve())
            if abs_new_dir_to_watch not in self.watched_dirs:
                if Path(abs_new_dir_to_watch).is_dir():
                    self.file_watcher.addPath(abs_new_dir_to_watch)
                    self.watched_dirs.add(abs_new_dir_to_watch)
                    print(f"Now watching directory: {abs_new_dir_to_watch}")
                else:
                    msg = (f"The base directory '{abs_new_dir_to_watch}' derived from "
                           f"pattern '{pattern_str}' is not a valid or accessible directory. "
                           "It will not be actively monitored by the file system watcher.")
                    QMessageBox.warning(self, "Directory Not Watched", msg)
                    print(f"Warning: {msg}")
        else:
            msg = (f"Could not determine a valid base directory to watch for pattern: '{pattern_str}'.")
            QMessageBox.warning(self, "No Base Directory", msg)
            print(f"Warning: {msg}")


    def _get_base_dir_for_pattern(self, pattern_str: str) -> str | None:
        try:
            p = Path(pattern_str)
            if not p.is_absolute(): p = Path.cwd() / p
            dir_to_watch = p
            while dir_to_watch.parent != dir_to_watch and any(c in dir_to_watch.name for c in ['*', '?', '[', ']']):
                dir_to_watch = dir_to_watch.parent
            resolved_dir = dir_to_watch.resolve(strict=False)
            return str(resolved_dir.parent) if resolved_dir.is_file() else str(resolved_dir)
        except Exception as e:
            print(f"Error determining base directory for '{pattern_str}': {e}")
            return None

    def showEvent(self, event): super().showEvent(event)
    def is_image_file(self, file_path: Path) -> bool: return file_path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS

    def process_file(self, file_path_str: str):
        file_path = Path(file_path_str).resolve()
        if not file_path.is_file() or not self.is_image_file(file_path): return
        str_path = str(file_path)
        pixmap = QPixmap(str_path)
        if pixmap.isNull(): return
        thumbnail = pixmap.scaled(THUMBNAIL_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        q_icon = QIcon(thumbnail)
        if str_path in self.path_to_item_map:
            self.path_to_item_map[str_path].setIcon(q_icon)
        else:
            item = QListWidgetItem(q_icon, file_path.name)
            item.setData(Qt.UserRole, str_path)
            item.setToolTip(str_path)
            self.thumbnail_list_widget.addItem(item)
            self.path_to_item_map[str_path] = item

    def scan_directories(self, patterns_to_scan: list[str], specific_dir_to_check: Path | None = None):
        for pattern_str in patterns_to_scan:
            try:
                p = Path(pattern_str)
                if not p.is_absolute(): p = Path.cwd() / p
                glob_pattern_str = p.as_posix()
                for file_path_str_from_glob in glob.glob(glob_pattern_str, recursive=True):
                    file_path = Path(file_path_str_from_glob).resolve()
                    if specific_dir_to_check:
                         try:
                            resolved_specific_dir = specific_dir_to_check.resolve(strict=True)
                            if not (file_path == resolved_specific_dir or resolved_specific_dir in file_path.parents):
                                continue
                         except (FileNotFoundError, ValueError):
                             if not str(file_path).startswith(str(specific_dir_to_check.resolve(strict=False))):
                                continue
                    if self.is_image_file(file_path): self.process_file(str(file_path))
            except Exception as e: print(f"Error scanning pattern '{pattern_str}': {e}")

    def initial_scan_and_watch(self):
        print("Performing initial scan and setting up watchers...")
        self.scan_directories(self.monitor_patterns)
        paths_to_add_to_watcher = set()
        for pattern in self.monitor_patterns:
            base_dir_str = self._get_base_dir_for_pattern(pattern)
            if base_dir_str :
                if Path(base_dir_str).is_dir():
                    paths_to_add_to_watcher.add(base_dir_str)
                    self.watched_dirs.add(base_dir_str)
                else:
                    print(f"Info: Base directory '{base_dir_str}' from pattern '{pattern}' not a dir. Cannot watch.")
        if paths_to_add_to_watcher:
            print(f"Initially watching: {list(paths_to_add_to_watcher)}")
            self.file_watcher.addPaths(list(paths_to_add_to_watcher))
        else: print("No valid initial directories to watch.")

    def on_directory_changed(self, path_str: str):
        self.changed_dir_path = Path(path_str)
        self.dir_change_timer.start()

    def handle_watched_paths_scan(self):
        if not hasattr(self, 'changed_dir_path') or self.changed_dir_path is None: return
        try: resolved_changed_dir = self.changed_dir_path.resolve(strict=True)
        except FileNotFoundError:
            path_str_to_remove = str(self.changed_dir_path)
            print(f"Watched directory {path_str_to_remove} no longer exists. Removing from watcher.")
            self.file_watcher.removePath(path_str_to_remove)
            self.watched_dirs.discard(path_str_to_remove)
            self.changed_dir_path = None
            return
        relevant_patterns = set()
        for p_str in self.monitor_patterns:
            base_dir_p_str = self._get_base_dir_for_pattern(p_str)
            if not base_dir_p_str: continue
            base_p = Path(base_dir_p_str)
            try:
                if resolved_changed_dir == base_p or \
                   resolved_changed_dir.is_relative_to(base_p) or \
                   base_p.is_relative_to(resolved_changed_dir):
                    relevant_patterns.add(p_str)
            except AttributeError: # Fallback for Python < 3.9
                resolved_changed_dir_str = str(resolved_changed_dir)
                base_p_str = str(base_p)
                sep = os.sep
                if resolved_changed_dir_str == base_p_str or \
                   resolved_changed_dir_str.startswith(base_p_str + sep) or \
                   base_p_str.startswith(resolved_changed_dir_str + sep):
                    relevant_patterns.add(p_str)

        patterns_to_scan_now = list(relevant_patterns) if relevant_patterns else self.monitor_patterns
        self.scan_directories(patterns_to_scan_now, specific_dir_to_check=resolved_changed_dir)
        self.changed_dir_path = None


if __name__ == '__main__':
    app = QApplication(sys.argv)
    if hasattr(Qt, 'AA_EnableHighDpiScaling'): QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'): QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    window = ImageBrowser()
    window.show()
    sys.exit(app.exec())