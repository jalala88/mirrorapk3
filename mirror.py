from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.logger import Logger

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import io
import time

from jnius import autoclass

# Android MediaProjection for capturing screen
PythonActivity = autoclass('org.kivy.android.PythonActivity')
MediaProjectionManager = autoclass('android.media.projection.MediaProjectionManager')
Context = autoclass('android.content.Context')

# Capture setup
media_proj_mgr = PythonActivity.mActivity.getSystemService(Context.MEDIA_PROJECTION_SERVICE)
media_proj = None

latest_frame = None

def start_screen_capture():
    global media_proj
    # Ask user for permission (you need to handle this on startup)
    intent = media_proj_mgr.createScreenCaptureIntent()
    PythonActivity.mActivity.startActivityForResult(intent, 1)
    Logger.info("ScreenCapture: Started")

def capture_frame():
    # TODO: implement MediaProjection image grab
    global latest_frame
    # Placeholder for testing: generate black frame
    latest_frame = b"\xff\xd8" + b"\xff\xd9"  # minimal JPEG

class StreamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != '/':
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header('Content-type',
                         'multipart/x-mixed-replace; boundary=frame')
        self.end_headers()
        while True:
            capture_frame()
            if latest_frame:
                try:
                    self.wfile.write(b"--frame\r\n")
                    self.wfile.write(b"Content-Type: image/jpeg\r\n\r\n")
                    self.wfile.write(latest_frame)
                    self.wfile.write(b"\r\n")
                    time.sleep(0.1)
                except:
                    break

def start_server():
    server = HTTPServer(('', 8080), StreamHandler)
    Logger.info("HTTPServer: Started at http://<device-ip>:8080")
    server.serve_forever()

class MirrorApp(App):
    def build(self):
        Clock.schedule_once(lambda dt: threading.Thread(target=start_server).start())
        start_screen_capture()
        return Label(text="Screen Mirror Server\nhttp://<device-ip>:8080")

if __name__ == '__main__':
    MirrorApp().run()
