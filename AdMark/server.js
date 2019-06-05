require('dotenv').config();
const express = require('express');
const request = require('request');
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const fs = require('fs');
const db = require('./db');

const app = express();

app.set('view engine', 'jade');

app.use('/scripts', express.static(__dirname + '/scripts'));
app.use('/styles', express.static(__dirname + '/styles'));
app.use(bodyParser.json()); // for parsing application/json
app.use(bodyParser.urlencoded({extended: true})); // for parsing application/json
app.use(cookieParser());

const videos = fs.readFileSync('videos.txt', 'utf8').split('\n').map(v => v.trim());

const clientByToken = {};
const TEMPLATES_DIR = __dirname + '/templates';

app.get('/', function(req, res) {
    const token = req.cookies.token;
    if (token && clientByToken[token]) {
        const client = clientByToken[token];
        const videoId = getNextVideo();
        console.log("client", client, 'taked video', videoId);
        db.getScore(client, function(score) {
            res.render(TEMPLATES_DIR + '/index.jade', {
                videoId: videoId,
                score: score
            });
        });
    } else {
        res.redirect('/login');
    }
});

app.get('/login', function(req, res, next) {
    const token = req.cookies.token;
    if (token && clientByToken[token]) {
        res.redirect('/');
    } else {
        res.render(TEMPLATES_DIR + '/login.jade', {
            appId: process.env.VK_APP_ID,
            authURL: getAuthUrl(req)
        });
    }
});

app.get('/logout', function(req, res) {
    console.log('logout');
    res.clearCookie('token');
    res.redirect('/');
});

app.post('/save', function (req, res, next) {
    console.log("save", req.body);
    const token = req.cookies.token;
    if (token && clientByToken[token]) {
        db.saveAd(clientByToken[token], req.body.videoId, req.body.startTime, req.body.endTime);
        res.json({
            status: 'OK'
        });
    } else {
        res.status(401);
    }
});

app.get('/auth', function(req, res, next) {
    if (req.query.code) {
        const appId = process.env.VK_APP_ID;
        const redirectUri = getAuthUrl(req);
        const appSecret = process.env.VK_APP_SECRET;
        const url = "https://oauth.vk.com/access_token" +
            "?client_id=" + appId +
            "&client_secret=" + appSecret +
            "&redirect_uri=" + redirectUri +
            "&code=" + req.query.code;
        request(url, function(error, response, body) {
            console.log("error", error);
            console.log("statusCode", response && response.statusCode);
            console.log("body", body);
            body = JSON.parse(body);
            clientByToken[body.access_token] = body.user_id;
            res.cookie('token', body.access_token);
            db.isNewUser(body.user_id, function(isNew) {
                if (isNew)
                    res.redirect('/help');
                else
                    res.redirect('/');
            });
        });
    }
});

app.get('/help', function(req, res) {
    res.render(TEMPLATES_DIR + '/help.jade');
});

function getAuthUrl(req) {
    return req.protocol + "://" + req.get('host') + "/auth";
}

function getNextVideo() {
    return videos[Math.floor(Math.random() * videos.length)];
}

app.use(express.static(__dirname + "/public"));

const PORT = process.env.PORT || 5000;
console.log("Listening on port", PORT);
app.listen(PORT);