import sys
import time
import logging
import watchdog

from htmlify import *
from watchdog.observers import Observer
from watchdog import events

class Handler(events.FileSystemEventHandler):
    """Logs all the events captured."""

    def on_moved(self, event):
        super(Handler, self).on_moved(event)
        # handle movement.. delete old file etc.
        pass
        

    def on_created(self, event):
        super(Handler, self).on_created(event)

        what = 'directory' if event.is_directory else 'file'
        is_ipynb = event.src_path[-6:] == '.ipynb'
        if is_ipynb:
            Htmlify(event.src_path).write_html()


    def on_deleted(self, event):
        super(Handler, self).on_deleted(event)
        is_ipynb = event.src_path[-6:] == '.ipynb'
        if is_ipynb:
            # delete relevant html
            pass

    def on_modified(self, event):
        super(Handler, self).on_modified(event)
        is_ipynb = event.src_path[-6:] == '.ipynb'
        if is_ipynb:
            print "modifying..."
            Htmlify(event.src_path).write_html()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    event_handler = Handler()
    observer = watchdog.observers.Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()