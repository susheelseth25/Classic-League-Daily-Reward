import discord
from discord.ext import commands, tasks
import random
from datetime import datetime, time
import asyncio
import os

# ========== SETTINGS ==========
TOKEN = "e1d5657eb8851e2b43bff4e31c0bbad2ac564f5e76e6c83d7d2cec2a24956bba"          # Paste your bot token
CHANNEL_ID =  1564683438248828933       # Replace with your #daily-entry channel ID
WINNERS_COUNT = 1                      # How many winners per day
ENTRY_EMOJI = "✅"                     # Emoji players react with
START_HOUR = 12                        # Hour the entry opens (24h format, IST)
END_HOUR = 23                          # Hour the draw happens (24h format, IST)
# ==============================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

daily_message = None
participants = set()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    daily_cycle.start()

@tasks.loop(minutes=1)
async def daily_cycle():
    global daily_message, participants
    now = datetime.now()
    
    # Start new entry at START_HOUR
    if now.hour == START_HOUR and now.minute == 0:
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            participants = set()
            embed = discord.Embed(
                title="🏆 Daily Classic League Entry",
                description=f"React with {ENTRY_EMOJI} to enter today's draw!\nWinners will be picked at {END_HOUR}:00",
                color=0xFFAA00
            )
            daily_message = await channel.send(embed=embed)
            await daily_message.add_reaction(ENTRY_EMOJI)
            print("New daily entry started")

    # Draw winners at END_HOUR
    if now.hour == END_HOUR and now.minute == 0 and daily_message:
        channel = bot.get_channel(CHANNEL_ID)
        if channel and participants:
            winners = random.sample(list(participants), min(WINNERS_COUNT, len(participants)))
            mentions = " ".join(w.mention for w in winners)
            await channel.send(
                f"🎉 **Today's Winners** 🎉\n{mentions}\n\nCongrats! Tagging you as requested."
            )
            print(f"Winners: {[w.name for w in winners]}")
        else:
            await channel.send("No entries today.")
        daily_message = None
        participants = set()

@bot.event
async def on_raw_reaction_add(payload):
    global participants
    if daily_message and payload.message_id == daily_message.id and str(payload.emoji) == ENTRY_EMOJI:
        if payload.user_id != bot.user.id:
            user = bot.get_user(payload.user_id)
            if user:
                participants.add(user)

@bot.event
async def on_raw_reaction_remove(payload):
    global participants
    if daily_message and payload.message_id == daily_message.id and str(payload.emoji) == ENTRY_EMOJI:
        user = bot.get_user(payload.user_id)
        if user in participants:
            participants.remove(user)

bot.run(TOKEN)
