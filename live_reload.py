from httpwatcher import HttpWatcherServer
from tornado.ioloop import IOLoop
from config import config
from app import app_run
from pathlib import Path
import os

"""
Run this to have a live-reload env for development
Your browser of choice should open automatically,
If it doesn't, try setting the BROWSER env var
in the same terminal that you are going to run this in.
"""

def serve(conf, root_folder):
    url = conf['dev_url']
    port = conf['dev_port']
    server = HttpWatcherServer(
        static_root=os.getcwd(), # server from this folder
        # watch these paths for changes
        watch_paths=[Path(root_folder, config['md_folder'])],
        on_reload=lambda: app_run(root_folder), # call this function before reloading
        # the browser
        host=url, # the host to bind to
        port=port, # the port to bind to
        server_base_path="/", # the path ("/" for url/, "/blog" for url/blog ) 
        watcher_interval=1.0, # maximum reload frequency (seconds)
        recursive=True, # watch for changes in static_root recursively
        open_browser=True # automatically attempt to open a web browser
    )
    server.listen()
    try:
        # will keep serving until someone hits Ctrl+C
        IOLoop.current().start()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == '__main__':
    app_root = os.getcwd()
    # Change the current working directory
    os.chdir(config['live_folder'])
    serve(config, app_root)
