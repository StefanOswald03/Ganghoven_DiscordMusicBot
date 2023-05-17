import discord
from discord.ext import commands
import wavelink
from wavelink import TrackEventPayload
from wavelink.ext import spotify
import settings
from urllib.parse import urlparse, parse_qs, urlunparse


async def parse_playlist_url(search_string):
    parsed_url = urlparse(search_string)
    query_params = parse_qs(parsed_url.query)
    query_params.pop('v', None)
    new_query_string = '&'.join([f"{k}={v[0]}" for k, v in query_params.items()])
    new_parsed_url = parsed_url._replace(query=new_query_string, path='/playlist')
    new_url = urlunparse(new_parsed_url)
    return new_url


class Music(commands.Cog):
    vc: wavelink.Player | None = None
    current_track = None
    music_channel = None
    has_been_skipped = False

    def __init__(self, bot):
        self.bot = bot

    async def setup(self):
        sp = spotify.SpotifyClient(client_id=settings.SPOTIFY_CLIENT, client_secret=settings.SPOTIFY_PASSWORD)
        node: wavelink.Node = wavelink.Node(
            uri=settings.LAVALINK_URL,
            password="changeme",
        )
        await wavelink.NodePool.connect(client=self.bot, nodes=[node], spotify=sp)

    # region Events
    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        print(f"{node} is ready")

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: TrackEventPayload):
        await self.music_channel.send(f"{payload.track.title} started playing")

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: TrackEventPayload):
        if self.vc is not None:
            await self.music_channel.send(f"{payload.track.title} finished: {payload.reason}")
            if self.vc.queue.is_empty:
                self.current_track = None
                await self.disconnect_from_voice_channel()
            elif self.has_been_skipped is False:
                await self.skip_current_song()
            else:
                self.has_been_skipped = False

    # endregion

    # region Commands
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

        decoded = spotify.decode_url(search[0])

        if decoded is not None:
            await self.play_spotify_track(search[0], decoded)
        elif search.__len__() == 1 and search[0].__contains__("https://youtube.com") or search[0].__contains__(
                "https://www.youtube.com") and search[0].__contains__("list"):
            search_string = search[0]
            if search_string.__contains__("watch"):
                search_string = await parse_playlist_url(search_string)

            playlist: wavelink.YouTubePlaylist = await wavelink.YouTubePlaylist.search(search_string)
            await self.play_playlist(playlist)

        else:
            chosen_track = await wavelink.YouTubeTrack.search(" ".join(search), return_first=True)
            await self.play_or_queue_new_track(chosen_track)

    @commands.command()
    async def skip(self, ctx):
        self.has_been_skipped = True
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

    # endregion

    # region Methods
    async def play_playlist(self, playlist):

        for track in playlist.tracks[1:]:
            self.vc.queue.put(track)
        self.current_track = playlist.tracks[0]
        await self.play_current_track()

    async def play_or_queue_new_track(self, track):
        if track:
            if self.current_track is None:
                self.current_track = track
                await self.play_current_track()
            else:
                queuing_time = self.current_track.length - self.vc.position
                for track in self.vc.queue:
                    queuing_time = queuing_time + track.length

                queuing_time = queuing_time / 1000
                queuing_time_min = int(queuing_time // 60)
                queuing_time_sec = int(queuing_time % 60)
                self.vc.queue.put(track)

                embed = discord.Embed(
                    title="Add Song to Queue"
                )
                embed.add_field(name="Interpreter", value=track.author, inline=False)
                embed.add_field(name="Title", value=track.title, inline=False)
                embed.add_field(name="Index in Queue", value=f"{self.vc.queue.count}", inline=False)
                embed.add_field(name="Time Until Played", value=f"{queuing_time_min} min {queuing_time_sec} sec",
                                inline=False)
                await self.music_channel.send(embed=embed)

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
            self.vc.queue.clear()
            self.vc = None
            self.music_channel = None

    async def play_spotify_track(self, url, decoded):
        if decoded == spotify.SpotifySearchType.track:
            track = await spotify.SpotifyTrack.search(query=url, return_first=True)
            await self.play_or_queue_new_track(track)
        elif decoded == spotify.SpotifySearchType.album:
            tracks = await spotify.SpotifyTrack.search(query=url)
            await self.play_playlist(tracks)
        elif decoded == spotify.SpotifySearchType.playlist:
            tracks = spotify.SpotifyTrack.iterator(query=url)
            await self.play_playlist(tracks)

    # endregion


async def setup(bot):
    music_bot = Music(bot)
    await bot.add_cog(music_bot)
    await music_bot.setup()
