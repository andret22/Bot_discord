#Bot de chamada da equipe rocket

import discord
import mysql.connector
from datetime import datetime
from discord.ext import commands

#Bot's token
#Token removido para repositório github público, adiconar o token novamente ao usar.
TOKEN = ""

#Instance of the bot connection to the discord server
bot = commands.Bot(command_prefix='$', intents=discord.Intents.all())
discord.Intents.members = True

#Try to connect to a db
try:
    conn = mysql.connector.connect(
        host="localhost",
        database="permanenciarocket",
        user="default",
        password="jozz57@z" )
except Exception as e:
    print(e)
    exit()

#Creates a cursos to do SQL QUERRIES
cursor = conn.cursor()


#On ready--------------------------------------------------------------------------------

@bot.event
async def on_ready():
   print(f'Estou pronto e operacional :D')
   canal =bot.get_channel(1068605735207977000);
   await canal.send("Conexão com o B.D. estabelecida com sucesso")
   await canal.send("Estou ativo e operacional :D")

#Message template------------------------------------------------------------------------

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.content.startswith("$algo"):
            await message.channel.send("Fazendo algo...")
            
    await bot.process_commands(message) 

#Greetings and GoodByes-----------------------------------------------------------------

@bot.event
async def on_voice_state_update(member, before, after):
    channel = bot.get_channel(1068605735207977000)
    previous = before.channel
    try:
        log = ''
        cursor.execute(f"SELECT * FROM membro WHERE id_membro LIKE 5379")
        for row in cursor:
            log+= row[1]
        if previous is None:
            if log == '':
                await channel.send(f"Bem-vindo, {member}. Você ainda não está cadastrado. utilize -> $cadastro 'nome' 'sobrenome' 'numero do subsistema' <- para se cadastrar")
                cursor.nextset()
            else:
                await channel.send(f"Bem-vindo, {member}. Início da permanência--> {datetime.now()}")
                cursor.execute(f"INSERT INTO horarios VALUES (DEFAULT, {member.id //10**14}, 1, NOW(), NULL, NULL)")
                cursor.execute("COMMIT")
                cursor.nextset()
        elif previous is not None:
            if log == '':
                await channel.send(f"Até mais, {member}")
                cursor.nextset()
            else:
                cursor.execute(f"UPDATE horarios SET saida = NOW() WHERE total IS NULL AND id_membro = {member.id //10**14}")
                cursor.execute("COMMIT")
                await channel.send(f"Até mais, {member}. Fim da permanência--> {datetime.now()}")
                cursor.nextset()
    except Exception as e:
        print(e)
        cursor.execute("ROLLBACK")
#Show all members----------------------------------------------------------------------

@bot.command()
async def membros(ctx):
    cursor.execute("SELECT membro.nome as nome, sobrenome, nome_subsistema as subsistema FROM membro NATURAL JOIN subsistema")
    msg = '/-------------------------------------------------------------------------\ \n'
    for row in cursor:
        msg += (f'# |NOME -> {row[0]} {row[1]} | SUBSISTEMA -> {row[2]}| #\n')
        msg += '-------------------------------------------------------------------------|\n'
    await ctx.send(msg)
    cursor.nextset()

#Sing up a member---------------------------------------------------------------------

@bot.command()
async def cadastro(ctx, nome, sobrenome, subsistema):
    try:
        myID = ctx.message.author.id
        cursor.execute(f"INSERT INTO membro VALUES ({myID // 10**14},'{nome}','{sobrenome}',{subsistema})")
        cursor.execute("COMMIT")
        await ctx.send("Usuário cadastrado com sucesso. Reloge no servidor para inicar sua permanência")
    except Exception as e:
        cursor.execute("ROLLBACK")
        await ctx.send("OPA, deu ruim...")
        await ctx.send(e)
#Return the last 30 members that were online-----------------------------------------

@bot.command()
async def permanencias(ctx):
    try:
        msgp = ''
        cursor.execute("CALL get_last_30")
        for row in cursor:
            msgp += (f'# NOME -> {row[0]} | {row[1]} | TEMPO DE PERMANENCIA-> {row[2]} MINUTOS #\n')
        print(msgp)
        try:
            await ctx.send(msgp)
        except Exception as e:
            print(e)
        cursor.nextset()
    except Exception as e:
        cursor.nextset()
        print(e)

#last 30 time online for specific member----------------------------------------------

@bot.command()
async def especifico(ctx, arg1, arg2):
    try:
        msg = ''
        cursor.execute(f"CALL specific_last_30('{arg1}','{arg2}')")
        for row in cursor:
            msg += (f'# NOME -> {row[0]} | {row[1]} | TEMPO DE PERMANENCIA-> {row[2]} MINUTOS #\n')
        await ctx.send(msg)
        cursor.nextset()
    except Exception as e:
        cursor.nextset()
        print(e)
    

#Run bot------------------------------------------------------------------------------
bot.run(TOKEN)