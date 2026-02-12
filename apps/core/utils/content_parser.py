from __future__ import annotations

import re
from typing import List, Optional

from apps.core.constants import ALLOWED_IMAGE_EXTENSIONS


class ContentParser:
    """
    질문 본문(Markdown 등)에서 정보를 추출하는 유틸리티 클래스
    """

    @staticmethod
    def _build_image_extension_pattern() -> str:
        """허용된 이미지 확장자를 기반으로 정규식 패턴 생성"""
        # {".jpg", ".jpeg", ".png", ".gif"} → "jpg|jpeg|png|gif"
        exts = "|".join(ext.lstrip(".") for ext in ALLOWED_IMAGE_EXTENSIONS)
        return exts

    @classmethod
    def extract_thumbnail_img_url(cls, content: Optional[str]) -> Optional[str]:
        """본문 텍스트 내 이미지 태그를 찾아 첫 번째 이미지의 URL을 반환"""
        # 입력값 검증
        if not content or not isinstance(content, str):
            return None

        # 허용된 확장자 패턴 생성
        exts = cls._build_image_extension_pattern()

        # 마크다운 이미지 패턴: ![...](url.jpg)
        # 확장자 뒤의 )를 종료 시점으로 인식
        markdown_image_pattern = rf"!\[[^\]]*\]\(([^\s]+\.(?:{exts}))\)"
        match = re.search(markdown_image_pattern, content, re.IGNORECASE)
        if match:
            url = match.group(1).strip()
            if url:  # 빈 URL이 아닌지 확인
                return url

        # HTML 이미지 태그 패턴: <img src="url">
        html_image_pattern = rf'<img\s+[^>]*src=["\'"]([^"\']+\.(?:{exts}))["\'"]'
        match = re.search(html_image_pattern, content, re.IGNORECASE)
        if match:
            url = match.group(1).strip()
            if url:  # 빈 URL이 아닌지 확인
                return url

        return None

    @classmethod
    def extract_content_preview(cls, content: Optional[str], limit: int) -> Optional[str]:
        """목록 조회를 위해 이미지 태그 제거 텍스트, 썸네일 URL 반환"""
        # 입력값 검증
        if not content or not isinstance(content, str):
            return ""

        # 허용된 확장자 패턴 생성
        exts = cls._build_image_extension_pattern()

        # 이미지 태그 제거 (마크다운 & HTML)
        clean_text = re.sub(rf"!\[[^\]]*\]\([^\s]+\.(?:{exts})\)", "", content, flags=re.IGNORECASE)
        clean_text = re.sub(r"<img\s+[^>]*>", "", clean_text)

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

        # 허용된 확장자 패턴 생성
        exts = cls._build_image_extension_pattern()

        # 마크다운 이미지 패턴 추출 (![alt](url.jpg))
        # 확장자 뒤의 )를 종료 시점으로 인식
        markdown_image_pattern = rf"!\[[^\]]*\]\(([^\s]+\.(?:{exts}))\)"
        urls.extend(re.findall(markdown_image_pattern, content, re.IGNORECASE))

        # HTML 이미지 태그 패턴 추출 (<img src="url.jpg">)
        # 작은따옴표와 큰따옴표 모두 지원
        html_image_pattern = rf'<img\s+[^>]*src=["\'"]([^"\']+\.(?:{exts}))["\'"]'
        urls.extend(re.findall(html_image_pattern, content, re.IGNORECASE))

        # 빈 URL 제거 및 공백 정리
        urls = [url.strip() for url in urls if url.strip()]

        # 중복 제거 (순서 유지)
        return list(dict.fromkeys(urls))
