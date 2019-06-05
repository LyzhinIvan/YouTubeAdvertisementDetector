var startTime, endTime;
var saved = false;

function onPlayerStateChange(event) {
    if (event.data !== YT.PlayerState.PAUSED || saved) {
        document.getElementById('btn-start-ad').setAttribute('disabled', 'disabled');
        document.getElementById('btn-stop-ad').setAttribute('disabled', 'disabled');
    }
    else {
        document.getElementById('btn-start-ad').removeAttribute('disabled');
        document.getElementById('btn-stop-ad').removeAttribute('disabled');
    }
    updatePlayPauseButton(event.data);
}

function formatTime(timestamp) {
    var hours   = Math.floor(timestamp / 3600);
    var minutes = Math.floor((timestamp - (hours * 3600)) / 60);
    var seconds = Math.floor(timestamp - (hours * 3600) - (minutes * 60));
    var ms      = Math.floor((timestamp - seconds - (hours * 3600) - (minutes * 60)) * 1000);

    if (hours   < 10) {hours   = "0"+hours;}
    if (minutes < 10) {minutes = "0"+minutes;}
    if (seconds < 10) {seconds = "0"+seconds;}
    if (ms < 10) { ms = "0" + ms; }
    if (ms < 100) { ms = "0" + ms; }
    return hours+':'+minutes+':'+seconds + "." + ms;
}

function markStartAd() {
    startTime = player.getCurrentTime();
    document.getElementById('p-start-ad').innerHTML = formatTime(startTime);
    onMark();
}

function markStopAd() {
    endTime = player.getCurrentTime();
    document.getElementById('p-stop-ad').innerHTML = formatTime(endTime);
    onMark();
}

function onMark() {
    var btnSave = document.getElementById('btn-save-ad');
    if (startTime === undefined || endTime === undefined || saved)
        btnSave.setAttribute('disabled', 'disabled');
    else
        btnSave.removeAttribute('disabled');
}

function noAdsClick() {
    var checkBox = document.getElementById('checkbox-no-ads');
    if (checkBox.checked) {
        document.getElementById('btn-start-ad').setAttribute('disabled', 'disabled');
        document.getElementById('btn-stop-ad').setAttribute('disabled', 'disabled');
        document.getElementById('p-start-ad').style.visibility = 'hidden';
        document.getElementById('p-stop-ad').style.visibility = 'hidden';
        if (!saved)
            document.getElementById('btn-save-ad').removeAttribute('disabled');
    } else {
        document.getElementById('btn-start-ad').removeAttribute('disabled');
        document.getElementById('btn-stop-ad').removeAttribute('disabled');
        document.getElementById('p-start-ad').style.visibility = 'visible';
        document.getElementById('p-stop-ad').style.visibility = 'visible';
        onMark();
    }

}

function saveAd() {
    document.getElementById('btn-start-ad').setAttribute('disabled', 'disabled');
    document.getElementById('btn-stop-ad').setAttribute('disabled', 'disabled');
    document.getElementById('btn-save-ad').setAttribute('disabled', 'disabled');
    document.getElementById('btn-save-ad').innerHTML = "Сохранение...";
    var noAd = document.getElementById('checkbox-no-ads').checked;
    $.ajax({
        url: '/save',
        data: {
            videoId: player.getVideoData().video_id,
            startTime: noAd ? -1 : startTime,
            endTime: noAd ? -1 : endTime
        },
        method: 'POST',
        success: function(response) {
            console.log("Response", response);
            saved = true;
            document.getElementById('btn-save-ad').innerHTML = "Сохранено!";
            document.getElementById('btn-skip').innerHTML = "Перейти к следующему видео";
            var scoreElement = document.getElementById('score');
            var score = parseInt(scoreElement.innerHTML) + 1;
            scoreElement.innerHTML = score;
        },
        error: function(response, status) {
            alert(status);
            document.getElementById('btn-start-ad').removeAttribute('disabled');
            document.getElementById('btn-stop-ad').removeAttribute('disabled');
            document.getElementById('btn-save-ad').removeAttribute('disabled');
            document.getElementById('btn-save-ad').innerHTML = "Save";
        }
    });
}

function minus5() {
    player.seekTo(player.getCurrentTime() - 5);
}

function plus5() {
    player.seekTo(player.getCurrentTime() + 5);
}

function prevFrame() {
    player.seekTo(player.getCurrentTime() - 1 / 25);
}

function nextFrame() {
    player.seekTo(player.getCurrentTime() + 1 / 25);
}

var playSymbol = String.fromCharCode(9658);
var pauseSymbol = String.fromCharCode(9612) + String.fromCharCode(9612);

function playStop() {
    var btn = document.getElementById("btn-play-pause");
    if (btn.innerText.substring(0, 1) === playSymbol) {
        player.playVideo();
    } else {
        player.pauseVideo();
    }
}

function updatePlayPauseButton(state) {
    var btn = document.getElementById("btn-play-pause");
    if (state === YT.PlayerState.PAUSED) {
        btn.innerText = playSymbol;
    } else {
        btn.innerText = pauseSymbol;
    }
}