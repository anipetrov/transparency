import sys
import time
import logging
import watchdog

from htmlify import *
from watchdog.observers import Observer
from watchdog import events

class Handler(events.FileSystemEventHandler):
    """Logs all the events captured."""

    def is_ipynb(self, event):
        return 'ipynb_checkpoints' not in event.src_path and event.src_path[-6:] == '.ipynb'

    def on_moved(self, event):
        super(Handler, self).on_moved(event)
        self.on_deleted(event)
        

    def on_created(self, event):
        super(Handler, self).on_created(event)
        print "created %s" % event.src_path
        what = 'directory' if event.is_directory else 'file'
        if self.is_ipynb(event):
            Htmlify(event.src_path).modify()


    def on_deleted(self, event):
        super(Handler, self).on_deleted(event)
        if self.is_ipynb(event):
            print 'deleted %s' % event.src_path
            Htmlify(event.src_path).delete()

    def on_modified(self, event):
        super(Handler, self).on_modified(event)
        if self.is_ipynb(event):
            print "modifying %s" % event.src_path
            Htmlify(event.src_path).modify()

if __name__ == "__main__":
    path = './analysis'
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
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