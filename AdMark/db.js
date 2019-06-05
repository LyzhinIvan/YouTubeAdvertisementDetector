let mongoClient;
let db;
let col;

function getMongoConnectionUrl() {
    const env = process.env;
    const m_user = env.MONGO_USER;
    const m_pwd = env.MONGO_PASSWORD;
    const user_part_url = m_user ? `${m_user}:${m_pwd}@` : '';
    const m_host = env.MONGO_HOST || "localhost";
    const m_port = env.MONGO_PORT || 27017;
    const m_db = env.MONGO_DATABASE || "admark";
    return `mongodb://${user_part_url}@${m_host}:${m_port}/${m_db}`;
}

require("mongodb").MongoClient.connect(getMongoConnectionUrl(), function(err, client) {
    if (err) {
        console.log(err);
    }
    mongoClient = client;
    db = mongoClient.db("admark");
    col = db.collection("markups");
});

module.exports = {
    saveAd: function(clientId, videoId, startAd, finishAd) {
        const markup = {
            clientId: clientId,
            videoId: videoId,
            startAd: startAd,
            finishAd: finishAd
        };
        col.insertOne(markup, function (err, result) {
            if (err) {
                return console.log(err);
            }
            console.log(result.ops);
        });
    },

    getScore: function(clientId, callback) {
        col.count({
            clientId: clientId
        }, function(err, result) {
            if (err) {
                console.log(err);
                callback(0);
            } else {
                callback(result);
            }
        });
    },

    isNewUser: function(clientId, callback) {
        col.count({
            clientId: clientId
        }, function(err, result) {
            if (err) {
                console.log(err);
                callback(true);
            }
            else {
                callback(result === 0);
            }
        })
    }
};