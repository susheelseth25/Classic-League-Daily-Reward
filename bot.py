import discord
from discord.ext import commands, tasks
import random
from datetime import datetime
import os

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))
WINNERS_COUNT = int(os.getenv("WINNERS_COUNT", "3"))
ENTRY_EMOJI = "✅"
START_HOUR = int(os.getenv("START_HOUR", "12"))
END_HOUR = int(os.getenv("END_HOUR", "23"))

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

if __name__ == "__main__":
    bot.run(TOKEN)
