import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QPushButton, QLabel, 
                             QMessageBox, QStatusBar, QSizePolicy)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import re

import logic

class FetchThread(QThread):
    # (결과 딕셔너리, 이미지 바이트 데이터) 반환
    result_ready = pyqtSignal(dict, bytes)
    
    def __init__(self, url):
        super().__init__()
        self.url = url
        
    def run(self):
        info_result = logic.extract_video_info(self.url)
        img_data = b""
        if info_result.get('success') and info_result.get('thumbnail_url'):
            img_data = logic.download_image(info_result['thumbnail_url'])
        
        self.result_ready.emit(info_result, img_data or b"")

class DownloadThread(QThread):
    progress_update = pyqtSignal(str)
    finished_signal = pyqtSignal(dict)
    
    def __init__(self, url):
        super().__init__()
        self.url = url
        
    def hook(self, d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '알 수 없음').strip()
            # Remove ANSI colors if any
            percent = re.sub(r'\x1b\[([0-9,A-Z]{1,2}(;[0-9]{1,2})?(;[0-9]{3})?)?[m|K]?', '', percent)
            self.progress_update.emit(f"다운로드 진행률: {percent}")
        elif d['status'] == 'finished':
            self.progress_update.emit("다운로드 완료 처리 중...")
            
    def run(self):
        result = logic.download_video(self.url, self.hook)
        self.finished_signal.emit(result)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Info Viewer")
        self.setMinimumSize(640, 520)
        
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        
        # 1. Top Section (Input)
        top_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("유튜브 링크를 입력하세요")
        self.fetch_btn = QPushButton("정보 가져오기")
        self.fetch_btn.clicked.connect(self.on_fetch_clicked)
        
        self.download_btn = QPushButton("다운로드")
        self.download_btn.clicked.connect(self.on_download_clicked)
        self.download_btn.setEnabled(False)  # 초기에는 비활성화
        
        top_layout.addWidget(self.url_input)
        top_layout.addWidget(self.fetch_btn)
        top_layout.addWidget(self.download_btn)
        main_layout.addLayout(top_layout)
        
        # 2. Middle Section (Thumbnail)
        self.img_label = QLabel("유튜브 링크를 입력하고 정보를 가져오세요.")
        self.img_label.setAlignment(Qt.AlignCenter)
        self.img_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        self.img_label.setMinimumHeight(340)
        main_layout.addWidget(self.img_label)
        
        # 3. Bottom Section (Metadata)
        self.title_label = QLabel("")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        self.title_label.setFont(title_font)
        self.title_label.setWordWrap(True)
        
        self.views_label = QLabel("")
        views_font = QFont()
        views_font.setPointSize(12)
        self.views_label.setFont(views_font)
        
        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet("color: #2e7d32; font-weight: bold;")
        
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.views_label)
        main_layout.addWidget(self.progress_label)
        
        central_widget.setLayout(main_layout)
        
        # 4. Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("대기 중")
        
    def on_fetch_clicked(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "입력 오류", "유튜브 링크를 입력해주세요.")
            return
            
        self.fetch_btn.setEnabled(False)
        self.download_btn.setEnabled(False)
        self.url_input.setEnabled(False)
        self.status_bar.showMessage("정보를 불러오는 중...")
        self.img_label.setText("동영상 정보를 가져오는 중입니다...")
        self.title_label.clear()
        self.views_label.clear()
        
        self.thread = FetchThread(url)
        self.thread.result_ready.connect(self.on_fetch_finished)
        self.thread.start()
        
    def on_fetch_finished(self, info_result, img_data):
        self.fetch_btn.setEnabled(True)
        self.url_input.setEnabled(True)
        
        if not info_result.get('success'):
            self.status_bar.showMessage("에러 발생")
            self.img_label.setText("이미지 통신 에러")
            QMessageBox.critical(self, "에러", info_result.get('error_msg', '알 수 없는 에러'))
            return
            
        self.status_bar.showMessage("정보 가져오기 성공")
        
        title = info_result.get('title', '')
        views = info_result.get('view_count', 0)
        
        self.title_label.setText(title)
        self.views_label.setText(f"조회수: {views:,}회" if views else "조회수 정보 없음")
        self.current_url = self.url_input.text().strip()
        self.download_btn.setEnabled(True)
        self.progress_label.clear()
        
        if img_data:
            pixmap = QPixmap()
            pixmap.loadFromData(img_data)
            # Resize image cleanly to fit inside the label
            scaled_pixmap = pixmap.scaled(self.img_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.img_label.setPixmap(scaled_pixmap)
        else:
            self.img_label.setText("이 영상의 썸네일을 불러올 수 없습니다.")

    def on_download_clicked(self):
        url = getattr(self, 'current_url', None) or self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "오류", "먼저 유효한 링크를 조회해주세요.")
            return
            
        self.fetch_btn.setEnabled(False)
        self.download_btn.setEnabled(False)
        self.url_input.setEnabled(False)
        
        self.progress_label.setText("다운로드 준비 중...")
        
        self.download_thread = DownloadThread(url)
        self.download_thread.progress_update.connect(self.on_download_progress)
        self.download_thread.finished_signal.connect(self.on_download_finished)
        self.download_thread.start()
        
    def on_download_progress(self, msg):
        self.progress_label.setText(msg)
        self.status_bar.showMessage(msg)
        
    def on_download_finished(self, result):
        self.fetch_btn.setEnabled(True)
        self.download_btn.setEnabled(True)
        self.url_input.setEnabled(True)
        
        if result.get('success'):
            self.progress_label.setText("다운로드 완료! (Downloads 폴더를 확인하세요)")
            self.status_bar.showMessage("다운로드 완료")
            QMessageBox.information(self, "완료", "다운로드가 완료되었습니다.")
        else:
            self.progress_label.setText("다운로드 실패")
            self.status_bar.showMessage("다운로드 에러")
            QMessageBox.critical(self, "에러", result.get('error_msg', '알 수 없는 다운로드 에러'))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
