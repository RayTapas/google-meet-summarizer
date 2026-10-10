# Private Google Meet Summarizer

An on-device Python prototype that turns a meeting audio recording into a transcript and a structured Markdown summary. It uses Faster-Whisper for speech recognition. Audio is processed on the computer running the app; the application does not sign in to, join, or control Google Meet.

## Before recording

Google Meet may provide its own recording/transcript facilities for eligible accounts; use them when appropriate and provide the downloaded audio to this tool.

## Model choices

The selected Whisper model is downloaded automatically on the first run and then cached locally. Outputs are saved to `outputs/` and can be downloaded in the browser.

## Limitations and next development steps

The initial version identifies likely decisions, action items, and questions with transparent local rules. It does not reliably identify speakers. For higher-quality summaries, a future version can send the transcript to an organisation-approved LLM, or use a local LLM through Ollama. A Google Workspace integration would require an administrator-approved OAuth application and access only to recordings/transcripts the user is permitted to access.
