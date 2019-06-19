# Advertisement Detector Server

REST server to responds to queries for detection of ads in YouTube videos.

##### Steps to run:
1. Install RabbitMQ.
2. Install MongoDB.
3. Specify connection parameters for RabbitMQ and MongoDB (example of config file can be found in root of repository).
4. Set environmental variable `CONFIG_PATH` with absolute path to config file.
5. Install requirements via `pip install -r requirements.txt`.
6. Run server via `python server.py`.

