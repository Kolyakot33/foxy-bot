import asyncio
from time import time
from traceback import print_exc, format_exc
import discord
from discord.ext import commands
from signal import signal, SIGINT, SIGTERM
from discord.ext import tasks
import pymysql
from discord_slash import ComponentContext, SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option, create_permission, create_choice
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_slash.model import ButtonStyle, SlashCommandPermissionType
from subprocess import Popen, PIPE
from mctools import QUERYClient

bot = commands.Bot(intents=discord.Intents.all(), command_prefix="$$")
slash = SlashCommand(bot, sync_commands=True)
start_time = time()
kolyakot33 = 632511458537898016


@tasks.loop(seconds=30)
async def refresh_status():
    # Check for updates
    # process = Popen(["git", "pull"], stdout=PIPE)
    # data = process.communicate()
    # if not data[0].startswith(b"Already up to date."):
    #    bot_stop()
    # change status
    await bot.change_presence(status=discord.Status.idle, activity=discord.Game(
        name=f"Задержка: {int(bot.latency * 1000)}мс, Аптайм: {round(int(time() - start_time) / 60.0, 2)}м"))
    # refresh server stats
    with QUERYClient("135.181.126.142", port=25953) as qc:
        stats = qc.get_full_stats()
    await bot.get_channel(874921983358414878).get_partial_message(875701352502804490).edit(
        embed=discord.Embed(title="Информация о сервере", description="foxdream.gomc.fun").add_field(
            name=f"Онлайн {stats['numplayers']}/{stats['maxplayers']}",
            value=", ".join(stats['players']).replace("[0m", "")))


@bot.event
async def on_ready():
    print("Ready")
    signal(SIGTERM, bot_stop)
    signal(SIGINT, bot_stop)
    if not refresh_status.is_running():
        refresh_status.start()


@bot.event
async def on_error(*args, **kwargs):
    try:
        await bot.get_user(kolyakot33).send(format_exc())
    except Exception as exc:
        print("Fatal Error!", exc)
    finally:
        print_exc()


@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return
    elif (
            "@everyone" in message.content.lower() or "@here" in message.content.lower()) and not message.author.guild_permissions.administrator:
        return
    elif message.content.lower().startswith("foxy"):
        if message.author.id == 632511458537898016:
            g = await eval(message.content.replace("foxy", ""))
            await message.author.send(g)
            await message.reply("OK", delete_after=10.0)
        else:
            await message.reply("Nope", delete_after=10.0)
            return


@slash.slash(name="warn", description="Дать игроку предупреждение", options=[
    create_option(name="player", description="Игрок которому вы хотите дать предупреждение", option_type=6,
                  required=True),
    create_option(name="reason", description="Причина предупреждения", option_type=3, required=True),
    create_option(name="task", description="Задание для снятия", option_type=3, required=True),
    create_option(name="time", description="Срок", option_type=3, required=True)])
@slash.permission(guild_id=785610109723738163,
                  permissions=[create_permission(785618963261685760, SlashCommandPermissionType.ROLE, True),
                               create_permission(799449713451335701, SlashCommandPermissionType.ROLE, True)])
async def warn(ctx: SlashContext, player: discord.User, reason: str, task: str, time: str):
    embed = discord.Embed(title="Предупреждение", description=f'{player}, вам выдано предупреждение',
                          colour=int("2f3136", base=16))
    embed.add_field(name="Причина:", value=reason)
    embed.add_field(name="Задание для снятия:", value=task)
    embed.add_field(name="Срок:", value=f"{time} дней")
    if ctx.author_id == 397354929288904704:
        embed.set_footer(text="Cubelius",
                         icon_url="https://cdn.discordapp.com/attachments/843588784126033943/870812313836453948/e081d6eabcfa794d9ac10cd0626799b4.webp")
    elif ctx.author_id == 422190637111050240:
        embed.set_footer(text="Homka",
                         icon_url="https://cdn.discordapp.com/attachments/843588784126033943/870815009293361173/Screenshot_74.png")
    elif ctx.author_id == 866255591818657792:
        embed.set_footer(text="ItsPomiDor4iK",
                         icon_url="https://cdn.discordapp.com/attachments/873174230970273832/877718152333656125/268b20822dcee012.PNG")
    await bot.get_guild(785610109723738163).get_channel(845562544965681153).send(embed=embed, content=player.mention)


@slash.slash(name="makeann", description="Сделать объявление", options=[
    create_option(name="ann_type", description="Тип объявления", option_type=3,
                  choices=[create_choice(name="Продажа", value="1"), create_choice(name="Покупка", value="2")],
                  required=True), create_option(name="resource", description="Ресурс", option_type=3, required=True),
    create_option(name="price", description="Цена", option_type=3, required=True)])
