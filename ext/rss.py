from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import aiohttp
import aiosqlite
import asyncio
import discord
import feedparser
import json
import logging
import os
import pytz
import time
import toml


log = logging.getLogger('adjutant.rss')


class RSS:
    def __init__(self, bot):
        self.bot = bot
        self.DATA_PATH = './data/rss/'
        self.FEEDS_FILE = 'feeds.toml'
        if os.path.isdir(self.DATA_PATH) is False:
            os.makedirs(self.DATA_PATH)
        if os.path.isfile(self.DATA_PATH + self.FEEDS_FILE) is False:
            open(self.DATA_PATH+self.FEEDS_FILE, 'a').close()
        self.feeds = toml.load(self.DATA_PATH + self.FEEDS_FILE)

        self.SLEEP_DELAY = float(self.bot.CONFIG['sc2oe']['sleepDelay'])
        self.MAX_POSTS = int(self.bot.CONFIG['sc2oe']['maxPosts'])-1

    @staticmethod
    async def fetch_feed(url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                raw_feed = await response.text()
                return feedparser.parse(raw_feed)

    async def read_feeds_in_background(self):
        await self.bot.wait_until_ready()
        while True:
            for feed in self.feeds['feeds']:
                log.info(f'RSS check: {feed}')
                feed_data = await self.fetch_feed(self.feeds['feeds'][feed]['feedURL'])
                for key in range(len(feed_data['entries'])-(len(feed_data['entries'])-self.MAX_POSTS), -1, -1):
                    msg = f"{self.feeds['feeds'][feed]['name']}: {feed_data['entries'][key]['title']}"
                    if len(feed_data['entries'][key]['summary']) <= 200:
                        em = discord.Embed(title=feed_data['entries'][key]['title'],
                                           colour=discord.Colour(int(self.feeds['feeds'][feed]['colour'], 16)),
                                           description=BeautifulSoup(feed_data['entries'][key]['summary'], 'html.parser').text.rstrip('More')
                                           )
                    else:
                        em = discord.Embed(title=feed_data['entries'][key]['title'],
                                           colour=discord.Colour(int(self.feeds['feeds'][feed]['colour'], 16)),
                                           description=BeautifulSoup(feed_data['entries'][key]['summary'][:197]+"...", 'html.parser').text.rstrip('More')
                                           )
                    em.set_author(name=self.feeds['feeds'][feed]['name'],
                                  icon_url=self.feeds['feeds'][feed]['icon'])
                    em.add_field(name='\u200b',
                                 value=f"[**READ MORE**]({self.feeds['feeds'][feed]['blogURL']}{feed_data['entries'][key]['id'].split('/')[-1]})",
                                 inline=False)
                    em.set_footer(text=f"Published at {time.strftime('%b %d, %H:%M', feed_data['entries'][key]['published_parsed'])} UTC")
                    log.info(f'{msg}')
                    async with aiosqlite.connect('./data/db/adjutant.sqlite3') as db:
                        sql = "SELECT * FROM guilds;"
                        cursor = await db.execute(sql)
                        guilds = await cursor.fetchall()
                        await cursor.close()
                    for guild in guilds:
                        if guild[6] != -1:
                            if guild[8] == '':
                                feed_dict = dict()
                                for feedName in self.feeds['feeds']:
                                    feed_dict[feedName] = []
                            else:
                                feed_dict = json.loads(guild[8])
                            feed_channel = self.bot.get_channel(guild[6])
                            if feed_channel.permissions_for(feed_channel.guild.me).send_messages and not feed_data['entries'][key]['id'].split('/')[-1] in feed_dict[feed]:
                                await feed_channel.send(msg, embed=em)
                                feed_dict[feed].append(feed_data['entries'][key]['id'].split('/')[-1])
                                async with aiosqlite.connect('./data/db/adjutant.sqlite3') as db:
                                    sql = "UPDATE guilds SET fids = ? WHERE id = ?;"
                                    try:
                                        await db.execute(sql, (json.dumps(feed_dict), feed_channel.guild.id,))
                                    except Exception as e:
                                        await db.rollback()
                                        chan = self.bot.get_channel(477110208225738752)
                                        await chan.send(f'```py\n{e.__class__.__name__}: {e}\n```')
                                    finally:
                                        await db.commit()
            next_update_time = datetime.now(tz=pytz.utc) + timedelta(minutes=self.SLEEP_DELAY)
            log.info(f'Next rss feed check at {next_update_time:%b %d, %H:%M (%Z)}')
            await asyncio.sleep(self.SLEEP_DELAY * 60.)


def setup(bot):
    n = RSS(bot)
    bot.add_cog(n)
    bot.loop.create_task(n.read_feeds_in_background())
