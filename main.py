import discord
from discord.ext import commands, tasks
import os
from collections import defaultdict
import random
from keep_alive import keep_alive
# ========== Configuration ==========
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
abusive_words = {"idiot", "stupid", "noob", "dumb", "fuck", "shit", "bitch"}  # Add more
spam_tracker = defaultdict(list)
GIVEAWAY_CHANNEL = "👾free-stuffs"
POLL_EMOJIS = ['👍', '👎']
STATUS_MESSAGE = "Chatting with legends 👑"

# ========== Events ==========

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=" Chatting with legends 👑"))


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.lower()
    author = message.author

    # 🚫 Detect @everyone misuse
    if "@everyone" in content:
        if not any(role.permissions.administrator for role in message.author.roles):
            await message.delete()
            await message.channel.send(f"🚫 {message.author.mention}, you're not allowed to use @everyone.")
            return

    # 🌍 Enforce English only
    if any(word in content for word in SUS_MESSAGES):
        await message.channel.send(f"🌐 {message.author.mention}, please speak English in this server.")

    # --- Abusive Word Check ---
    if any(word in content for word in abusive_words):
        await message.channel.send(f"🚫 {author.mention}, watch your language!")

    # --- DM interaction ---
    if isinstance(message.channel, discord.DMChannel):
        replies = [
            "👋 Hello! How can I assist you today?",
            "🤖 I'm always here to help, just ask!",
            "🌟 Want to create a poll or submit a suggestion?"
        ]
        await message.channel.send(random.choice(replies))

    # --- Mention reply ---
    if bot.user in message.mentions:
        await message.channel.send("👋 Yes? You called me? I'm ready!")

    # --- Anti-spam ---
    user_msgs = spam_tracker[author.id]
    user_msgs.append(content)
    if len(user_msgs) > 5:
        user_msgs.pop(0)

    if user_msgs.count(content) == 2:
        await message.channel.send(f"⚠️ {author.mention}, please don’t spam...")
    elif user_msgs.count(content) == 3:
        await message.channel.send(f"❗ {author.mention}, one more and I’ll start deleting your messages.")
    elif user_msgs.count(content) >= 4:
        try:
            await message.delete()
            await message.channel.send(f"🛑 {author.mention}, message removed for spam.")
        except discord.errors.Forbidden:
            pass

    await bot.process_commands(message)

# ========== features ==========

# Server rules list
SERVER_RULES = """
📜 **Server Rules**
1. Be respectful to everyone—no hate, harassment, or bullying.
2. No spamming messages, emojis, or mic in voice chats.
3. Keep all content safe for work and appropriate.
4. Use the correct channels for the right topics.
5. No self-promotion or advertising without staff approval.
6. Don’t share illegal content or break Discord’s Terms of Service.
7. Respect all staff and their decisions.
8. Use English only unless another language is allowed in a specific channel.
9. Don’t impersonate other members or staff.
🔟 Have fun, stay chill, and enjoy the server!
🚫 Don't mention @everyone unless you are staff.
"""

# Detect suspicious patterns or local slang
SUS_MESSAGES = [
    "oyee", "bhai", "kya", "kyaa", "yrr", "kaha", "haan", "nahi", "matlab", "bkl", "suno", "abe"
]

@bot.command()
async def rules(ctx):
    await ctx.send(SERVER_RULES)



# ========== Commands ==========

@bot.command()
async def myhelp(ctx):
    await ctx.send("""
📘 **Available Commands**
- `!makepoll <question>` — Create a yes/no poll
- `!giveaway` — Show latest free game (simulated)
- `!ping` — Check bot latency
- `!about` — Info about the bot
- `!talk <message>` — Talk with bot in public
    """)

@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! Latency is `{latency}ms`")

@bot.command()
async def about(ctx):
    await ctx.send("🤖 I'm a friendly, fun, and helpful Discord bot built with love! Created by `Ansh`.")

@bot.command()
async def talk(ctx, *, message):
    await ctx.send(f"🗣️ {ctx.author.name}, I heard you say: *{message}*")

@bot.command()
async def makepoll(ctx, *, question):
    msg = await ctx.send(f"📊 **Poll:** {question}")
    for emoji in POLL_EMOJIS:
        await msg.add_reaction(emoji)

@bot.command()
async def giveaway(ctx):
    giveaways = [
        "🎮 Free Game on Steam: *Super Adventure 2*",
        "🎁 Epic Games Freebie: *Rogue Galaxy*",
        "🆓 Free Weekend: *Minecraft Java Edition*"
    ]
    channel = discord.utils.get(ctx.guild.text_channels, name=GIVEAWAY_CHANNEL)
    if channel:
        await channel.send(random.choice(giveaways))
        await ctx.send("✅ Giveaway posted!")
    else:
        await ctx.send("⚠️ Giveaway channel not found.")

# ========== DM Command Simulation ==========

@bot.command()
async def dmme(ctx):
    try:
        await ctx.author.send("📩 Here's a secret message in DMs!")
        await ctx.send("✅ Sent you a DM!")
    except discord.Forbidden:
        await ctx.send("❌ I can't DM you. Check your privacy settings.")

# ========== Welcome ==========

@bot.event
async def on_member_join(member):
    try:
        await member.send("👋 Welcome to the server! Please read and follow our rules:\n" + SERVER_RULES)
    except discord.Forbidden:
        pass


# ========== Run the Bot ==========
keep_alive()
token = os.getenv("TOKEN")
if not token:
    raise Exception("TOKEN environment variable not set. Please set it before running the bot.")
bot.run(token)  # Store token in environment variable  # Store token in environment variable

