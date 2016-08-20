import multiprocessing
import signal
import requests
import ssl
import json
import BaseHTTPServer
import subprocess
import os
import sys
import time

import logging
from telegram import BotAPI

class ReceiveProcess(multiprocessing.Process):
    def __init__(self, token, q):
        multiprocessing.Process.__init__(self)
        self.q = q
        self.token = token
        self.api = BotAPI(token)

    def setup(self):
        pass

    def run(self):
        raise NotImplementedError()

class APIReceiver(ReceiveProcess):
    def __init__(self, token, q):
        ReceiveProcess.__init__(self, token, q)
        self.offset = None

    def setup(self):
        self.api.remove_webhook()

    def fetch_updates(self):
        logging.log("Fetching updates")
        response = self.api.get_updates(offset = self.offset, timeout = 120) if self.offset != None else self.api.get_updates(timeout = 120)
        updates = response["result"]
        if len(updates) > 0:
            self.offset = updates[len(updates) - 1]["update_id"] + 1
        for update in updates:
            self.q.put(update)

    def run(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN) # Make sure KeyboardInterrupts are not sent to this process
        while True:
            try:
                self.fetch_updates()
            except Exception as e:
                logging.error("An exception occurred inside recv process:\n" + str(e))
                time.sleep(120) # Prevent making unnecessary fetches when Telegram API is down

class WebhookRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write("tgbot running <b style='color:green;'>OK</b>")

    def do_POST(self):
        if self.path != self.server.receiver.webhook_path():
            self.send_error(404)
            return
        try:
            content_len = int(self.headers.getheader("Content-Length", 0))
        except:
            self.send_error(400)
            return
        update_json = self.rfile.read(content_len)
        try:
            update = json.loads(update_json)
        except ValueError:
            logging.error("Could not parse JSON sent to webhook by Telegram")
            self.send_error(400)
            return
        logging.log("Webhook server received update from Telegram")
        self.server.receiver.q.put(update)
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def log_error(self, *args, **kwargs):
        return # Stop debug printing

    def log_message(self, *args, **kwargs):
        return # Stop debug printing

class WebhookServer(BaseHTTPServer.HTTPServer):
    def __init__(self, receiver, port):
        BaseHTTPServer.HTTPServer.__init__(self, ("", port), WebhookRequestHandler)
        self.receiver = receiver

    def upgrade_ssl(self, certificate_path, key_path):
        self.socket = ssl.wrap_socket(self.socket, certfile = certificate_path, keyfile = key_path, server_side = True)

class WebhookReceiver(ReceiveProcess):
    def __init__(self, token, q, port = 8443, openssl_command = "openssl"):
        ReceiveProcess.__init__(self, token, q)
        self.port = port
        self.ip = None
        self.openssl_command = openssl_command

    def fetch_public_ip(self):
        logging.log("Getting public IP address")
        response = requests.get("http://ip.42.pl/raw")
        self.ip = response.text.strip()
        if response.status_code != 200 or len(self.ip) == 0:
            raise Exception("Could not find public IP")
        logging.log("Found IP " + self.ip)

    def webhook_path(self):
        return "/" + self.token

    def webhook_url(self):
        return "https://{0}:{1}{2}".format(self.ip, self.port, self.webhook_path())

    def working_dir(self):
        return os.getcwd()

    def private_key_path(self):
        return self.working_dir() + "/tgbot_priv.key"

    def public_key_path(self):
        return self.working_dir() + "/tgbot_pub.pem"

    def gen_certificate(self):
        logging.log("Generating self-signed certificate pair")
        error = False
        try:
            subprocess.call("{0} req -newkey rsa:2048 -sha256 -nodes -keyout {1} -x509 -days 365 -out {2} -subj \"/CN={3}\"".format(self.openssl_command, self.private_key_path(), self.public_key_path(), self.ip))
        except:
            error = True
        if error or not os.path.exists(self.private_key_path()) or not os.path.exists(self.public_key_path()):
            raise Exception("Could not generate certificate pair, make sure command '{0}' can be run on your machine and {1}, {2} are writable".format(self.openssl_command, self.private_key_path(), self.public_key_path()))

    def setup(self):
        logging.info("Setting up webhook")
        self.fetch_public_ip()
        if not os.path.exists(self.private_key_path()) or not os.path.exists(self.public_key_path()):
            self.gen_certificate()
        self.api.remove_webhook()
        self.api.set_webhook(url = self.webhook_url(), certificate = open(self.public_key_path(), "rb"))

    def run(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN) # Make sure KeyboardInterrupts are not sent to this process
        self.server = WebhookServer(self, self.port)
        self.server.upgrade_ssl(self.public_key_path(), self.private_key_path())
        logging.info("Webhook server started listening to Telegram on " + self.webhook_url())
        self.server.serve_forever()
