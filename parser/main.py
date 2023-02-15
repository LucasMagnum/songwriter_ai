import os
import logging

import asyncio
import aiofiles
from aiofiles import os as aiofiles_os
from bs4 import BeautifulSoup


async def parse_files(root_dir: str):
    for artist_id in os.listdir(root_dir):
        async for (song_id, song_html_file) in read_artist_folder(
            os.path.join(root_dir, artist_id)
        ):
            content = await parse_html_to_lyrics(song_html_file)
            await save_parsed_lyrics_to_disk(artist_id, song_id, content)


async def read_artist_folder(path: str) -> str:
    for filename in os.listdir(path):
        logging.debug(f"Reading file {filename}")
        pathfile = os.path.join(path, filename)

        async with aiofiles.open(pathfile, mode="r") as f:
            content = await f.read()
            yield filename, content


async def parse_html_to_lyrics(content: str) -> str:
    html = BeautifulSoup(content, "html.parser")
    containers = html.find_all("div", {"data-lyrics-container": "true"})

    text = "".join(container.get_text(separator="\n") for container in containers)
    return clean_text(text)


def clean_text(text: str) -> str:
    return text


async def save_parsed_lyrics_to_disk(artist_id: str, song_id: str, content: str):
    artist_path = f"parsed_files/{artist_id}"

    if not await aiofiles_os.path.exists("parsed_files"):
        await aiofiles_os.mkdir("parsed_files")

    if not await aiofiles_os.path.exists(artist_path):
        await aiofiles_os.mkdir(artist_path)

    async with aiofiles.open(f"{artist_path}/{song_id}", mode="w") as parsed_file:
        await parsed_file.writelines(content)


if __name__ == "__main__":
    logging.basicConfig(format="[%(levelname)s] => %(message)s", level=logging.DEBUG)
    asyncio.run(
        parse_files(os.path.join(os.path.dirname(__name__), "../crawler/raw_files"))
    )
