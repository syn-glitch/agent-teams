"""인스타 릴스 텍스트 추출 + 벤치마킹 분석 CLI

Usage:
    python main.py <URL>
    python main.py <URL1> <URL2> ... (최대 10건)
"""

import argparse
import os
import sys
import time

from downloader import download_reel
from transcriber import transcribe
from analyzer import analyze
from reporter import generate_summary

MAX_URLS = 10
DELAY_SECONDS = 5


def process_reel(url: str, base_download_dir: str, base_output_dir: str) -> str:
    """단일 릴스 URL 처리 파이프라인"""

    print(f"\n{'='*60}")
    print(f"  처리 중: {url}")
    print(f"{'='*60}")

    # T-002: 다운로드 + 캡션 추출
    print("[1/4] 릴스 다운로드 + 캡션 추출...")
    info = download_reel(url, base_dir=base_download_dir)
    print(f"  > @{info['username']} | {info['duration']}초 | 다운로드 완료")

    # 출력 디렉토리
    output_dir = os.path.join(
        base_output_dir, f"{info['username']}_{info['shortcode']}"
    )
    os.makedirs(output_dir, exist_ok=True)

    # 캡션을 output에도 복사
    caption_path = os.path.join(output_dir, "caption.txt")
    with open(caption_path, "w", encoding="utf-8") as f:
        f.write(info["caption"])

    # T-003: STT
    print("[2/4] 음성 → 텍스트 변환 (OpenAI Whisper API)...")
    stt_text = transcribe(info["video_path"], output_dir)
    print(f"  > STT 완료 ({len(stt_text)}자)")

    # T-004: LLM 벤치마킹 분석
    print("[3/4] 벤치마킹 분석 (Claude Haiku)...")
    analysis = analyze(info["caption"], stt_text, info["duration"], output_dir)
    print(f"  > 분석 완료")

    # T-004: summary.md 생성
    print("[4/4] summary.md 생성...")
    summary_path = generate_summary(
        username=info["username"],
        shortcode=info["shortcode"],
        url=url,
        caption=info["caption"],
        stt_text=stt_text,
        duration=info["duration"],
        analysis=analysis,
        output_dir=output_dir,
    )
    print(f"  > 저장 완료: {summary_path}")

    return summary_path


def main():
    parser = argparse.ArgumentParser(
        description="인스타 릴스 텍스트 추출 + 벤치마킹 분석"
    )
    parser.add_argument("urls", nargs="+", help="인스타 릴스 URL (최대 10건)")
    args = parser.parse_args()

    urls = args.urls

    # Rate Limiting: 최대 10건
    if len(urls) > MAX_URLS:
        print(f"[오류] 최대 {MAX_URLS}건까지 처리 가능합니다. ({len(urls)}건 입력됨)")
        sys.exit(1)

    # 환경변수 확인
    if not os.environ.get("OPENAI_API_KEY"):
        print("[오류] OPENAI_API_KEY 환경변수를 설정해주세요.")
        sys.exit(1)
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("[오류] ANTHROPIC_API_KEY 환경변수를 설정해주세요.")
        sys.exit(1)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    download_dir = os.path.join(base_dir, "downloads")
    output_dir = os.path.join(base_dir, "output")

    results = []
    for i, url in enumerate(urls):
        try:
            summary_path = process_reel(url, download_dir, output_dir)
            results.append({"url": url, "status": "success", "path": summary_path})
        except Exception as e:
            print(f"\n[오류] {url}: {e}")
            results.append({"url": url, "status": "error", "error": str(e)})

        # Rate Limiting: 다건 처리 시 5초 대기
        if i < len(urls) - 1:
            print(f"\n  ... {DELAY_SECONDS}초 대기 (Rate Limiting) ...")
            time.sleep(DELAY_SECONDS)

    # 결과 요약
    print(f"\n{'='*60}")
    print("  처리 완료")
    print(f"{'='*60}")
    success = sum(1 for r in results if r["status"] == "success")
    print(f"  성공: {success}/{len(results)}건")
    for r in results:
        status = "✅" if r["status"] == "success" else "❌"
        detail = r.get("path", r.get("error", ""))
        print(f"  {status} {r['url']}")
        if detail:
            print(f"     → {detail}")


if __name__ == "__main__":
    main()
