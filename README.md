# NewsDub AI

A beginner-friendly Flask app that fetches the latest news headlines, translates them into Indian languages using the [Sarvam AI Translation API](https://docs.sarvam.ai/api-reference-docs/api-guides-tutorials/text-processing/translation.mdx), and reads them aloud with the [Sarvam Bulbul v3 Text-to-Speech API](https://docs.sarvam.ai/api-reference-docs/getting-started/models/bulbul.mdx).

## Features

- Fetches the latest **5 headlines** from BBC News RSS (configurable)
- Displays headline title and summary on selection
- Translates to **10 Indian languages** supported by both Sarvam Translation and TTS
- Generates natural speech with **bulbul:v3**
- Plays audio in the browser and allows download

## Project Structure

```
NewsDub - Sarvam/
├── app.py                  # Flask routes and app setup
├── requirements.txt
├── .env.example
├── services/
│   ├── rss_service.py      # RSS feed fetching
│   ├── translation_service.py  # Sarvam translation
│   └── tts_service.py      # Sarvam text-to-speech
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── script.js
└── generated_audio/        # Saved WAV files (gitignored)
```

## Prerequisites

- Python 3.10 or newer
- A [Sarvam AI API key](https://dashboard.sarvam.ai)

## Setup

1. **Clone or download** this project and open a terminal in the project folder.

2. **Create a virtual environment** (recommended):

   ```bash
   python -m venv venv
   ```

   Activate it:

   - Windows (PowerShell): `.\venv\Scripts\Activate.ps1`
   - macOS/Linux: `source venv/bin/activate`

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:

   ```bash
   copy .env.example .env
   ```

   Edit `.env` and set your `SARVAM_API_KEY`.

5. **Run the app**:

   ```bash
   python app.py
   ```

6. Open **http://localhost:5000** in your browser.

## How It Works

1. **Headlines** — `rss_service.py` uses `feedparser` to read the BBC RSS feed.
2. **Translation** — `translation_service.py` calls `client.text.translate()` with `mayura:v1`.
3. **Speech** — `tts_service.py` calls `client.text_to_speech.convert()` with `bulbul:v3`, decodes the base64 `audios` response, and saves a WAV file.
4. **Frontend** — Vanilla JavaScript calls Flask JSON APIs and plays the returned audio.

## Supported Languages

These languages work with both Sarvam Translation (`mayura:v1`) and TTS (`bulbul:v3`):

| Code   | Language  |
|--------|-----------|
| hi-IN  | Hindi     |
| bn-IN  | Bengali   |
| ta-IN  | Tamil     |
| te-IN  | Telugu    |
| gu-IN  | Gujarati  |
| kn-IN  | Kannada   |
| ml-IN  | Malayalam |
| mr-IN  | Marathi   |
| pa-IN  | Punjabi   |
| od-IN  | Odia      |

## API Routes

| Method | Route                    | Description              |
|--------|--------------------------|--------------------------|
| GET    | `/`                      | Main page                |
| GET    | `/api/headlines`         | Latest headlines (JSON)  |
| POST   | `/api/translate`         | Translate text           |
| POST   | `/api/synthesize`        | Generate speech audio    |
| GET    | `/generated_audio/<file>`| Serve/download WAV files |
| GET    | `/api/languages`         | Supported languages      |

## Environment Variables

| Variable         | Required | Description                          |
|------------------|----------|--------------------------------------|
| `SARVAM_API_KEY` | Yes      | Your Sarvam AI API subscription key  |
| `RSS_FEED_URL`   | No       | RSS feed URL (default: BBC News)     |
| `FLASK_SECRET_KEY` | No     | Flask session secret                 |
| `FLASK_DEBUG`    | No       | Set to `true` for debug mode         |
| `FLASK_PORT`     | No       | Port number (default: 5000)          |

## Official Sarvam Documentation

- [Quickstart](https://docs.sarvam.ai/api-reference-docs/getting-started/quickstart)
- [Translation API](https://docs.sarvam.ai/api-reference-docs/api-guides-tutorials/text-processing/translation.mdx)
- [Bulbul TTS Model](https://docs.sarvam.ai/api-reference-docs/getting-started/models/bulbul.mdx)
- [TTS REST API](https://docs.sarvam.ai/api-reference-docs/text-to-speech/convert)

## License

This project is for educational purposes. News content is sourced from public RSS feeds. Sarvam AI usage is subject to [Sarvam's terms](https://sarvam.ai).
---

# 📸 Screenshots

## 🏠 Home Page

![Home Page](Screenshots/Home%20Page.png)

---

## 🌐 Translation Output

![Translation](Screenshots/Translated%20Text%20and%20Speech.png)

---

## 🔊 Audio Playback

![Audio](Screenshots/Audio%20Selection.png)