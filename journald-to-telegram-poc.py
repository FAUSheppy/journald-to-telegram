#!/usr/bin/python3

from systemd import journal
import datetime
import time
import sys
import select
import requests

j = journal.Reader()
j.log_level(journal.LOG_INFO)
j.this_boot()
j.this_machine()

j.add_match(_SYSTEMD_UNIT="sheppy-insurgency-01.service")
j.add_match(_SYSTEMD_UNIT="sheppy-insurgency-02.service")

j.seek_tail()
j.get_previous()

p = select.poll()
journal_fd = j.fileno()
poll_event_mask = j.get_events()
p.register(journal_fd, poll_event_mask)

while True:
    if p.poll(1000):
        if j.process() == journal.APPEND:
            for entry in j:
                msg = entry["MESSAGE"]
                token1 = '" say_team "'
                token2 = '" say "'
                if token1 in msg or token2 in msg:
                    stuff, nameAndContent = msg.split(': "')
                    server = entry['_SYSTEMD_UNIT'].split("sheppy-")[1].split(".service")[0]
                    nameAndContent = nameAndContent.replace(token1, "\n")
                    nameAndContent = nameAndContent.replace(token2, "\n")
                    nameAndContent = nameAndContent.strip("\n").strip('"')
                    requests.post("http://localhost:5012/send-all",
                                json={ "message" : server + ": " + nameAndContent})
