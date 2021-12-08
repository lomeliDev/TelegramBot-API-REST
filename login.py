#!/bin/env python3

import asyncio, os, time, sqlite3, sys, socks, sqlite3
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError

re = "\033[1;31m"
gr = "\033[1;32m"
cy = "\033[1;36m"
ot = "\033[1;39m"

clientGlobal = None
cursorGlobal = None
db_name = 'db.db'


def deleteFileClient(phone):
    if os.path.exists("sessions/" + phone + ".session"):
        os.remove("sessions/" + phone + ".session")
    if os.path.exists("sessions/" + phone + ".session-journal"):
        os.remove("sessions/" + phone + ".session-journal")


def clear():
    os.system('clear')


def logo():
    print(f"""
        {re}╔╦╗{cy}┌─┐┬  ┌─┐{re}╔═╗  ╔═╗{cy}┌─┐┬─┐┌─┐┌─┐┌─┐┬─┐
        {re} ║ {cy}├┤ │  ├┤ {re}║ ╦  ╚═╗{cy}│  ├┬┘├─┤├─┘├┤ ├┬┘
        {re} ╩ {cy}└─┘┴─┘└─┘{re}╚═╝  ╚═╝{cy}└─┘┴└─┴ ┴┴  └─┘┴└─
                    Login Account
                    version : 1.0.0
                github.com/lomelidev
                autor : Miguel Lomeli
                exit command: 6666
    """)


def scraper_exit(n):
    if(n == 6666 or n == "6666"):
        print(re + '\nBye. See you soon\n')
        os._exit(0)
        sys.exit(0)
        sys.exit()
        exit()


def cursorClose():
    try:
        cursorGlobal.close()
    except:
        pass


def run_query(query, parameters = ()):
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursorGlobal = cursor
        result = cursor.execute(query, parameters)
        conn.commit()
    return result   


def run_query_count( query, parameters = ()):
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursorGlobal = cursor
        result = cursor.execute(query, parameters)
        rows = cursor.fetchall()
        result = len (rows)
        conn.commit()
        try:
            cursor.close()
        except:
            pass
    return result         


def disconnectGlobal():
    try:
        clientGlobal.disconnect()
    except:
        pass
    try:
        cursorGlobal.close()
    except:
        pass


def main():
    clear()
    logo()

    while True:
        try:
            api_id = input(gr+"[+] enter the api id : "+re)
            scraper_exit(api_id)
            break
        except:
            pass
    while True:
        try:
            api_hash = input(gr+"[+] enter the hash : "+re)
            scraper_exit(api_hash)
            break
        except:
            pass
    while True:
        try:
            phone = input(gr+"[+] enter the phone : "+re)
            scraper_exit(phone)
            break
        except:
            pass
    while True:
        try:
            alias = input(gr+"[+] enter the alias : "+re)
            scraper_exit(alias)
            break
        except:
            pass


    db_proxie = run_query('SELECT * FROM proxies WHERE status=1 ORDER BY RANDOM() LIMIT 1', ())
    proxie = ['', '', '', '']
    for row in db_proxie:
        proxie[0] = str(row[1])
        proxie[1] = str(row[2])
        proxie[2] = str(row[3])
        proxie[3] = str(row[4])
    cursorClose()

    if int(proxie[1]) == 0:
        clear()
        logo()
        print(re+"[!] To use the bot, you need at least one active proxy !!\n")
        sys.exit(1)

    db_count_account = run_query_count('SELECT id FROM accounts WHERE phone=?', (str(phone),))
    if db_count_account > 0:
        clear()
        logo()
        print(re+"[!] Account already exists !!\n")
        sys.exit(1)

    deleteFileClient(phone)

    try:
        client = TelegramClient("sessions/" + phone, api_id, api_hash, proxy=("socks5", proxie[0], int(proxie[1]), True, proxie[2], proxie[3]))
        clientGlobal = client
    except KeyError:
        clear()
        logo()
        print(re+"[!] run python3 setup.py first !!\n")
        sys.exit(1)

    client.connect()
    if not client.is_user_authorized():
        client.sign_in(phone, phone_code_hash=api_hash)
        clear()
        logo()
        while True:
            try:
                code = input(gr+"[+] enter the code : "+re)
                scraper_exit(code)
                break
            except:
                pass
        while True:
            try:
                password = input(gr+"[+] enter the password : "+re)
                scraper_exit(password)
                break
            except:
                pass

        try:
            client.sign_in(phone, code)
        except SessionPasswordNeededError:
            client.sign_in(password=password)

        if not client.is_user_authorized():
            clear()
            logo()
            print(re+"[!] There was an error logging in to the account !!\n")
            try:
                client.disconnect()
            except:
                pass
            sys.exit(1)
        else:
            clear()
            logo()
            print(gr+"[!] Account was successfully saved !!\n")
            query = 'INSERT INTO accounts VALUES(NULL, ?, ?, ?, ?, ?)';
            run_query(query, (api_id,api_hash,phone,alias,1,))
            cursorClose()
            try:
                client.disconnect()
            except:
                pass


if __name__ == "__main__":
    try:
        main()
        disconnectGlobal()
    except KeyboardInterrupt:
        print("Application finished (Keyboard Interrupt)")
        disconnectGlobal()
        sys.exit("Manually Interrupted")
    except Exception as e:
        print(e)
        print("Oh no, something bad happened! Restarting...")
        disconnectGlobal()
        sys.exit("Manually Interrupted")
