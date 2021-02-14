const { ApolloServer, gql } = require('apollo-server');
const { RESTDataSource } = require('apollo-datasource-rest');

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

class TracksAPI extends RESTDataSource {
    constructor() {
        super()
        this.baseURL = serverUri
    }

    async getTracks() {
        return this.get('/tracks.json')
    }
}

class PlaylistsAPI extends RESTDataSource {
    constructor() {
        super()
        this.baseURL = serverUri
    }

    async getPlaylists() {
        return this.get('/playlists.json')
    }
}

const resolvers = {
    Query: {
        tracks: async (_source, { ids }, { dataSources }) => {
            return dataSources.tracksAPI.getTracks();
        },

        playlists: async (_source, { ids }, { dataSources }) => {
            return dataSources.playlistsAPI.getPlaylists();
        },
    },

    Playlist: {
        tracks: async (parent, _source, { dataSources }) => {
            return dataSources.tracksAPI.getTracks();
        },
    },
};



const server = new ApolloServer({
    typeDefs, resolvers, playground: true, dataSources: () => {
        return {
            tracksAPI: new TracksAPI(),
            playlistsAPI: new PlaylistsAPI(),
        };
    },
});

// The `listen` method launches a web server.
server.listen().then(({ url }) => {
    console.log(`Server ready at ${url}`);
});