import discord, time, jishaku, io, aiohttp, json
from discord.ext import commands
from cairosvg import svg2png

line='-'*25
hid=666317117154525185

async def is_owner(ctx):
    return ctx.author.id == hid
def ishex(s):
    try:
        int(s, 16)
        return True
    except ValueError:
        return False
def ename(d):
    if d['name']['exact_match_name']:
        return f"this color is {d['name']['value']}"
    else:
        return f"the closest named color is {d['name']['value']}({d['name']['closest_named_hex']}) with a distance of {d['name']['distance']}"
def percnt(n):
    if isinstance(n, str):
        n=eval(n)
    elif isinstance(n, (float, int)):
        pass
    else:
        n=eval(str(n))

    if n<1:
        n=str(round(n*100))
        return f"{n[0:2]}%"
    else:
        return "100%"
def invertHex(hexNumber):
    inverse = hex(abs(int(hexNumber, 16) - 255))[2:] 
    if len(inverse) == 1: 
        inverse = '0'+inverse
    return inverse
def colorInvert(hexCode):
    inverse = "" 
    if len(hexCode) == 6: 
        R = hexCode[:2]
        G = hexCode[2:4]
        B = hexCode[4:]
    else:
        return hexCode 
    inverse = inverse + invertHex(R)
    inverse = inverse + invertHex(G)
    inverse = inverse + invertHex(B)
    return inverse

client=commands.Bot(command_prefix='h.', owner_id=hid)

@client.event
async def on_ready():
    print(f"{line}\n{client.user}\n<{client.user.id}>\n{line}")
    await client.change_presence(status="dnd",activity=discord.Game("h"))

@client.command()
async def h(ctx):
    await ctx.send(content="h")
@client.command()
@commands.check(is_owner)
async def uh(ctx):
    await ctx.send(content="ok")
@client.command(name="hex")
async def h(ctx,*,arg):
    orig=arg
    if arg.startswith("#"):
        arg=arg[1:len(arg)]
    if len(arg)==3 and ishex(arg):
        arg=f"{arg[0]}{arg[0]}{arg[1]}{arg[1]}{arg[2]}{arg[2]}"
    size=150
    if ishex(arg) and len(arg)==6:
        async with aiohttp.ClientSession() as session:
            picurl=f"http://www.singlecolorimage.com/get/{arg}/{size}x{size}"
            async with session.get(picurl) as resp:
                if resp.status != 200:
                    return await ctx.send('Could not download file...')
                pic=io.BytesIO(await resp.read())
            async with session.get(f"http://thecolorapi.com/id?hex={arg}&format=json") as resp:
                if resp.status != 200:
                    return await ctx.send('Could not download file...')
                dat=json.loads(await resp.read())
        e=discord.Embed(url=picurl,title=f"#{arg}",description=f"you gave me:\n*{orig}*",color=eval(f"0x{arg}"))
        e.set_image(url=picurl)
        e.set_thumbnail(url=f'attachment://{arg}.png')
        e.add_field(name='Name',value=ename(dat))
        e.add_field(name='RGB',value=f"red: {dat['rgb']['r']} ({percnt(dat['rgb']['fraction']['r'])})\ngreen: {dat['rgb']['g']} ({percnt(dat['rgb']['fraction']['g'])})\nblue: {dat['rgb']['b']} ({percnt(dat['rgb']['fraction']['b'])})")
        e.add_field(name='HSL',value=f"hue: {dat['hsl']['h']} ({percnt(dat['hsl']['fraction']['h'])})\nsaturation: {dat['hsl']['s']} ({percnt(dat['hsl']['fraction']['s'])})\nlightness: {dat['hsl']['l']} ({percnt(dat['hsl']['fraction']['l'])})")
        e.add_field(name='CMYK',value=f"cyan: {dat['cmyk']['c']} ({percnt(dat['cmyk']['fraction']['c'])})\nmagenta: {dat['cmyk']['m']} ({percnt(dat['cmyk']['fraction']['m'])})\nyellow: {dat['cmyk']['y']} ({percnt(dat['cmyk']['fraction']['y'])})\nblack: {dat['cmyk']['k']} ({percnt(dat['cmyk']['fraction']['k'])})")
        e.set_footer(text=f"inverted: #{colorInvert(arg)}",icon_url=f"http://www.singlecolorimage.com/get/{colorInvert(arg)}/50x50")
        await ctx.send(embed=e,file=discord.File(io.BytesIO(svg2png(url=f"http://www.thecolorapi.com/id?format=svg&hex={arg}")), f'{arg}.png'))

client.add_cog(jishaku.cog.Jishaku(bot=client))

client.run('TOKEN HERE')
