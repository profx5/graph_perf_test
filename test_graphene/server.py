import graphene
import aiohttp
import os
import ujson
from graphql.execution.executors.asyncio import AsyncioExecutor
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.graphql import GraphQLApp
from starlette.graphql import GraphQLApp


server_uri = os.environ.get("TEST_SERVER_URI", "http://localhost:8080")
session = aiohttp.ClientSession()


async def load_tracks(ids):
    async with session.get(f"{server_uri}/tracks.json") as resp:
        return await resp.json(loads=ujson.loads)


async def load_playlists(ids):
    async with session.get(f"{server_uri}/playlists.json") as resp:
        return await resp.json(loads=ujson.loads)


class TrackGraphQL(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()

    class Meta:
        name = "Track"


class PlaylistGraphQL(graphene.ObjectType):
    id = graphene.ID()
    title = graphene.String()
    tracks = graphene.List(TrackGraphQL)

    class Meta:
        name = "Playlist"

    async def resolve_tracks(parent, info):
        ids = parent["track_ids"]
        return await load_tracks(ids)


class RootQuery(graphene.ObjectType):
    tracks = graphene.List(TrackGraphQL, ids=graphene.List(graphene.Int))
    playlists = graphene.List(PlaylistGraphQL, ids=graphene.List(graphene.Int))

    async def resolve_tracks(self, info, ids):
        return await load_tracks(ids)

    async def resolve_playlists(self, info, ids):
        return load_playlists(ids)


routes = [
    Route(
        "/",
        GraphQLApp(
            schema=graphene.Schema(query=RootQuery), executor_class=AsyncioExecutor
        ),
    )
]

app = Starlette(routes=routes)
