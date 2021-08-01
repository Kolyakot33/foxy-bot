import asyncio
from time import time, sleep
from traceback import print_exc, format_exc
import discord
from signal import signal, SIGINT, SIGTERM
from discord.ext import tasks

client = discord.Client()
start_time = time()
state = 1


@tasks.loop(seconds=30)
async def refresh_status():
    await client.change_presence(status=discord.Status.idle, activity=discord.Game(
        name=f"Задержка: {int(client.latency * 1000)}мс, Аптайм: {int(time() - start_time)}c"))


@client.event
async def on_ready():
    print("Ready!")
    signal(SIGTERM, bot_stop)
    signal(SIGINT, bot_stop)
    if not refresh_status.is_running():
        refresh_status.start()


@client.event
async def on_error(err):
    try:
        await client.get_user(632511458537898016).send(format_exc())
    except Exception:
        print("Fatal Error!")
    finally:
        print_exc()


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user or state == 0:
        return
    elif ("@everyone" in message.content.lower() or "@here" in message.content.lower()) and not message.author.guild_permissions.administrator:
        await message.channel.send("Какой тебе ещё пинг? Бан хочешь?")
        await message.delete()
        return
    elif message.content.lower().startswith("foxy restart"):
        if message.author.id == 632511458537898016:
            await message.reply("OK")
            bot_stop()
        else:
            return
    elif message.content.lower().startswith("!pred"):
        if not message.author.guild_permissions.administrator:
            return
        try:
            usr, reason, task, time, admin = message.content[6:].split(sep=";")
        except ValueError:
            await message.channel.send("Ошибка в синтаксисе команды")
        embed = discord.Embed(title="Предупреждение", description=f'{usr}, вам выдано предупреждение',
                              colour=int("2f3136", base=16))
        embed.add_field(name="Причина:", value=reason)
        embed.add_field(name="Задание для снятия:", value=task)
        embed.add_field(name="Срок:", value=f"{time} дней")
        if admin.lower() == "cubelius":
            embed.set_footer(text="Cubelius",
                             icon_url="https://cdn.discordapp.com/attachments/843588784126033943/870812313836453948/e081d6eabcfa794d9ac10cd0626799b4.webp")
        elif admin.lower() == "homka":
            embed.set_footer(text="Homka",
                             icon_url="https://cdn.discordapp.com/attachments/843588784126033943/870815009293361173/Screenshot_74.png")
        await message.channel.send(embed=embed, content=usr)
    elif message.content.lower().startswith("!makeann"):
        try:
            type, resource, price = message.content[9:].split(sep=";")
        except ValueError:
            await message.reply("Ошибка в синтаксисе команды")
        embed = discord.Embed(title="Объявление", colour=int("2f3136", base=16))
        embed.add_field(name="Тип", value="Продажа" if type=="1" else "Покупка")
        embed.add_field(name="Ресурсы", value=resource)
        embed.add_field(name="Цена", value=f"{price} <:lar:858797748924448788>")
        embed.set_footer(icon_url=message.author.avatar_url, text=message.author.name)
        await message.channel.send(embed=embed)
        await message.delete()
        return
    elif message.channel.id == 858986069553840138:
        await message.delete()



def bot_stop(*args):
    global state
    state = 0
    print("Stopping...")
    print("Waiting tasks to finish...")
    sleep(5)
    refresh_status.stop()
    for task in asyncio.all_tasks():
        task.cancel()
    asyncio.get_running_loop().stop()
    print("Stop completed!")


client.run('ODA1NDg3MTIxNTgxOTk4MTUx.YBbmVw.gziNetHjAmwC6vQ1I9hyBkEQyyk')
