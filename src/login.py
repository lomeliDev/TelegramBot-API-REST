#!/bin/env python3

import asyncio, os, time, sqlite3, sys, socks, threading
from telethon.sync import TelegramClient

cursorLoginGlobal = None
db_name = 'db.db'

def cursorClose():
    global cursorLoginGlobal
    try:
        cursorLoginGlobal.close()
    except:
        pass

def run_query(query, parameters = ()):
    global cursorLoginGlobal
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursorLoginGlobal = cursor
        result = cursor.execute(query, parameters)
        conn.commit()
    return result   

def run_query_count( query, parameters = ()):
    global cursorLoginGlobal
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursorLoginGlobal = cursor
        result = cursor.execute(query, parameters)
        rows = cursor.fetchall()
        result = len (rows)
        conn.commit()
        try:
            cursor.close()
        except:
            pass
    return result

def closeCheckLogin(id):
    cursorClose()
    query = 'UPDATE accounts SET status=? where id=?'
    run_query(query, (3,id,))
    cursorClose()

def _checkLogin(data):
    try:
        db_proxie = run_query('SELECT * FROM proxies WHERE status=1 ORDER BY RANDOM() LIMIT 1', ())
        proxie = ['', '', '', '']
        for row in db_proxie:
            proxie[0] = str(row[1])
            proxie[1] = str(row[2])
            proxie[2] = str(row[3])
            proxie[3] = str(row[4])
        cursorClose()

        client = None

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            client = TelegramClient("sessions/" + str(data[3]), str(data[1]), str(data[2]), proxy=("socks5", str(proxie[0]), int(proxie[1]), True, proxie[2], proxie[3]), loop=loop)
        except Exception as e:
            closeCheckLogin(int(data[0]))
            return
        except:
            closeCheckLogin(int(data[0]))
            return

        client.connect()
        query = 'UPDATE accounts SET status=? where id=?'
        if not client.is_user_authorized():
            run_query(query, (2,int(data[0]),))
        else:
            run_query(query, (1,int(data[0]),))

        cursorClose()
        client.disconnect()
    except Exception as e:
        closeCheckLogin(int(data[0]))
        pass
    except:
        closeCheckLogin(int(data[0]))
        pass

def checkLogins(jsonify, request):
    print('checkLogins')
    global cursorLoginGlobal
    try:
        
        db_proxie = run_query('SELECT * FROM proxies WHERE status=1 ORDER BY RANDOM() LIMIT 1', ())
        proxie = ['', '', '', '']
        for row in db_proxie:
            proxie[0] = str(row[1])
            proxie[1] = str(row[2])
            proxie[2] = str(row[3])
            proxie[3] = str(row[4])
        cursorClose()

        if int(proxie[1]) == 0:
            return jsonify({'status': 422, 'message': 'To use the bot, you need at least one active proxy', 'payload': {}})

        db_accounts = run_query('SELECT * FROM accounts WHERE status=1 or status=4', ())
        accounts = []
        for row in db_accounts:
            accounts.append(row)
        cursorClose()
        
        for row in accounts:
            query = 'UPDATE accounts SET status=? where status=1'
            run_query(query, (0,))
            cursorClose()

        for row in accounts:
            t = threading.Thread(target=_checkLogin, args=(row,))
            t.start()
        
        return jsonify({'status': 200, 'message': 'Accounts are being verified', 'payload': {}})
    except Exception as e:
        return jsonify({'status': 422, 'message': str(e), 'payload': {}})
    except :
        return jsonify({'status': 422, 'message': 'An error occurred while parsing the accounts', 'payload': {}})

def StatusLogins(jsonify, request):
    print('StatusLogins')
    global cursorLoginGlobal
    try:
        cursorClose()
        db_accounts = run_query('SELECT status FROM accounts', ())
        data = [0, 0, 0, 0, 0]
        for row in db_accounts:
            data[int(row[0])] = data[int(row[0])] + 1
        cursorClose()

        return jsonify({'status': 200, 'message': 'Account details', 'payload': data})

    except Exception as e:
        return jsonify({'status': 422, 'message': str(e), 'payload': {}})
    except :
        return jsonify({'status': 422, 'message': 'An error occurred while parsing the accounts', 'payload': {}})

