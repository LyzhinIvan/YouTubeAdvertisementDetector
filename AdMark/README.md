# AdMark
#### Tool for annotation of advertisements in YouTube videos to collect data for models training.

![AdMark screenshot](https://raw.githubusercontent.com/LyzhinIvan/YouTubeAdvertisementDetector/master/AdMark/screenshot.png)

##### Steps to run:
1. Register VK application for authentication purpose (or it is possible to remove authentication part of code).
2. Install MongoDB.
3. Install NodeJS
4. Install dependencies via `npm install`.
5. Specify configuration fields in `.env` file.
6. Fill `videos.txt` with identifiers of YouTube videos which should be annotated.
6. Run server with `node server.js`.