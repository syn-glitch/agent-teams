"""T-004: Claude Haiku 벤치마킹 분석 (Structured Output)"""

import json
import os

import anthropic


ANALYSIS_PROMPT = """당신은 인스타그램 릴스 콘텐츠 분석 전문가입니다.
아래 릴스의 캡션과 음성 대본을 분석하여 벤치마킹 인사이트를 제공해주세요.

[캡션]
{caption}

[음성 대본]
{stt_text}

[영상 길이]
{duration}초

다음 항목을 JSON 형식으로 분석해주세요:
1. hook_point: 첫 3초 내 시청자 유인 요소
2. hook_line: 영상 시작 1~3초에 사용된 핵심 문장
3. cta: 행동 유도 문구 (팔로우, 저장 등). 없으면 "없음"
4. content_structure: 도입-전개-마무리 흐름 분석
5. keywords: 반복 사용된 주요 단어 (최대 5개, 배열)
6. tone: 정보형/감성형/유머형 분류 + 근거
7. difficulty: 우리 채널 적용 난이도 (상/중/하) + 이유
8. action_points: 우리 채널에서 벤치마킹할 수 있는 구체적 방안 3가지 (배열)

반드시 유효한 JSON만 출력하세요. 다른 텍스트 없이 JSON만 반환하세요."""


def analyze(caption: str, stt_text: str, duration: float, output_dir: str) -> dict:
    """캡션+STT 텍스트를 Claude Haiku로 벤치마킹 분석

    Returns:
        analysis dict
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")

    client = anthropic.Anthropic(api_key=api_key)

    prompt = ANALYSIS_PROMPT.format(
        caption=caption or "(캡션 없음)",
        stt_text=stt_text or "(음성 대본 없음)",
        duration=duration,
    )

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = message.content[0].text.strip()

    # JSON 파싱 (코드블록 감싸기 대응)
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        response_text = "\n".join(lines[1:-1])

    analysis = json.loads(response_text)

    # insight.txt 저장
    insight_path = os.path.join(output_dir, "insight.txt")
    with open(insight_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)

    return analysis
