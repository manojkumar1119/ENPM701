from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from smtplib import SMTP, SMTPException
import cv2
from datetime import datetime
from . import config

class Emailer:
    def __init__(self, user=None, password=None, recipients=None):
        self.user = user or config.SMTP_USER
        self.password = password or config.SMTP_PASS
        self.recipients = recipients or config.SMTP_RECIPIENTS

    def send_frame(self, frame, pic_time=None, subject="Block Picked!!!"):
        if pic_time is None:
            pic_time = datetime.now()
        time_str = pic_time.strftime("%Y-%m-%d %H:%M:%S")

        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = self.user
        msg["To"] = ", ".join(self.recipients)

        body = MIMEText(f"Block picked successfully at {time_str}")
        msg.attach(body)

        ok, encoded = cv2.imencode(".jpg", frame)
        if not ok:
            print("Failed to encode image frame.")
            return False
        img = MIMEImage(encoded.tobytes(), name=f"picked_block_{time_str}.jpg")
        img.add_header("Content-Disposition", "attachment", filename=f"picked_block_{time_str}.jpg")
        msg.attach(img)

        try:
            with SMTP(config.SMTP_HOST, config.SMTP_PORT) as s:
                s.ehlo()
                s.starttls()
                s.login(self.user, self.password)
                s.sendmail(self.user, self.recipients, msg.as_string())
            print("Email sent to:", self.recipients)
            return True
        except SMTPException as e:
            print("Email failed:", str(e))
            return False
