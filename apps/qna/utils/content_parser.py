from __future__ import annotations

import re
from typing import List, Optional


class ContentParser:
    """
    질문 본문(Markdown 등)에서 정보를 추출하는 유틸리티 클래스
    """

    @classmethod
    def extract_thumbnail_img_url(cls, content: Optional[str]) -> Optional[str]:
        """본문 텍스트 내 이미지 태그를 찾아 첫 번째 이미지의 URL을 반환"""
        # 입력값 검증
        if not content or not isinstance(content, str):
            return None

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

    @classmethod
    def extract_content_preview(cls, content: Optional[str], limit: int) -> Optional[str]:
        """목록 조회를 위해 이미지 태그 제거 텍스트, 썸네일 URL 반환"""
        # 입력값 검증
        if not content or not isinstance(content, str):
            return ""

        # 이미지 태그 제거 (마크다운 & HTML)
        clean_text = re.sub(r"!\[.*?\]\(.*?\)", "", content)
        clean_text = re.sub(r"<img [^>]*>", "", clean_text)

        # 불필요한 공백 및 줄바꿈 정리
        clean_text = re.sub(r"\s+", " ", clean_text).strip()

        # 텍스트가 없을 경우 처리
        if not clean_text:
            clean_text = ""

        preview = clean_text[:limit] + "..." if len(clean_text) > limit else clean_text

        return preview

    @classmethod
    def extract_all_image_urls(cls, content: str) -> List[str]:
        """본문 텍스트 내의 모든 이미지 URL(Markdown, HTML)을 추출하여 리스트로 반환"""
        urls: List[str] = []

        # 1. 마크다운 이미지 패턴 추출 (![alt](url))
        markdown_image_pattern = r"!\[.*?\]\((.*?)\)"
        urls.extend(re.findall(markdown_image_pattern, content))

        # 2. HTML 이미지 태그 패턴 추출 (<img src="url">)
        html_image_pattern = r'<img [^>]*src="([^"]+)"'
        urls.extend(re.findall(html_image_pattern, content))

        # 3. 중복 제거 (순서 유지)
        return list(dict.fromkeys(urls))
