# Private Google Meet Summarizer

An on-device Python prototype that turns a meeting audio recording into a transcript and a structured Markdown summary. It uses Faster-Whisper for speech recognition. Audio is processed on the computer running the app; the application does not sign in to, join, or control Google Meet.

## Before recording

Get clear consent from all participants and comply with your organisation's policies and local recording laws. Google Meet may provide its own recording/transcript facilities for eligible accounts; use them when appropriate and provide the downloaded audio to this tool.

## Install and run (Windows PowerShell)

```powershell
cd "C:\Users\tapas\OneDrive\Desktop\AI PROJECT\google_meet_summarizer"
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Open the local link printed by Streamlit (normally `http://localhost:8501`), upload an audio/video recording, choose a model, and select **Transcribe and summarize**.

## Model choices

- `base`: good quick default for CPU use.
- `small`: better accuracy, slower and larger download.
- `medium`: better for difficult audio, substantially slower on CPU.

The selected Whisper model is downloaded automatically on the first run and then cached locally. Outputs are saved to `outputs/` and can be downloaded in the browser.

## Limitations and next development steps

The initial version identifies likely decisions, action items, and questions with transparent local rules. It does not reliably identify speakers. For higher-quality summaries, a future version can send the transcript to an organisation-approved LLM, or use a local LLM through Ollama. A Google Workspace integration would require an administrator-approved OAuth application and access only to recordings/transcripts the user is permitted to access.
