import os
import aiohttp
import ujson
from ariadne import QueryType, make_executable_schema, ObjectType
from ariadne.asgi import GraphQL


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


query = QueryType()
playlist = ObjectType("Playlist")
server_uri = os.environ.get("TEST_SERVER_URI", "http://localhost:8080")

session = aiohttp.ClientSession()


async def load_tracks(ids):
    async with session.get(f"{server_uri}/tracks.json") as resp:
        return await resp.json(loads=ujson.loads)


async def load_playlists(ids):
    async with session.get(f"{server_uri}/playlists.json") as resp:
        return await resp.json(loads=ujson.loads)


@playlist.field("tracks")
async def load_tracks_for_playlist(obj, info):
    return await load_tracks(obj["track_ids"])


@query.field("playlists")
async def resolve_playlists(*some, ids):
    return await load_playlists(ids)


@query.field("tracks")
async def resolve_tracks(*some, ids):
    return await load_tracks(ids)

schema = make_executable_schema(type_defs, query, playlist)

app = GraphQL(schema=schema)
