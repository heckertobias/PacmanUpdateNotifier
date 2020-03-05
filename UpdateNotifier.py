import subprocess
import re
import smtplib
from email.message import EmailMessage

import smtp_settings

paccmd = 'pacman -Syu --print'
regexp = r'\/(?P<package>[a-z-]*[a-z])-(?P<version>[0-9.-]*)-'
dateformat = ""

def get_pacman_print():
    p = subprocess.Popen(paccmd.split(' '), stdout=subprocess.PIPE)
    data = p.communicate()
    return data[0].decode().splitlines()

def get_hostname():
    p = subprocess.Popen(['cat', '/etc/hostname'], stdout=subprocess.PIPE)
    data = p.communicate()
    return data[0].decode()

def get_package_and_version(url):
    r = re.search(regexp, url)
    return (r.group('package'), r.group('version'))

def build_email(packages):
    hostname = 'testhost'#get_hostname()
    msg_text = "The following updates are available on " + hostname + ":\n\n"
    msg_text += "{:45}| {}\n".format("Package", "Version")
    msg_text += "---------------------------------------------+--------------\n"
    for p in packages:
        msg_text += "{:45}| {}\n".format(p[0], p[1])
    if smtp_settings.sshhost != "" and smtp_settings.sshlogin != "":
        msg_text += "\nPlease go to ssh://" + smtp_settings.sshlogin + "@" + smtp_settings.sshhost + " and install the updates via 'pacman -Syu'."

    msg = EmailMessage()
    msg['Subject'] = "New updates available on " + hostname
    msg['From'] = smtp_settings.sender
    msg['To'] = smtp_settings.reciver
    msg.set_content(msg_text)

    server = smtplib.SMTP(smtp_settings.server, smtp_settings.port)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(smtp_settings.username, smtp_settings.password)
    server.send_message(msg)

if __name__ == "__main__":
    paclines = get_pacman_print()
    packages = [get_package_and_version(line) for line in paclines if line.startswith('http')]
    build_email(packages)