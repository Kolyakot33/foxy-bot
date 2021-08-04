import asyncio
from time import time, sleep
from traceback import print_exc, format_exc
import discord
from signal import signal, SIGINT, SIGTERM
from discord.ext import tasks
import pymysql
from discord_slash import ComponentContext
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle
from discord_slash import SlashCommand
import subprocess

client = discord.Client(intents=discord.Intents.all())
slash = SlashCommand(client, sync_commands=True)
start_time = time()
state = 1
kolyakot33 = 632511458537898016


@tasks.loop(seconds=30)
async def refresh_status():
    process = subprocess.Popen(["git", "pull"], stdout=subprocess.PIPE)
    data = process.communicate()
    if not data[0].startswith(b"Already up to date."):
        bot_stop()
    await client.change_presence(status=discord.Status.idle, activity=discord.Game(
        name=f"Задержка: {int(client.latency * 1000)}мс, Аптайм: {round(int(time() - start_time) / 60.0, 2)}м"))


@client.event
async def on_ready():
    print("Ready!")
    signal(SIGTERM, bot_stop)
    signal(SIGINT, bot_stop)
    if not refresh_status.is_running():
        refresh_status.start()


@client.event
async def on_error(*args, **kwargs):
    try:
        await client.get_user(kolyakot33).send(format_exc())
    except Exception as exc:
        print("Fatal Error!", exc)
    finally:
        print_exc()


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user or state == 0:
        return
    elif (
            "@everyone" in message.content.lower() or "@here" in message.content.lower()) and not message.author.guild_permissions.administrator:
        await message.channel.send("Какой тебе ещё пинг? Бан хочешь?")
        await message.delete()
        return
    elif message.content.lower().startswith("foxy"):
        if message.author.id == 632511458537898016:
            g = await eval(message.content.replace("foxy",""))
            message.author.send(g)
            await message.reply("OK", delete_after=10.0)
        else:
            await message.reply("Nope", delete_after=10.0)
            return
    elif message.content.lower().startswith("!pred"):
        if not message.author.guild_permissions.administrator and not message.author.id == kolyakot33:
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
        await message.guild.get_channel(845562544965681153).send(embed=embed, content=usr)
        return

    if message.content.lower().startswith("!makeann") and message.channel.id == 858986069553840138:
        smsg = message.content[9:].split(sep=";")
        if len(smsg) == 3:
            type, resource, price = smsg
            embed = discord.Embed(title="Объявление", colour=int("2f3136", base=16))
            embed.add_field(name="Тип", value="Продажа" if type == "1" else "Покупка")
            embed.add_field(name="Ресурсы", value=resource)
            embed.add_field(name="Цена", value=f"{price} <:lar:858797748924448788>")
        else:
            embed = discord.Embed(title="Объявление", colour=int("2f3136", base=16), description=message.content[11:])
        embed.set_footer(icon_url=message.author.avatar_url, text=message.author.nick)
        msg = await message.channel.send(embed=embed, components=[create_actionrow(
            create_button(style=ButtonStyle.green, label="Удалить(только для создателя)",
                          emoji=client.get_emoji(867776679673462785)))
        ])
        con = pymysql.connect(host="5.252.194.76", user="u24_Gy3siZPRMr", password="!v9+4cr!bQa2Wwo=y51zeu1+",
                              database="s24_main")
        cur = con.cursor()
        cur.execute(f"INSERT INTO ann (message, user) VALUES ({msg.id}, {message.author.id})")
        cur.execute(f"SELECT id FROM ann WHERE message={msg.id}")
        d = cur.fetchone()[0]
        cur.close()
        con.commit()
        con.close()
        a = msg.embeds[0]
        a.title = f"Объявление #{d}"
        await msg.edit(embed=a)
        await message.delete()
    elif message.content.lower().startswith("!buy"):
        try:
            iD, comment = message.content[5:].split(sep=';')
        except ValueError:
            await message.delete()
        con = pymysql.connect(host="5.252.194.76", user="u24_Gy3siZPRMr", password="!v9+4cr!bQa2Wwo=y51zeu1+",
                              database="s24_main")
        cur = con.cursor()
        cur.execute(f"SELECT user, message FROM ann WHERE id={int(iD)}")
        res = cur.fetchone()
        cur.close()
        con.close()
        print(res)
        user = client.get_user(int(res[0]))
        embed = discord.Embed(title="Покупка",
                              description=f"{user.mention}, у вас хотят купить ресурсы по этому айди: [#{iD}]({client.get_channel(858986069553840138).get_partial_message(int(res[1])).jump_url})",
                              colour=int("6cc789", base=16))
        embed.add_field(name="Комментарий покупателя", value=comment)
        embed.set_footer(icon_url=message.author.avatar_url, text=message.author.nick)
        await client.get_channel(858986069553840138).send(embed=embed, content=user.mention)
        await message.delete()
    elif message.channel.id == 858986069553840138:
        await message.delete()
    return


@client.event
async def on_component(ctx: ComponentContext):
    if ctx.channel.id == 858986069553840138:
        con = pymysql.connect(host="5.252.194.76", user="u24_Gy3siZPRMr", password="!v9+4cr!bQa2Wwo=y51zeu1+",
                              database="s24_main")
        cur = con.cursor()
        cur.execute(f"SELECT user FROM ann WHERE message={ctx.origin_message.id}")
        if int(cur.fetchone()[0]) == ctx.author_id:
            await ctx.origin_message.delete()
        cur.close()


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
