# main.py
import os

import aiohttp
import ujson
import uvloop
from aiohttp import web
from tartiflette import Resolver
from tartiflette_aiohttp import register_graphql_handlers

uvloop.install()
session = aiohttp.ClientSession()


server_uri = os.environ.get("TEST_SERVER_URI", "http://localhost:8080")

type_defs = """
    type Track{
        id: ID
        name: String
    }

    type Playlist{
        id: ID
        title: String
        tracks: [Track]
    }

    type Query {
        playlists(ids: [ID]!): [Playlist]
        tracks(ids: [ID]!): [Track]
}"""


async def _load_tracks(ids):
    async with session.get(f"{server_uri}/tracks.json") as resp:
        return await resp.json(loads=ujson.loads)


async def _load_playlists(ids):
    async with session.get(f"{server_uri}/playlists.json") as resp:
        return await resp.json(loads=ujson.loads)


@Resolver("Query.playlists")
async def resolver_playlists(ctx, ids, *a, **kwargs):
    result = await _load_playlists(ids)
    return result


@Resolver("Query.tracks")
async def resolver_tracks(ctx, ids, *a, **kwargs):
    result = await _load_tracks(ids)
    return result


@Resolver("Playlist.tracks")
async def _load_tracks_for_playlist(ctx, ids, *a, **kwargs):
    result = await _load_tracks(ids)
    return result


# @Resolver("Track")
# async def load_tracks(ctx, ids, *a, **kwargs):
#     result = await _load_tracks(ids)
#     return result


web.run_app(
    register_graphql_handlers(
        web.Application(),
        engine_sdl=type_defs,
        executor_http_methods=["POST", "GET"],
    ),
    port="8000",
)