async def makeann(ctx: SlashContext, ann_type: str, resource: str, price: str):
    embed = discord.Embed(title="Объявление", colour=int("2f3136", base=16))
    embed.add_field(name="Тип", value="Продажа" if ann_type == "1" else "Покупка")
    embed.add_field(name="Ресурсы", value=resource)
    embed.add_field(name="Цена", value=f"{price} <:lar:858797748924448788>")
    embed.set_footer(icon_url=ctx.author.avatar_url, text=ctx.author.nick)
    msg = await ctx.channel.send(embed=embed, components=[
        create_actionrow(
            create_button(style=ButtonStyle.green, label="Удалить(только для создателя)",
                          emoji=bot.get_emoji(867776679673462785), custom_id="remove_ann"))
    ])
    with pymysql.connect(host="5.252.194.76", user="u24_Gy3siZPRMr", password="!v9+4cr!bQa2Wwo=y51zeu1+",
                         database="s24_main") as con:
        cur = con.cursor()
        cur.execute(f"INSERT INTO ann (message, user) VALUES ({msg.id}, {ctx.author.id})")
        cur.execute(f"SELECT id FROM ann WHERE message={msg.id}")
        d = cur.fetchone()[0]
        cur.close()
        con.commit()
    embed.title = f"Объявление #{d}"
    await msg.edit(embed=embed)


@slash.slash(name="buy", description="Купить что-то",
             options=[create_option(name="id", option_type=4, description="id без #", required=True),
                      create_option(name="comment", description="Коментарий", option_type=3, required=True)])
async def buy(ctx: SlashContext, ID: int, comment: str):
    con = pymysql.connect(host="5.252.194.76", user="u24_Gy3siZPRMr", password="!v9+4cr!bQa2Wwo=y51zeu1+",
                          database="s24_main")
    cur = con.cursor()
    cur.execute(f"SELECT user, message FROM ann WHERE id={int(ID)}")
    res = cur.fetchone()
    cur.close()
    con.close()
    if res == ():
        return
    user = bot.get_user(int(res[0]))
    embed = discord.Embed(title="Покупка",
                          description=f"{user.mention}, у вас хотят купить ресурсы по этому айди: [#{ID}]({bot.get_channel(858986069553840138).get_partial_message(int(res[1])).jump_url})",
                          colour=int("6cc789", base=16))
    embed.add_field(name="Комментарий покупателя", value=comment)
    embed.set_footer(icon_url=ctx.author.avatar_url, text=ctx.author.nick)
    await bot.get_channel(858986069553840138).send(embed=embed, content=user.mention)


@slash.component_callback()
async def remove_ann(ctx: ComponentContext):
    con = pymysql.connect(host="5.252.194.76", user="u24_Gy3siZPRMr", password="!v9+4cr!bQa2Wwo=y51zeu1+",
                          database="s24_main")
    cur = con.cursor()
    cur.execute(f"SELECT user FROM ann WHERE message={ctx.origin_message.id}")
    if int(cur.fetchone()[0]) == ctx.author_id:
        await ctx.origin_message.delete()
    else:
        await ctx.send("Ошибка: вы не создатель объявления", hidden=True)
    cur.close()
    con.close()


@slash.component_callback()
async def new_ticket(ctx: ComponentContext):
    con = pymysql.connect(host="5.252.194.76", user="u24_Gy3siZPRMr", password="!v9+4cr!bQa2Wwo=y51zeu1+",
                          database="s24_main")
    cur = con.cursor()
    cur.execute("SELECT id FROM tickets WHERE id=(SELECT MAX(id) FROM tickets)")
    channel = await ctx.guild.create_text_channel(name=f"Тикет-{cur.fetchone()[0] + 1}", overwrites={
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.author: discord.PermissionOverwrite(read_messages=True),
        ctx.guild.get_role(799449713451335701): discord.PermissionOverwrite(read_messages=True),
        ctx.guild.get_member(kolyakot33): discord.PermissionOverwrite(read_messages=True)
    }, category=ctx.guild.get_channel(872495698598309918))
    msg = await channel.send(content=f"{ctx.author.mention} опишите вашу проблему.",
                             components=[
                                 create_actionrow(
                                     create_button(style=ButtonStyle.red, label="Закрыть", custom_id="close_ticket")
                                 )
                             ])
    cur.execute(f"INSERT INTO tickets (channel, user) VALUES ({channel.id}, {ctx.author_id})")
    con.commit()
    cur.close()
    con.close()


@slash.component_callback()
async def close_ticket(ctx: ComponentContext):
    await ctx.channel.edit(overwrites={
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.author: discord.PermissionOverwrite(read_messages=False),
        ctx.guild.get_role(799449713451335701): discord.PermissionOverwrite(read_messages=True),
        ctx.guild.get_member(kolyakot33): discord.PermissionOverwrite(read_messages=True)
    }, name="(Закрыт) " + ctx.channel.name.lower())
    await ctx.channel.send(f"Тикет закрыт {ctx.author.mention}")


def bot_stop(*args):
    refresh_status.stop()
    for task in asyncio.all_tasks():
        task.cancel()
    asyncio.get_running_loop().stop()
    print("Stop completed!")


bot.run('ODA1NDg3MTIxNTgxOTk4MTUx.YBbmVw.gziNetHjAmwC6vQ1I9hyBkEQyyk')
