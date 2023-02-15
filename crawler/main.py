"""
Crawl Genius.com extract lyrics from a specific Artist.
"""
import logging
from collections.abc import Callable
from typing import Any

import aiohttp
import asyncio
from aiofiles import open, os


base_api_url = "https://genius.com/api"


async def crawl_songs(artists_ids: list[str]) -> dict[str]:
    lyrics = {}

    for artist_id in artists_ids:
        logging.debug(f"Crawling for artist -> {artist_id}")

        async for song in get_list_of_songs_for_artist(artist_id, 60):
            logging.debug(f"Crawling for song -> {song['id']}")

            if await is_song_already_saved(artist_id, song["id"]):
                logging.debug(f"Already saved, skipping {song['id']}")
                continue

            song_lyrics = await get_lyrics_for_song_id(song["url"])

            await save_lyrics_to_disk(artist_id, song["id"], song_lyrics)
            # lyrics[song["full_title"]] = await parse_lyrics_from_song(song_lyrics)

    return lyrics


async def get_list_of_songs_for_artist(
    artist_id: str, next_page: str = None
) -> list[dict[str, str]]:
    artist_songs_path = f"{base_api_url}/artists/{artist_id}/songs"

    if next_page is not None:
        artist_songs_path = f"{artist_songs_path}?page={next_page}"

    content = await get_json(artist_songs_path)

    if not content or not content.get("response", {}).get("songs"):
        yield []

    for song in content["response"]["songs"]:
        yield song

    if next_page := content["response"]["next_page"]:
        async for song in get_list_of_songs_for_artist(artist_id, next_page):
            yield song


async def get_lyrics_for_song_id(lyrics_url: str) -> str:
    content = await get_text(lyrics_url)

    if not content:
        return

    return content


async def is_song_already_saved(artist_id: str, song_id: str):
    song_path = f"raw_files/{artist_id}/{song_id}"
    return await os.path.exists(song_path)


async def save_lyrics_to_disk(artist_id: str, song_id: str, content: str):
    artist_path = f"raw_files/{artist_id}"

    if not await os.path.exists("raw_files"):
        await os.mkdir(artist_path)

    if not await os.path.exists(artist_path):
        await os.mkdir(artist_path)

    async with open(f"raw_files/{artist_id}/{song_id}", "w") as raw_file:
        await raw_file.writelines(content)


async def parse_lyrics_from_song(song: str) -> str:
    return song


async def get_json(path: str) -> dict[str, str]:
    async with aiohttp.ClientSession() as session:
        logging.debug(f"Requesting path -> {path}")
        async with session.get(path) as response:
            if response.status != 200:
                print("Request error -> ", path)
                return

            return await response.json()


async def get_text(path: str) -> str:
    async with aiohttp.ClientSession() as session:
        logging.debug(f"Requesting path -> {path}")
        async with session.get(path) as response:
            if response.status != 200:
                print("Request error -> ", path)
                return

            return await response.text()


if __name__ == "__main__":
    artists_ids = [
        # "214301", # NF songs
        "45",  # Eminem
    ]
    logging.basicConfig(format="[%(levelname)s] => %(message)s", level=logging.DEBUG)
    asyncio.run(crawl_songs(artists_ids))
