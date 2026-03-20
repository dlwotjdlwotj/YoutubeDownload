Cursor의 기술 검토 의견을 반영하여, **관심사 분리(SoC)**와 **비동기 처리(QThread)**를 강조한 더욱 견고한 plan.md 수정안입니다.

📝 YouTube Info Viewer 프로젝트 계획서 (V2)
1. 프로젝트 개요

yt-dlp를 활용하여 유튜브 영상 URL로부터 메타데이터(제목, 조회수, 썸네일)를 추출하고, PyQt5 GUI를 통해 사용자에게 시각적으로 정보를 제공하는 데스크톱 애플리케이션을 개발합니다.

2. 기술 스택 및 라이브러리

GUI: PyQt5

Data Extraction: yt-dlp

Image Handling: requests (썸네일 다운로드), QPixmap

Async Processing: QThread (UI 프리징 방지)

3. 시스템 아키텍처 (관심사 분리)

유지보수와 확장을 위해 로직과 UI를 엄격히 분리합니다.

main.py: QMainWindow 클래스 정의, 위젯 배치, 이벤트 시그널 처리 및 UI 업데이트 로직.

logic.py: yt-dlp를 이용한 데이터 파싱 함수 및 이미지 데이터 로드 함수 관리.

memory_bank/: 프로젝트의 맥락과 기술적 결정을 기록하는 문서 저장소.

4. 상세 UI 레이아웃 설계

입력 영역 (Top):

QLineEdit: 유튜브 URL 입력 (Placeholder: "유튜브 링크를 입력하세요")

QPushButton: "정보 가져오기" (조회 실행)

정보 표시 영역 (Middle/Bottom):

QLabel (Thumbnail): 썸네일 표시 (고정 너비 480px 또는 640px, 비율 유지)

QLabel (Title): 영상 제목 (폰트 크기 확대 및 Bold 적용)

QLabel (Views): 조회수 (천 단위 콤마 포맷팅 적용)

상태 바 (Status Bar):

조회 중 "정보를 불러오는 중..." 또는 에러 메시지 출력

5. 단계별 구현 계획
0단계: Memory Bank 동기화 (SSOT 구축)

projectbrief.md, techContext.md 등에 현재 설계 구조 반영.

1단계: 환경 설정 및 의존성 설치

pip install PyQt5 yt-dlp requests

2단계: 로직 모듈 (logic.py) 개발

extract_video_info(url): 제목, 썸네일 URL, 조회수를 딕셔너리 형태로 반환.

예외 처리: 유효하지 않은 URL 입력 시 에러 핸들링.

3단계: 기본 UI 및 QThread 연동 (main.py)

UI 기본 골격 작성.

Worker Thread 구현: 네트워크 요청(yt-dlp)이 실행되는 동안 메인 UI가 멈추지 않도록 QThread와 pyqtSignal 사용.

4단계: 데이터 바인딩 및 완성

썸네일 이미지 비동기 로딩 및 UI 업데이트.

조회수 포맷팅(예: 1,234,567회) 및 제목 레이아웃 최적화.

6. 기술적 고려 사항 (Risk Mitigation)

UI 프리징 방지: yt-dlp가 정보를 가져오는 동안 GUI가 응답 없음 상태가 되지 않도록 별도 스레드에서 작업 수행.

데이터 유효성: URL 형식이 잘못되었거나 네트워크 연결이 끊긴 경우 QMessageBox를 통해 사용자에게 알림.

이제 이 계획을 바탕으로 ACT 모드로 넘어가서 다음 순서대로 진행해도 될까요?

Memory Bank 파일들(projectbrief.md 등) 생성/업데이트

의존성 라이브러리 설치

logic.py 작성

main.py 작성

승인해 주시면 바로 실행에 옮기겠습니다!