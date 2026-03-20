# System Patterns

- **관심사 분리 (SoC)**
  - `main.py`: QMainWindow 클래스 정의, 위젯 배치, 이벤트/시그널 처리 및 UI 업데이트
  - `logic.py`: yt-dlp 래핑 담당 (정보 추출, 고화질 영상/오디오 분리 다운로드 및 병합, 이미지 HTTP 통신 담당)
- **비동기 처리**
  - 네트워크 I/O(yt-dlp 메타데이터 파싱, 영상 다운로드) 진행 시 PyQt GUI 멈춤(Freezing) 방지를 위해 `QThread` 및 `pyqtSignal`을 사용하여 백그라운드 처리.
  - 별도의 `FetchThread`와 `DownloadThread`를 각각 운영하여 UI가 블로킹되지 않도록 구성.
  - yt-dlp의 `progress_hooks`를 이용해 다운로드 중 실시간 진행률 퍼센트를 스레드를 통해 GUI로 전달.
