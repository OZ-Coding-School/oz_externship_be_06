import re
from typing import Optional


class ContentParser:
    """
    질문 본문(Markdown 등)에서 정보를 추출하는 유틸리티 클래스
    """

    @staticmethod
    def extract_thumbnail_img_url(content: str) -> Optional[str]:
        """본문 텍스트 내 이미지 태그를 찾아 첫 번째 이미지의 URL을 반환"""
        # 마크다운 이미지 패턴: ![...](url)
        markdown_image_pattern = r"!\[.*?\]\((.*?)\)"
        match = re.search(markdown_image_pattern, content)
        if match:
            return match.group(1)

        # HTML 이미지 태그 패턴: <img src="url">
        html_image_pattern = r'<img [^>]*src="([^"]+)"'
        match = re.search(html_image_pattern, content)
        if match:
            return match.group(1)

        return None
