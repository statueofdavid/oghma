import os, discord
from aiocron import crontab
from replit import db
from discord.ext import commands, tasks

class OnReady_Message(commands.Cog):
  def __init__(self, client, data):
    self.data = data
    self.client = client
    self._last_member = None

    
  def cog_unload(self):
    return

  @commands.Cog.listener()
  async def on_ready(self):
    print('logged in')
    print('Ready')
    self._internal_cron.start()


  @tasks.loop(seconds=1)
  async def _internal_cron(self):
      await crontab('3 7 * * *').next()
      my_secret = int(os.environ['DISCORD_RATIONALITY_DOJO_CHANNEL_ID'])
      ctx = await self.client.fetch_channel(my_secret)
      self._get_idx(1)
      await self.print_current(ctx)


  @commands.Cog.listener()
  async def on_member_join(self, member):
    channel = member.guild.system_channel
    if channel is not None:
        await channel.send('Hi {0.mention}, welcome to the rationality Dojo!'.format(member))
        await member.create_dm()
        await member.dm_channel.send('These are the following commands:')
        await member.dm_channel.send([c.name for c in commands])

  @commands.command()
  async def hello(self, ctx, *, member: discord.Member = None):
    """Says hello"""
    member = member or ctx.author
    if self._last_member is None or self._last_member.id != member.id:
        await ctx.send('Hello {0.name}~'.format(member))
    else:
        await ctx.send('Hello {0.name}... This feels familiar.'.format(member))
    self._last_member = member

  @commands.Cog.listener()
  async def on_member_remove(self, member):
    print(f'{member} has left the server')

  @commands.Cog.listener()
  async def on_message(self, message):
    if message.author == self.client.user:
        return

    if self.client.user.mentioned_in(message):
        await message.channel.send(':wave:')

  def _get_data_sizes(self):
    sizes = []
    total_index_start = [0]
    for ind, v in enumerate(self.data.values()):
      sizes.append(len(v))
      total_index_start.append(total_index_start[ind] + len(v))
    return len(sizes), sizes, total_index_start[-1], total_index_start[:-1], total_index_start[1:]

  def _get_idx(self, increment: int= 0):

    #check if db values instanciated:
    if "book_idx" not in db.keys() or "chapter_idx" not in db.keys():
      self._reset_db()

    #Get the current indices, add by val for the new one
    book_idx, chapter_idx = db["book_idx"], db["chapter_idx"] + increment

    # get current sizes
    book_size, chapter_sizes, total_chapters, chapter_total_index_start, chapter_total_running = self._get_data_sizes()
    
    # use modulo on the book to constrain index
    book_idx = book_idx % book_size

    # set the chapter index to the total index
    chapter_idx = chapter_idx + chapter_total_index_start[book_idx]

    # Perform modulo on the chapter with total size
    chapter_idx = chapter_idx % total_chapters
    # get current book index in reverse from total index list using a generator
    book_idx = [i for i,v in enumerate(chapter_total_running) if chapter_idx < v][0]

    # get the local chapter index
    chapter_idx -= chapter_total_index_start[book_idx]

    # set the db with the new values
    db["book_idx"] = book_idx
    db["chapter_idx"] = chapter_idx

    return chapter_idx, book_idx

  def _reset_db(self):
      db["book_idx"] = 0
      db["chapter_idx"] = 0

  @commands.command('skip')
  async def skip_and_print(self, ctx):
    await ctx.send("skipping to next assignment")
    self._get_idx(1)
    await self.print_current(ctx)

  @commands.command('rewind')
  async def rewind_and_print(self, ctx):
    await ctx.send("reverting to last assignment")
    self._get_idx(-1)
    await self.print_current(ctx)
    
  @commands.command('current')
  async def print_current(self, ctx):
    chapter_idx, book_idx = self._get_idx()
    book_uri = list(self.data.keys())[book_idx]
    chapter_uri = self.data[book_uri][chapter_idx]

    await ctx.send('Here is your latest reading assignment, ya filthy animal')

    embed1 = discord.Embed(title=f"**BOOK {book_idx + 1}**", url=book_uri, description="of *Rationality - From AI to Zombies*", colour=0x87CEEB)
    embed1.set_author(name="Eliezer Yudkowsky")
    await ctx.send(embed=embed1)
    embed2 = discord.Embed(title=f"*chapter {chapter_idx + 1}*", url=chapter_uri, description="Please read this chapter and discuss within one (1) day")
    await ctx.send(embed=embed2)



    