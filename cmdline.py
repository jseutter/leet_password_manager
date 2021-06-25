#!/usr/bin/env python3

import ansible.parsing.vault
import argparse
import editor
from getpass import getpass
import json
import os
import re
from secrets import Secrets
import shutil
import subprocess
import sys
import termios
from textwrap import dedent
import tty

def parse_command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', nargs='?', help='the action to perform on secrets')
    args = parser.parse_args()
    return args

def dump_secrets(s):
    print(s.data)

def menu():
    print()
    print('Actions: (f)ind, (l)ist, (q)uit, or an entry Id followed by (p), (u), (h)')

def pbcopy_exists():
    return shutil.which('pbcopy') != None

def pbcopy(text):
    # https://stackoverflow.com/questions/1825692/can-python-send-text-to-the-mac-clipboard
    if pbcopy_exists():
        process = subprocess.Popen('pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
        process.communicate(text.encode('utf-8'))
    else:
        print(text)

def list_(s):
    (columns, lines) = shutil.get_terminal_size()
    begin = 0
    entries = s.entries()
    for end in range(lines-4, len(entries), lines-3):
        subentries = entries[begin:end]
        list_screenful(subentries)
        begin = end
        if end < len(entries):
            print('<space> for more, <q> to quit: ', end='')
            sys.stdout.flush()
            ch = get_ch()
            print()
            if ch == ' ':
                continue
            else:
                break
    print()

def list_screenful(entries):
    fmt = '{0: >5}  {1: <45}  {2: <20}'
    print(fmt.format('Id', 'Title', 'Username'))
    print('='*74)
    for entry in entries:
        print(fmt.format(entry['id'], entry['title'], entry['username']))

def list_raw(s):
    for entry in s.entries():
        print(entry)

def find(s):
    lookfor = input('look for title: ')
    for entry in s.entries():
        if entry['title'].lower().find(lookfor.lower()) >= 0:
            print()
            fmt = '{0: >5}  {1: <45}  {2: <20}'
            print(fmt.format(entry['id'], entry['title'], entry['username']))

def copy_pwd(s, id_):
    for entry in s.entries():
        if id_ == entry['id']:
            print()
            print('Copied password for "{}" to clipboard.'.format(entry['title']))
            pbcopy(entry['password'])

def copy_user(s, id_):
    for entry in s.entries():
        if id_ == entry['id']:
            print()
            print('Copied username for "{}" to clipboard.'.format(entry['title']))
            pbcopy(entry['username'])

def copy_url(s, id_):
    for entry in s.entries():
        if id_ == entry['id']:
            print()
            print('attempting to open {}...'.format(entry['url']))
            os.system("open '{}'".format(entry['url']))

def change_master_password(s):
    confirm = input('Confirm you want to change the master password? (y/n)')
    if confirm == 'y':
        old_keyphrase = getpass('Old keyphrase:')
        keyphrase1 = getpass('New keyphrase:')
        keyphrase2 = getpass('New keyphrase (again):')
        if old_keyphrase != s.keyphrase:
            print('Old keyphrase mismatch.  Cancel.')
        elif keyphrase1 == keyphrase2:
            s.keyphrase = keyphrase1
            s.write()
            print('Keyphrase updated, vault written to disk.')
        else:
            print('Keyphrase mismatch.  Cancel.')
    else:
        print('cancel.')

def edit_entry_old(s, id_):
    for entry in s.entries():
        if id_ == entry['id']:
            print('type in new value, or enter if unchanged.')
            for k, v in entry.items():
                print('{}: {}'.format(k, v))
                new_val = input('input new val, or enter to keep current:')
                if new_val != '':
                    entry[k] = new_val
            print(entry)
            ok = input('keep new values?')
            if ok == 'Y':
                s.write()
            print('remember, there is a bug here.')

def edit_entry(s, id_):
    entry = None
    for e in s.entries():
        if id_ == e['id']:
            entry = e
            break
    else:
        print('invalid entry')
        return
    updated = editor.edit(contents=json.dumps(entry, sort_keys=True, indent=2))
    updated_data = json.loads(updated)
    s.replace_entry(entry, updated_data)
    s.write()

def view_entry(s, id_):
    for e in s.entries():
        if id_ == e['id']:
            entry = e
            break
    else:
        print('invalid entry')
    print(e)

def new_entry(s):
    pristine = {
        'title': '',
        'username': '',
        'password': '',
        'url': '',
        'notes': ''
    }
    while True:
        new = editor.edit(contents=json.dumps(pristine, sort_keys=True, indent=2))
        print(new)
        confirm = input('save changes? y/n/redo:')
        if confirm == 'y':
            try:
                new_entry = json.loads(new)
                s.add_entry(new_entry)
                s.write()
                print('Entry saved.')
            except json.JSONDecodeError:
                response = input('Entry is not valid json.  Keep editing? (y/n):')
                if response == 'y':
                    continue
                else:
                    print('aborting..')
                    break
            return
        elif confirm == 'n':
            return
        elif confirm == 'redo':
            continue

def parse_numeric_action(action):
    match = re.match('([0-9]+)([hupe])', action.strip())
    if match:
        groups = match.groups()
        if len(groups) == 2:
            return int(groups[0]), groups[1]
    return []
    
def get_action():
    return input('what do you want to do? ')

def help_():
    print('Available actions:')
    print('q - quit')
    print('l - list secrets')
    print('raw - raw dump of secrets')
    print('master - change the master password')
    print('help - this menu')
    print('123p - copy the password for entry 123 to the clipboard')
    print('123u - copy the username for entry 123 to the clipboard')
    print('123h - copy the http(s) url for entry 123 to the clipboard')
    print('123e - edit entry 123')
    print('f - enter a string to find matching entries')

def get_ch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def interactive(s):
    while True:
        menu()
        action = get_action()
        numeric_action = parse_numeric_action(action)
        if action == 'q':
            print('quitting.')
            break
        elif action == 'l':
            list_(s)
        elif action == 'raw':
            list_raw(s)
        elif action == 'n':
            new_entry(s)
        elif action == 'master':
            change_master_password(s)
        elif action == 'help':
            help_()
        elif numeric_action:
            (id_, cmd) = numeric_action
            if cmd == 'p':
                copy_pwd(s, id_)
            elif cmd == 'u':
                copy_user(s, id_)
            elif cmd == 'h':
                copy_url(s, id_)
            elif cmd == 'e':
                edit_entry(s, id_)
            elif cmd == 'v':
                view_entry(s, id_)
        elif action == 'f':
            find(s)

def main():
    args = parse_command_line()
    keyphrase = getpass('Keyphrase:')
#    keyphrase = 'password'
    try:
        s = Secrets('vault.yml', keyphrase)
        s.read()
    except ansible.parsing.vault.AnsibleVaultError:
        print('Vault password failed.')
        sys.exit(1)
    if not args.action:
        interactive(s)
    elif args.action == 'jsondump':
        dump_secrets(s)


if __name__ == "__main__":
    main()

