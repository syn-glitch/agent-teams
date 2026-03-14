"""T-002: 인스타 릴스 다운로드 + 캡션/메타데이터 추출"""

import json
import os
import re
import subprocess


def extract_shortcode(url: str) -> str:
    """URL에서 릴스 shortcode 추출"""
    match = re.search(r'/reel/([A-Za-z0-9_-]+)', url)
    if not match:
        raise ValueError(f"유효한 릴스 URL이 아닙니다: {url}")
    return match.group(1)


def download_reel(url: str, base_dir: str = "downloads") -> dict:
    """릴스 영상 다운로드 + 캡션/메타데이터 추출

    Returns:
        dict with keys: video_path, metadata_path, caption, username, shortcode, duration
    """
    shortcode = extract_shortcode(url)

    # 1단계: 메타데이터 먼저 추출 (다운로드 없이)
    meta_cmd = [
        "yt-dlp",
        "--dump-json",
        "--no-download",
        url,
    ]
    result = subprocess.run(meta_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"메타데이터 추출 실패: {result.stderr}")

    metadata = json.loads(result.stdout)
    username = metadata.get("uploader_id", metadata.get("channel", "unknown"))
    caption = metadata.get("description", "")
    duration = metadata.get("duration", 0)

    # 디렉토리 생성
    output_dir = os.path.join(base_dir, f"{username}_{shortcode}")
    os.makedirs(output_dir, exist_ok=True)

    # 메타데이터 저장
    metadata_path = os.path.join(output_dir, "metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    # 2단계: 영상 다운로드
    video_path = os.path.join(output_dir, "video.mp4")
    dl_cmd = [
        "yt-dlp",
        "-o", video_path,
        "--format", "best[ext=mp4]/best",
        "--no-overwrites",
        url,
    ]
    result = subprocess.run(dl_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"영상 다운로드 실패: {result.stderr}")

    # 캡션 저장
    caption_path = os.path.join(output_dir, "caption.txt")
    with open(caption_path, "w", encoding="utf-8") as f:
        f.write(caption)

    return {
        "video_path": video_path,
        "metadata_path": metadata_path,
        "caption": caption,
        "username": username,
        "shortcode": shortcode,
        "duration": duration,
        "output_dir": output_dir,
    }
