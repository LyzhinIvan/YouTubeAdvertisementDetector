var video = undefined;
var currentVideoId = undefined;
var adsList = [];
var lastUrl = undefined;
const requestInterval = 10000;

setInterval(function() {
    if (document.URL !== lastUrl) {
        lastUrl = document.URL;
        processPage();
    }
}, 1000);

function processPage() {
    console.log("process page");
    video = document.getElementsByTagName('video')[0];
    if (video !== undefined) {
        processVideo();
        video.onloadstart = processVideo;
        video.ontimeupdate = trackVideoAndSkipAds;
    }
}

function processVideo() {
    var newVideoId = extractVideoIdFromUrl();
    if (newVideoId === currentVideoId) return;
    currentVideoId = newVideoId;
    adsList = [];
    if (currentVideoId) {
        console.log("detected page with video " + currentVideoId);
        loadAds(currentVideoId);
    }
}

function trackVideoAndSkipAds() {
    if (!video) return;
    var currentTime = video.currentTime;
    for (var i = 0; i < adsList.length; ++i) {
        var ad = adsList[i];
        var adStart = ad[0], adFinish = ad[1];
        if (adStart < currentTime && currentTime < adFinish) {
            console.log("skipping ad");
            video.currentTime = ad[1];
        }
    }
}

function loadAds(videoId) {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', 'http://localhost:1234/' + videoId);
    xhr.onload = function() {
        if (xhr.status !== 200) {
            setTimeout(loadAds.bind(this, videoId), requestInterval);
            return;
        }
        if (videoId !== currentVideoId) return;
        var resp = JSON.parse(xhr.responseText);
        console.log(resp);
        if (resp['status'] === 'OK') {
            adsList = resp['ads'];
        } else if (resp['status'] === 'IN_QUEUE') {
            setTimeout(loadAds.bind(this, videoId), requestInterval);
        }
    };
    xhr.onerror = function () {
        setTimeout(loadAds.bind(this, videoId), requestInterval);
    };
    xhr.send();
}

function extractVideoIdFromUrl() {
    return extractUrlParams()['v'];
}

function extractUrlParams() {
    var url = document.URL;
    url = url.substr(url.indexOf('?') + 1);
    var args = url.split('&');
    var params = {};
    for (var index in args) {
        var arg = args[index];
        var sepIdx = arg.indexOf('=');
        var argName = arg.substr(0, sepIdx);
        var argValue = arg.substr(sepIdx+1);
        params[argName] = argValue;
    }
    return params;
}

