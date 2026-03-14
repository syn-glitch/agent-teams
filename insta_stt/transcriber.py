"""T-003: 오디오 추출 + OpenAI Whisper API STT"""

import os
import subprocess

from openai import OpenAI


def extract_audio(video_path: str, audio_path: str = None) -> str:
    """ffmpeg로 영상에서 오디오(.mp3) 추출"""
    if audio_path is None:
        audio_path = os.path.splitext(video_path)[0] + ".mp3"

    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-vn",
        "-acodec", "libmp3lame",
        "-q:a", "4",
        "-y",
        audio_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"오디오 추출 실패: {result.stderr}")

    return audio_path


def transcribe(video_path: str, output_dir: str) -> str:
    """영상에서 오디오 추출 → OpenAI Whisper API로 STT

    Returns:
        transcribed text
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")

    # 오디오 추출
    audio_path = os.path.join(output_dir, "audio.mp3")
    extract_audio(video_path, audio_path)

    # Whisper API 호출
    client = OpenAI(api_key=api_key)
    with open(audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="ko",
            response_format="text",
        )

    # STT 결과 저장
    stt_path = os.path.join(output_dir, "stt.txt")
    with open(stt_path, "w", encoding="utf-8") as f:
        f.write(transcript)

    # 오디오 파일 정리 (용량 절약)
    os.remove(audio_path)

    return transcript
