"""Local meeting transcription and summarisation app.

This app does not join meetings, bypass Google Meet permissions, or upload audio.
It processes an audio recording that the user provides or records from a selected
audio input. Ensure every participant has agreed before recording.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st
from faster_whisper import WhisperModel


APP_DIR = Path(__file__).parent
OUTPUT_DIR = APP_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


@st.cache_resource(show_spinner=False)
def load_whisper(model_size: str) -> WhisperModel:
    """Load an on-device speech-to-text model (downloaded once on first use)."""
    # CPU-safe default. Use CUDA automatically only when explicitly configured.
    device = os.getenv("WHISPER_DEVICE", "cpu")
    compute_type = "float16" if device == "cuda" else "int8"
    return WhisperModel(model_size, device=device, compute_type=compute_type)


def transcribe(audio_path: str, model_size: str) -> tuple[str, list[dict[str, Any]], str]:
    model = load_whisper(model_size)
    segments, info = model.transcribe(
        audio_path,
        beam_size=5,
        vad_filter=True,
        word_timestamps=False,
    )
    rows = [
        {"start": round(s.start, 1), "end": round(s.end, 1), "text": s.text.strip()}
        for s in segments
        if s.text.strip()
    ]
    return "\n".join(item["text"] for item in rows), rows, info.language


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.replace("\n", " ")) if len(s.strip()) > 20]


def extractive_summary(text: str, max_sentences: int = 5) -> str:
    """Small offline fallback summary; no API key or cloud model required."""
    sentences = _sentences(text)
    if not sentences:
        return "No usable speech was detected."
    tokens = re.findall(r"[a-zA-Z']+", text.lower())
    stop = {"the", "a", "an", "and", "or", "to", "of", "in", "is", "it", "that", "we", "i", "for", "on", "with", "this", "was", "are", "be", "as", "at", "from"}
    freq = Counter(t for t in tokens if t not in stop and len(t) > 2)
    scored = []
    for i, sentence in enumerate(sentences):
        words = re.findall(r"[a-zA-Z']+", sentence.lower())
        score = sum(freq[w] for w in words if w in freq) / max(len(words), 1)
        scored.append((score, i, sentence))
    chosen = sorted(sorted(scored, reverse=True)[:max_sentences], key=lambda item: item[1])
    return " ".join(item[2] for item in chosen)


def make_report(transcript: str, language: str) -> str:
    sentences = _sentences(transcript)
    action_markers = ("will ", "need to", "action", "follow up", "follow-up", "deadline", "by friday", "by monday", "assigned", "responsible")
    questions = [s for s in sentences if "?" in s or s.lower().startswith(("how ", "what ", "when ", "who ", "why "))]
    actions = [s for s in sentences if any(marker in s.lower() for marker in action_markers)]
    decisions = [s for s in sentences if any(marker in s.lower() for marker in ("decided", "agreed", "approve", "chosen", "plan is"))]
    bullet = lambda entries, fallback: "\n".join(f"- {x}" for x in entries[:8]) if entries else f"- {fallback}"
    return f"""# Meeting summary

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}  
Detected language: {language}

## Overview

{extractive_summary(transcript)}

## Decisions

{bullet(decisions, 'No explicit decisions detected; review the transcript.')}

## Action items

{bullet(actions, 'No action items were automatically detected.')}

## Open questions

{bullet(questions, 'No open questions were automatically detected.')}

## Transcript

{transcript}
"""


st.set_page_config(page_title="Private Meeting Summarizer", page_icon="📝", layout="centered")
st.title("📝 Private Meeting Summarizer")
st.caption("Transcribe a Google Meet recording locally and produce a structured summary.")
st.warning("Only record or upload meetings when all participants have been informed and consented. This tool does not join Google Meet or access it automatically.")

with st.sidebar:
    model_size = st.selectbox("Speech model", ["base", "small", "medium"], index=0, help="`base` is quickest; `small` is usually more accurate. First use downloads the selected model.")
    st.caption("All transcription runs on this computer. The first model download requires internet access.")

uploaded = st.file_uploader("Upload a meeting recording", type=["mp3", "wav", "m4a", "mp4", "webm", "ogg"])
if uploaded:
    suffix = Path(uploaded.name).suffix or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded.getbuffer())
        temp_path = tmp.name
    st.audio(uploaded)
    if st.button("Transcribe and summarize", type="primary"):
        try:
            with st.spinner("Transcribing audio locally…"):
                transcript, segments, language = transcribe(temp_path, model_size)
            report = make_report(transcript, language)
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = OUTPUT_DIR / f"meeting_summary_{stamp}.md"
            report_path.write_text(report, encoding="utf-8")
            st.success(f"Done. Saved locally as {report_path.name}")
            st.markdown(report)
            st.download_button("Download report (.md)", report, file_name=report_path.name, mime="text/markdown")
            st.download_button("Download transcript (.json)", json.dumps(segments, indent=2), file_name=f"transcript_{stamp}.json", mime="application/json")
        except Exception as exc:
            st.error(f"Could not process the recording: {exc}")
        finally:
            Path(temp_path).unlink(missing_ok=True)
else:
    st.info("Export or record the meeting audio, then upload it here. For live Google Meet audio, configure a consented system-audio recording device separately and upload the resulting file.")
