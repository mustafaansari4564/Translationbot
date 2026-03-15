import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import aiohttp
import re
import base64
import asyncio
from flask import Flask
from threading import Thread

# ── Keep-alive server ────────────────────────────────────────────────────────
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive! 🤖"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run_flask, daemon=True).start()

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
MODEL = "openrouter/auto"

# ── Bot setup ────────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ── Helpers ──────────────────────────────────────────────────────────────────

def contains_arabic(text):
    return bool(re.search(r'[\u0600-\u06FF]', text))

async def ask_llama(prompt, retries=3):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://discord-translation-bot.com",
        "X-Title": "Arabic Translation Bot"
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a professional Arabic translator. Translate accurately and completely."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 4000
    }
    for attempt in range(retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(OPENROUTER_URL, headers=headers, json=payload) as resp:
                    data = await resp.json()
            if "error" in data:
                error_msg = data["error"].get("message", "Unknown error")
                if "rate" in error_msg.lower():
                    await asyncio.sleep(10)
                    continue
                return f"ERROR: {error_msg}"
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Exception (attempt {attempt+1}): {e}")
            await asyncio.sleep(5)
    return "FAILED"

async def extract_arabic_from_image(image_bytes, mime_type):
    image_b64 = base64.b64encode(image_bytes).decode('utf-8')
    prompt = "Extract all Arabic text from this image exactly as written. Return ONLY the Arabic text. If no Arabic found, return: NONE"
    payload = {
        "contents": [{"parts": [
            {"inline_data": {"mime_type": mime_type, "data": image_b64}},
            {"text": prompt}
        ]}]
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{GEMINI_URL}?key={GEMINI_API_KEY}", json=payload) as resp:
            data = await resp.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError):
        return ""

async def translate_to_language(arabic_text, language):
    prompt = f"""Translate the COMPLETE Arabic text below to {language}.
Do not skip or truncate any part. Return ONLY the {language} translation.

Arabic text:
{arabic_text}"""
    return await ask_llama(prompt)

async def translate_both(arabic_text):
    prompt = f"""Translate the COMPLETE Arabic text below to both Urdu and English.
Do not skip or truncate any part.

Arabic text:
{arabic_text}

Respond in EXACTLY this format:
URDU: [complete urdu translation]
ENGLISH: [complete english translation]"""
    response = await ask_llama(prompt)
    result = {"urdu": "", "english": ""}
    if response in ["FAILED"] or response.startswith("ERROR:"):
        result["urdu"] = response
        result["english"] = response
        return result
    for line in response.strip().split('\n'):
        line = line.strip()
        if line.upper().startswith("URDU:"):
            result["urdu"] = line[5:].strip()
        elif line.upper().startswith("ENGLISH:"):
            result["english"] = line[8:].strip()
    if not result["urdu"] and not result["english"]:
        result["english"] = response[:500]
        result["urdu"] = "Could not parse"
    return result

def add_long_field(embed, name, value):
    chunks = [value[i:i+1024] for i in range(0, len(value), 1024)]
    for i, chunk in enumerate(chunks):
        embed.add_field(name=name if i == 0 else f"{name} (cont.)", value=chunk, inline=False)

async def get_image_arabic(ctx):
    attachment = ctx.message.attachments[0]
    if not attachment.content_type or not attachment.content_type.startswith("image/"):
        await ctx.reply("⚠️ Please attach a valid image.")
        return None
    await ctx.message.add_reaction("⏳")
    async with aiohttp.ClientSession() as session:
        async with session.get(attachment.url) as resp:
            image_bytes = await resp.read()
    extracted = await extract_arabic_from_image(image_bytes, attachment.content_type)
    await ctx.message.remove_reaction("⏳", bot.user)
    if not extracted or extracted.upper() == "NONE":
        await ctx.reply("🖼️ No Arabic text found in this image.")
        return None
    return extracted

# ── Events ───────────────────────────────────────────────────────────────────

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    print(f"OpenRouter: {'✅' if OPENROUTER_API_KEY else '❌'} | Gemini: {'✅' if GEMINI_API_KEY else '❌'}")

# ── Commands ─────────────────────────────────────────────────────────────────

@bot.command(name="urdu", aliases=["u", "ur"])
async def translate_urdu(ctx, *, text=None):
    """Translate Arabic to Urdu only"""
    if ctx.message.attachments:
        arabic = await get_image_arabic(ctx)
        if not arabic:
            return
        async with ctx.typing():
            translation = await translate_to_language(arabic, "Urdu")
        embed = discord.Embed(title="🇵🇰 Urdu Translation", color=0x00f3ff)
        add_long_field(embed, "📝 Original Arabic", arabic)
        add_long_field(embed, "🇵🇰 Urdu", translation)
        embed.set_footer(text="Gemini OCR + OpenRouter Llama 🦙")
        await ctx.reply(embed=embed)
        return
    if not text:
        await ctx.reply("**Usage:** `!urdu <arabic text>` or attach image + `!urdu`")
        return
    if not contains_arabic(text):
        await ctx.reply("⚠️ Please provide Arabic text.")
        return
    async with ctx.typing():
        translation = await translate_to_language(text, "Urdu")
    embed = discord.Embed(title="🇵🇰 Urdu Translation", color=0x00f3ff)
    add_long_field(embed, "📝 Original Arabic", text)
    add_long_field(embed, "🇵🇰 Urdu", translation)
    embed.set_footer(text="Powered by OpenRouter Llama 🦙")
    await ctx.reply(embed=embed)

@bot.command(name="english", aliases=["e", "en"])
async def translate_english(ctx, *, text=None):
    """Translate Arabic to English only"""
    if ctx.message.attachments:
        arabic = await get_image_arabic(ctx)
        if not arabic:
            return
        async with ctx.typing():
            translation = await translate_to_language(arabic, "English")
        embed = discord.Embed(title="🇬🇧 English Translation", color=0x00f3ff)
        add_long_field(embed, "📝 Original Arabic", arabic)
        add_long_field(embed, "🇬🇧 English", translation)
        embed.set_footer(text="Gemini OCR + OpenRouter Llama 🦙")
        await ctx.reply(embed=embed)
        return
    if not text:
        await ctx.reply("**Usage:** `!english <arabic text>` or attach image + `!english`")
        return
    if not contains_arabic(text):
        await ctx.reply("⚠️ Please provide Arabic text.")
        return
    async with ctx.typing():
        translation = await translate_to_language(text, "English")
    embed = discord.Embed(title="🇬🇧 English Translation", color=0x00f3ff)
    add_long_field(embed, "📝 Original Arabic", text)
    add_long_field(embed, "🇬🇧 English", translation)
    embed.set_footer(text="Powered by OpenRouter Llama 🦙")
    await ctx.reply(embed=embed)

@bot.command(name="translate", aliases=["t", "tr", "both", "b"])
async def translate_both_command(ctx, *, text=None):
    """Translate Arabic to both Urdu and English"""
    if ctx.message.attachments:
        arabic = await get_image_arabic(ctx)
        if not arabic:
            return
        async with ctx.typing():
            translations = await translate_both(arabic)
        embed = discord.Embed(title="🌐 Arabic Translation", color=0x00f3ff)
        add_long_field(embed, "📝 Original Arabic", arabic)
        add_long_field(embed, "🇵🇰 Urdu", translations["urdu"])
        add_long_field(embed, "🇬🇧 English", translations["english"])
        embed.set_footer(text="Gemini OCR + OpenRouter Llama 🦙")
        await ctx.reply(embed=embed)
        return
    if not text:
        await ctx.reply(
            "**📖 Quick Guide:**\n\n"
            "`!urdu <arabic>` — Urdu only\n"
            "`!english <arabic>` — English only\n"
            "`!translate <arabic>` — Both\n"
            "Attach image + any command above for image translation\n\n"
            "Type `!guide` for full guide."
        )
        return
    if not contains_arabic(text):
        await ctx.reply("⚠️ Please provide Arabic text.")
        return
    async with ctx.typing():
        translations = await translate_both(text)
    embed = discord.Embed(title="🌐 Arabic Translation", color=0x00f3ff)
    add_long_field(embed, "📝 Original Arabic", text)
    add_long_field(embed, "🇵🇰 Urdu", translations["urdu"])
    add_long_field(embed, "🇬🇧 English", translations["english"])
    embed.set_footer(text="Powered by OpenRouter Llama 🦙")
    await ctx.reply(embed=embed)

@bot.command(name="guide", aliases=["h", "commands"])
async def guide(ctx):
    """Show full guide"""
    embed = discord.Embed(
        title="📖 Translation Bot — Full Guide",
        description="Translates Arabic text and images to Urdu and/or English.",
        color=0x00f3ff
    )
    embed.add_field(name="━━━━━━━━━━━━━━━━━━━━", value="**📝 TEXT TRANSLATION**", inline=False)
    embed.add_field(name="🇵🇰 Urdu only", value="`!urdu <arabic text>`\n`!u <arabic text>`\nExample: `!urdu مرحبا`", inline=False)
    embed.add_field(name="🇬🇧 English only", value="`!english <arabic text>`\n`!e <arabic text>`\nExample: `!english مرحبا`", inline=False)
    embed.add_field(name="🌐 Both Urdu + English", value="`!translate <arabic text>`\n`!t <arabic text>`\nExample: `!translate مرحبا`", inline=False)
    embed.add_field(name="━━━━━━━━━━━━━━━━━━━━", value="**🖼️ IMAGE TRANSLATION**", inline=False)
    embed.add_field(name="🇵🇰 Image → Urdu only", value="Attach image + type `!urdu` or `!u`", inline=False)
    embed.add_field(name="🇬🇧 Image → English only", value="Attach image + type `!english` or `!e`", inline=False)
    embed.add_field(name="🌐 Image → Both", value="Attach image + type `!translate` or `!t`", inline=False)
    embed.add_field(name="━━━━━━━━━━━━━━━━━━━━", value="**⚙️ OTHER COMMANDS**", inline=False)
    embed.add_field(name="🏓 Check Status", value="`!ping`", inline=False)
    embed.add_field(name="📖 Show Guide", value="`!guide` or `!help` or `!h`", inline=False)
    embed.set_footer(text="Powered by Gemini OCR + OpenRouter Llama 🦙")
    await ctx.reply(embed=embed)

@bot.command(name="ping")
async def ping(ctx):
    await ctx.reply(f"🏓 Pong! Latency: {round(bot.latency * 1000)}ms")

if __name__ == "__main__":
    bot.run(TOKEN)
