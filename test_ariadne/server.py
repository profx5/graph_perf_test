import os
import aiohttp
from ariadne import QueryType, make_executable_schema, ObjectType
from ariadne.asgi import GraphQL
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route



with open("../schema.gql") as f:
    type_defs = f.read()


query = QueryType()
playlist = ObjectType("Playlist")
server_uri = os.environ.get("TEST_SERVER_URI", "http://localhost:8080")


async def load_tracks(ids):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{server_uri}/tracks.json") as resp:
            return await resp.json()


async def load_playlists(ids):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{server_uri}/playlists.json") as resp:
            return await resp.json()


@playlist.field("tracks")
async def load_tracks_for_playlist(obj, info):
    return await load_tracks(obj["track_ids"])


@query.field("playlists")
async def resolve_playlists(*some, ids):
    return await load_playlists(ids)


@query.field("tracks")
async def resolve_tracks(*some, ids):
    return await load_tracks(ids)

async def ping(request):
    return PlainTextResponse("pong")

schema = make_executable_schema(type_defs, query, playlist)

app = Starlette(routes=[Route("/ping/", ping)])
app.mount("/graphql", GraphQL(schema))
