const { ApolloServer, gql } = require('apollo-server');
const { RESTDataSource } = require('apollo-datasource-rest');
const fetch = require('node-fetch');


const typeDefs = gql`
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
    }
`;


const serverUri = process.env.TEST_SERVER_URI || "http://localhost:8080"

async function loadTracks() {
    const response = await fetch(serverUri + '/tracks.json');
    return await response.json();
}


async function  loadPlaylists() {
    const response = await fetch(serverUri + '/playlists.json');
    return await response.json();
}


const resolvers = {
    Query: {
        tracks: async (_source, { ids }, { dataSources }) => {
            return await loadTracks();
        },

        playlists: async (_source, { ids }, { dataSources }) => {
            return await loadPlaylists();
        },
    },

    Playlist: {
        tracks: async (parent, _source, { dataSources }) => {
            return await loadTracks();
        },
    },
};



const server = new ApolloServer({
    typeDefs, resolvers, playground: true
});

// The `listen` method launches a web server.
server.listen().then(({ url }) => {
    console.log(`Server ready at ${url}`);
});