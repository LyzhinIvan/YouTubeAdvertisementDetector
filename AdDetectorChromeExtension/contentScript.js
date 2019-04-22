window.addEventListener("load", function() {
    processVideo();
    var video = document.getElementsByTagName('video')[0];
    video.onloadstart = processVideo;
});

function processVideo() {
    var url = document.URL;
    url = url.substr(url.indexOf('?') + 1);
    var args = url.split('&');
    var videoId = undefined;
    for (var index in args) {
        var arg = args[index];
        var sepIdx = arg.indexOf('=');
        var argName = arg.substr(0, sepIdx);
        if (argName === 'v') {
            videoId = arg.substr(sepIdx + 1);
        }
    }
    if (videoId) {
        console.log("detected page with video " + videoId);
        var xhr = new XMLHttpRequest();
        xhr.open('GET', 'http://localhost:1234/' + videoId);
        xhr.onload = function() {
            var resp = JSON.parse(xhr.responseText);
            console.log(resp['ads']);
        };
        xhr.send();
    }
}

