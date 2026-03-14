"""T-004: summary.md 통합 생성"""

import os
from datetime import datetime


def generate_summary(
    username: str,
    shortcode: str,
    url: str,
    caption: str,
    stt_text: str,
    duration: float,
    analysis: dict,
    output_dir: str,
) -> str:
    """caption + stt + insight → summary.md 통합 벤치마킹 시트 생성

    Returns:
        summary.md 파일 경로
    """
    keywords = ", ".join(analysis.get("keywords", []))
    action_points = "\n".join(
        f"   {i+1}. {point}"
        for i, point in enumerate(analysis.get("action_points", []))
    )

    summary = f"""# 릴스 벤치마킹 분석 — @{username}

---
- **분석일**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
- **URL**: {url}
- **계정**: @{username}
- **영상 길이**: {duration}초
---

## 캡션

{caption or "(캡션 없음)"}

## 음성 대본 (STT)

{stt_text or "(음성 없음)"}

## 벤치마킹 분석

| 항목 | 분석 결과 |
|------|----------|
| 훅 포인트 | {analysis.get("hook_point", "-")} |
| 훅 라인 | {analysis.get("hook_line", "-")} |
| CTA | {analysis.get("cta", "-")} |
| 콘텐츠 구조 | {analysis.get("content_structure", "-")} |
| 핵심 키워드 | {keywords or "-"} |
| 톤 앤 매너 | {analysis.get("tone", "-")} |
| 적용 난이도 | {analysis.get("difficulty", "-")} |

## 우리 채널 적용 포인트

{action_points or "   (없음)"}
"""

    summary_path = os.path.join(output_dir, "summary.md")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary)

    return summary_path
