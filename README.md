# 🤖 Arabic Translation Discord Bot

A powerful Discord bot that **translates Arabic text and images** to Urdu and English using AI. Built with Google Gemini OCR and OpenRouter Llama 3.3 70B.

---

## ✨ Features

- 📝 **Text Translation** — Paste any Arabic text and get instant Urdu & English translations
- 🖼️ **Image Translation** — Send an image containing Arabic text and the bot extracts and translates it automatically
- 🌐 **Language Specific** — Choose to translate to Urdu only, English only, or both at once
- ⚡ **Fast & Reliable** — Powered by OpenRouter Llama 3.3 70B for translation and Google Gemini 2.0 Flash for OCR
- 🆓 **Completely Free** — Uses free tiers of all APIs
- 🟢 **24/7 Online** — Hosted on Render with UptimeRobot keep-alive

---

## 🚀 Commands

| Command | Shortcut | Description |
|---|---|---|
| `!translate <arabic>` | `!t` | Translate to **both** Urdu & English |
| `!urdu <arabic>` | `!u` | Translate to **Urdu only** |
| `!english <arabic>` | `!e` | Translate to **English only** |
| `!translate` + image | `!t` + image | Extract & translate Arabic from image (both) |
| `!urdu` + image | `!u` + image | Extract & translate Arabic from image (Urdu) |
| `!english` + image | `!e` + image | Extract & translate Arabic from image (English) |
| `!guide` | `!h` | Show full command guide |
| `!ping` | | Check bot status & latency |

---

## 🛠️ Tech Stack

| Service | Purpose |
|---|---|
| [discord.py](https://discordpy.readthedocs.io/) | Discord bot framework |
| [Google Gemini 2.0 Flash](https://aistudio.google.com/) | Arabic OCR from images |
| [OpenRouter](https://openrouter.ai/) + Llama 3.3 70B | Arabic → Urdu & English translation |
| [Flask](https://flask.palletsprojects.com/) | Keep-alive server |
| [Render](https://render.com/) | Free 24/7 hosting |
| [UptimeRobot](https://uptimerobot.com/) | Prevents Render from sleeping |

---

## 📋 Prerequisites

- Python 3.11+
- Discord Bot Token
- Google Gemini API Key (free at [aistudio.google.com](https://aistudio.google.com))
- OpenRouter API Key (free at [openrouter.ai](https://openrouter.ai))

---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Create `.env` file
```env
DISCORD_TOKEN=your_discord_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### 4. Run the bot
```bash
python bot.py
```

---

## 🌐 Deploy to Render (Free 24/7 Hosting)

1. Push your code to GitHub
2. Go to [render.com](https://render.com) and sign up with GitHub
3. Click **New** → **Web Service** → connect your repo
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `python bot.py`
6. Add environment variables:
   - `DISCORD_TOKEN`
   - `GEMINI_API_KEY`
   - `OPENROUTER_API_KEY`
7. Deploy!

### Keep Bot Alive with UptimeRobot
1. Go to [uptimerobot.com](https://uptimerobot.com)
2. Add new monitor → HTTP(s)
3. Enter your Render URL (e.g. `https://your-bot.onrender.com`)
4. Set interval to 5 minutes

---

## 📁 Project Structure

```
arabic-translation-bot/
├── bot.py              # Main bot code
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (never commit this!)
├── .gitignore          # Git ignore file
└── README.md           # This file
```

---

## 🔑 Getting API Keys

### Discord Bot Token
1. Go to [discord.com/developers/applications](https://discord.com/developers/applications)
2. Create new application → Bot → Reset Token
3. Enable **Message Content Intent**

### Google Gemini API Key (Free)
1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Click **Get API Key** → Create API Key
- Free tier: **1,500 requests/day**

### OpenRouter API Key (Free)
1. Go to [openrouter.ai](https://openrouter.ai)
2. Sign up → Keys → Create Key
- Uses `openrouter/auto` (free models)
- Virtually **unlimited** for normal usage

---

## 📊 Free Tier Limits

| Service | Free Limit |
|---|---|
| Gemini (image OCR) | 1,500 images/day |
| OpenRouter (translation) | Virtually unlimited |
| Render (hosting) | Free forever |
| UptimeRobot (monitoring) | Free forever |

---

## 🤝 Invite Bot to Your Server

Generate an invite link:
1. Go to [discord.com/developers/applications](https://discord.com/developers/applications)
2. OAuth2 → URL Generator
3. Select `bot` scope
4. Select permissions: `Read Messages`, `Send Messages`, `Add Reactions`, `Read Message History`
5. Copy and share the generated URL

---

## 📝 Example Usage

**Text Translation:**
```
User: !translate مرحبا كيف حالك
Bot: 
📝 Original Arabic: مرحبا كيف حالك
🇵🇰 Urdu: ہیلو آپ کیسے ہیں
🇬🇧 English: Hello, how are you
```

**Image Translation:**
```
User: [attaches image with Arabic text] !translate
Bot: 
📝 Extracted Arabic: [extracted text]
🇵🇰 Urdu: [urdu translation]
🇬🇧 English: [english translation]
```

---

## ⚠️ Important Notes

- Never commit your `.env` file to GitHub
- Keep all API keys secret
- Gemini quota resets every 24 hours
- Bot only responds to `!` commands — it does NOT auto-translate every message

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🙏 Credits

Built with ❤️ using:
- [discord.py](https://discordpy.readthedocs.io/)
- [Google Gemini](https://aistudio.google.com/)
- [OpenRouter](https://openrouter.ai/)
- [Llama 3.3 70B](https://www.llama.com/) by Meta
