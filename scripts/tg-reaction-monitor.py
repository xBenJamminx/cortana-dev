#!/usr/bin/env python3
"""
Telegram Reaction Monitor v6

Watches journalctl for openclaw gateway events.
On cli exec: sends typing to all forum topics + reacts to incoming message.
On sendMessage ok: stop typing, remove reaction, track message_id.
On watchdog timeout: immediately alert Ben which model failed.
On all models failed: send clear failure message.
"""
import re
import subprocess
import sys
import time
import requests
from datetime import datetime
from threading import Timer, Lock

BOT_TOKEN = '8553187574:AAFDKi7lik8TXLIbed3rWcPsLry8E4MuJyg'
API = f'https://api.telegram.org/bot{BOT_TOKEN}'
GROUP_CHAT_ID = -1003856131939
TOPICS = [1, 20, 22, 26, 29, 31]
TYPING_INTERVAL = 4
EYES = '👀'

lock = Lock()

def send_typing_all():
    for tid in TOPICS:
        try:
            requests.post(f'{API}/sendChatAction', json={
                'chat_id': GROUP_CHAT_ID,
                'action': 'typing',
                'message_thread_id': tid
            }, timeout=3)
        except:
            pass

def react(chat_id, message_id, emoji=EYES):
    try:
        r = requests.post(f'{API}/setMessageReaction', json={
            'chat_id': chat_id,
            'message_id': message_id,
            'reaction': [{'type': 'emoji', 'emoji': emoji}],
            'is_big': False
        }, timeout=5)
        return r.ok
    except:
        return False

def unreact(chat_id, message_id):
    try:
        requests.post(f'{API}/setMessageReaction', json={
            'chat_id': chat_id,
            'message_id': message_id,
            'reaction': [],
        }, timeout=5)
    except:
        pass

def send_to_all_topics(text):
    """Send message to all topics so Ben sees it regardless of where he is."""
    sent = False
    for tid in TOPICS:
        try:
            r = requests.post(f'{API}/sendMessage', json={
                'chat_id': GROUP_CHAT_ID,
                'text': text,
                'message_thread_id': tid
            }, timeout=10)
            if r.ok:
                sent = True
        except:
            pass
    return sent

def send_alert(text, topic=1):
    try:
        requests.post(f'{API}/sendMessage', json={
            'chat_id': GROUP_CHAT_ID,
            'text': text,
            'message_thread_id': topic
        }, timeout=10)
    except:
        pass

def log(msg):
    print(f'[{datetime.now():%H:%M:%S}] {msg}', flush=True)

def main():
    log('Telegram reaction monitor v6 started')

    proc = subprocess.Popen(
        ['journalctl', '-u', 'openclaw-gateway', '-f', '-o', 'cat', '--no-pager'],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1
    )

    processing = False
    processing_start = 0
    typing_timer = None
    last_bot_msg_id = 0
    reacted_msg_id = None
    fallback_count = 0  # track how many models have failed this round
    timeout_alerted = False  # only send first timeout alert per incident

    def keep_typing():
        nonlocal typing_timer
        with lock:
            if processing:
                send_typing_all()
                typing_timer = Timer(TYPING_INTERVAL, keep_typing)
                typing_timer.daemon = True
                typing_timer.start()

    def stop_processing():
        nonlocal processing, typing_timer, reacted_msg_id, fallback_count, timeout_alerted
        with lock:
            processing = False
            fallback_count = 0
            timeout_alerted = False
            if typing_timer:
                typing_timer.cancel()
                typing_timer = None
            if reacted_msg_id:
                unreact(GROUP_CHAT_ID, reacted_msg_id)
                reacted_msg_id = None

    for line in proc.stdout:
        line = line.strip()

        if 'Config warnings' in line:
            continue

        # Track outgoing message IDs — response received, reset state
        if '[telegram] sendMessage ok' in line:
            match = re.search(r'chat=(-?\d+)\s+message=(\d+)', line)
            if match:
                msg_id = int(match.group(2))
                last_bot_msg_id = msg_id
                if processing:
                    elapsed = time.time() - processing_start
                    log(f'Response sent after {elapsed:.1f}s (msg={msg_id})')
                    stop_processing()

        # Agent started processing a message
        if '[agent/claude-cli] cli exec' in line:
            now = time.time()
            model_match = re.search(r'model=(\S+)', line)
            model = model_match.group(1) if model_match else 'unknown'

            # If this is a fallback (processing already active), don't reset timer
            if processing and (now - processing_start) < 10:
                continue

            if not processing:
                # Fresh request
                with lock:
                    processing = True
                    processing_start = now
                    fallback_count = 0
                    timeout_alerted = False
                log(f'Agent started: model={model}')
                send_typing_all()

                if typing_timer:
                    typing_timer.cancel()
                typing_timer = Timer(TYPING_INTERVAL, keep_typing)
                typing_timer.daemon = True
                typing_timer.start()
            else:
                # This is a fallback model kicking in
                log(f'Fallback model: {model}')

        # Watchdog killed a model — notify Ben on FIRST timeout only (no per-retry spam)
        if '[agent/claude-cli] cli watchdog timeout' in line:
            model_match = re.search(r'model=(\S+)', line)
            model = model_match.group(1) if model_match else 'model'
            timeout_match = re.search(r'noOutputTimeoutMs=(\d+)', line)
            timeout_s = int(timeout_match.group(1)) // 1000 if timeout_match else '?'

            with lock:
                fallback_count += 1
                already_alerted = timeout_alerted
                if not timeout_alerted:
                    timeout_alerted = True

            log(f'Watchdog timeout: model={model} after {timeout_s}s (alerted={already_alerted})')
            if not already_alerted:
                send_to_all_topics(f'⚠️ {model} timed out — trying fallback...')

        # All models exhausted
        if 'All models failed' in line or 'Embedded agent failed before reply' in line:
            log('All models failed')
            stop_processing()
            send_to_all_topics('❌ All models failed — I\'m back up but that message didn\'t get through. Please resend.')

        # Gateway restart mid-processing
        if 'starting provider' in line and 'Cortana_MoltBot' in line:
            if processing:
                log('Gateway restarted while processing')
                send_to_all_topics('⚠️ Gateway restarted mid-response — please resend your last message.')
                stop_processing()

if __name__ == '__main__':
    main()
