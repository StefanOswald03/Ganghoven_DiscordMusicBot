import discord
from discord.ext import commands
import wavelink
from wavelink import TrackEventPayload

import settings


class Music(commands.Cog):
    vc: wavelink.Player | None = None
    current_track = None
    music_channel = None

    def __init__(self, bot):
        self.bot = bot

    async def setup(self):
        node: wavelink.Node = wavelink.Node(
            uri=settings.LAVALINK_URL,
            password="changeme"
        )
        await wavelink.NodePool.connect(client=self.bot, nodes=[node])

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        print(f"{node} is ready")

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: TrackEventPayload):
        await self.music_channel.send(f"{payload.track.title} started playing")

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: TrackEventPayload):
        await self.music_channel.send(f"{payload.track.title} finished: {payload.reason}")
        if self.vc.queue.is_empty:
            self.current_track = None
            await self.disconnect_from_voice_channel()
        else:
            await self.skip_current_song()

    @commands.command(
        aliases=['p']
    )
    async def play(self, ctx, *search: str):
        if self.vc is None:
            voice_channel = ctx.message.author.voice.channel
            text_channel = ctx.message.channel
            if voice_channel and text_channel:
                self.vc = await voice_channel.connect(cls=wavelink.Player)
                self.music_channel = text_channel

        chosen_track = await wavelink.YouTubeTrack.search(" ".join(search), return_first=True)
        if chosen_track:
            if self.current_track is None:
                self.current_track = chosen_track
                await self.play_current_track()
            else:
                queuing_time = self.current_track.length - self.vc.position
                for track in self.vc.queue:
                    queuing_time = queuing_time + track.length

                queuing_time = queuing_time / 1000
                queuing_time_min = int(queuing_time // 60)
                queuing_time_sec = int(queuing_time % 60)
                self.vc.queue.put(chosen_track)

                embed = discord.Embed(
                    title="Add Song to Queue"
                )
                embed.add_field(name="Interpreter", value=chosen_track.author, inline=False)
                embed.add_field(name="Title", value=chosen_track.title, inline=False)
                embed.add_field(name="Index in Queue", value=f"{self.vc.queue.count}", inline=False)
                embed.add_field(name="Time Until Played", value=f"{queuing_time_min} min {queuing_time_sec} sec",
                                inline=False)
                await self.music_channel.send(embed=embed)

    @commands.command()
    async def skip(self, ctx):
        await self.skip_current_song()

    @commands.command()
    async def pause(self, ctx):
        await self.vc.pause()

    @commands.command()
    async def resume(self, ctx):
        await self.vc.resume()

    @commands.command()
    async def stop(self, ctx):
        self.vc.queue.clear()
        await self.vc.stop()

    @commands.command(
        aliases=['dc']
    )
    async def disconnect(self, ctx):
        await self.disconnect_from_voice_channel()

    async def play_current_track(self):
        if self.current_track and self.vc:
            await self.vc.play(self.current_track)

    async def skip_current_song(self):
        if not self.vc.queue.is_empty:
            self.current_track = self.vc.queue.get()
            await self.play_current_track()
        else:
            self.music_channel.send("No track remaining in the queue!")

    async def disconnect_from_voice_channel(self):
        if self.vc:
            await self.vc.disconnect()
            self.vc = None
            self.music_channel = None


async def setup(bot):
    music_bot = Music(bot)
    await bot.add_cog(music_bot)
    await music_bot.setup()
