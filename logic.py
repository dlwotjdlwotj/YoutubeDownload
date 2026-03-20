import os
import yt_dlp
import requests

def extract_video_info(url: str) -> dict:
    """
    유튜브 URL에서 영상 정보를 추출합니다.
    :param url: 유튜브 영상 URL
    :return: 성공 시 {'success': True, 'title': str, 'thumbnail_url': str, 'view_count': int}
             실패 시 {'success': False, 'error_msg': str}
    """
    ydl_opts = {
        'skip_download': True,
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            
            title = info_dict.get('title', '제목 없음')
            thumbnail_url = info_dict.get('thumbnail', '')
            view_count = info_dict.get('view_count', 0)
            
            return {
                'success': True,
                'title': title,
                'thumbnail_url': thumbnail_url,
                'view_count': view_count
            }
    except yt_dlp.utils.DownloadError as e:
        return {
            'success': False,
            'error_msg': '유효하지 않은 URL이거나 영상 정보를 찾을 수 없습니다.'
        }
    except Exception as e:
        return {
            'success': False,
            'error_msg': f'알 수 없는 에러가 발생했습니다: {str(e)}'
        }

def download_image(url: str) -> bytes:
    """
    주어진 URL에서 이미지를 다운로드하여 바이트 데이터로 반환합니다.
    :param url: 이미지 URL
    :return: 이미지 데이터 바이트 배열 (실패 시 None)
    """
    if not url:
        return None
        
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.content
    except Exception:
        return None

def download_video(url: str, progress_hook=None) -> dict:
    """
    유튜브 URL에서 영상을 시스템의 Downloads 폴더로 다운로드합니다.
    """
    downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
    
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best',
        'outtmpl': os.path.join(downloads_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'merge_output_format': 'mp4',
    }
    
    if progress_hook:
        ydl_opts['progress_hooks'] = [progress_hook]
        
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            return {'success': True}
    except Exception as e:
        return {'success': False, 'error_msg': str(e)}
