#!/bin/env python3

import asyncio, os, time, sqlite3, sys, socks, threading
from telethon.sync import TelegramClient
from telethon.tl.types import UserStatusOnline, UserStatusRecently, UserStatusOffline, UserStatusLastWeek, UserStatusLastMonth
from datetime import datetime, timedelta

cursorScrapperGlobal = None
db_name = 'db.db'

def cursorClose():
    global cursorScrapperGlobal
    try:
        cursorScrapperGlobal.close()
    except:
        pass

def run_query(query, parameters = ()):
    global cursorScrapperGlobal
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursorScrapperGlobal = cursor
        result = cursor.execute(query, parameters)
        conn.commit()
    return result   

def run_query_count( query, parameters = ()):
    global cursorScrapperGlobal
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursorScrapperGlobal = cursor
        result = cursor.execute(query, parameters)
        rows = cursor.fetchall()
        result = len (rows)
        conn.commit()
        try:
            cursor.close()
        except:
            pass
    return result

def _scrapper(account, channel, id_campaign, photo, limit, usernameCheck):
    global cursorScrapperGlobal
    channel = channel.replace("@", "")
    channel = channel.replace("/", "")

    try:
        db_proxie = run_query('SELECT * FROM proxies WHERE status=1 ORDER BY RANDOM() LIMIT 1', ())
        proxie = ['', '', '', '']
        for row in db_proxie:
            proxie[0] = str(row[1])
            proxie[1] = str(row[2])
            proxie[2] = str(row[3])
            proxie[3] = str(row[4])
        cursorClose()

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            client = TelegramClient("sessions/" + str(account[3]), str(account[1]), str(account[2]), proxy=("socks5", str(proxie[0]), int(proxie[1]), True, proxie[2], proxie[3]), loop=loop)
        except Exception as e:
            run_query('UPDATE campaigns SET status=? where id=?', (2,id_campaign,))
            cursorClose()
            return
        except:
            run_query('UPDATE campaigns SET status=? where id=?', (2,id_campaign,))
            cursorClose()
            return

        client.connect()
        if not client.is_user_authorized():
            run_query('UPDATE campaigns SET status=? where id=?', (2,id_campaign,))
            cursorClose()
            client.disconnect()
            return

        clients = []
        all_participants = client.get_participants(channel, aggressive=True, limit=limit)

        for user in all_participants:

            checkStatus = False

            if user.id == None:
                continue

            if user.deleted != False:
                continue
            
            if user.bot != False:
                continue
                
            if user.scam != False:
                continue
                
            if user.fake != False:
                continue

            if isinstance(user.status, UserStatusOnline):
                checkStatus = True
            
            if isinstance(user.status, UserStatusRecently):
                checkStatus = True
            
            if isinstance(user.status, UserStatusLastWeek):
                checkStatus = True

            if isinstance(user.status, UserStatusLastMonth):
                checkStatus = True

            if usernameCheck == True:
                if user.username == None:
                    continue

            if photo == True:
                if user.photo != None:
                    checkStatus = True

            if isinstance(user.status, UserStatusOffline):
                last = datetime.now() - timedelta(days=30)
                userDate = datetime(int(user.status.was_online.year), int(user.status.was_online.month), int(user.status.was_online.day))

                if userDate >= last:
                    checkStatus = True

            if checkStatus == False:
                continue

            id = ''
            access_hash = ''
            username = ''
            name = ''
            phone = ''

            if user.phone != None:
                phone = user.phone
            
            if user.username != None:
                username = user.username

            if user.access_hash != None:
                access_hash = user.access_hash
            
            if user.id != None:
                id = user.id
            
            if user.first_name != None:
                name = user.first_name
            
            if user.last_name != None:
                name = name + " " + user.last_name

            dataClient = {
                'id': id,
                'access_hash': access_hash,
                'username': username,
                'name': name,
                'phone': phone
            }
            
            clients.append(dataClient)

        client.disconnect()

        for user in clients:
            search_id = run_query_count('SELECT id FROM users WHERE campaign_id=? AND uuid=?', (id_campaign, user['id']))
            if search_id == 0:
                query = 'INSERT INTO users VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)';
                run_query(query, (id_campaign, 0, user['id'], user['access_hash'], user['username'], user['name'], user['phone'], "", 1, 0,))
                cursorClose()

        total_users = run_query_count('SELECT id FROM users WHERE campaign_id=?', (id_campaign,))
        query = 'UPDATE campaigns SET total_users=? where id=?'
        run_query(query, (total_users, id_campaign,))
        cursorClose()

        run_query('UPDATE campaigns SET status=? where id=?', (1,id_campaign,))
        cursorClose()

        print("\n\n")
        print("Total users extracted : " + str(len(clients)))
        print("Total users in  campaign : " + str(total_users))
        print("\n\n")

    except:
        run_query('UPDATE campaigns SET status=? where id=?', (2,id_campaign,))
        cursorClose()
        return


def scrapper(jsonify, request):
    print('scrapper')
    global cursorScrapperGlobal
    try:
        cursorClose()

        try:
            channel = request.json['channel']
            campaign = request.json['campaign']
            group = request.json['group']
            photo = request.json['photo']
            limit = int(request.json['limit'])
            seconds = str(request.json['seconds'])
            username = request.json['username']
            index = channel.find("http")
            if index >= 0:
                return jsonify({'status': 422, 'message': 'Just pass the user', 'payload': {}})
        except:
            return jsonify({'status': 422, 'message': 'Send all parameters', 'payload': {}})

        db_accounts = run_query('SELECT * FROM accounts WHERE status=1 ORDER BY RANDOM() LIMIT 1', ())
        account = None
        for row in db_accounts:
            account = row
        cursorClose()

        if account == None:
            return jsonify({'status': 422, 'message': 'There is no assigned account', 'payload': {}})

        total_campaigns = run_query_count('SELECT id FROM campaigns WHERE name=?', (campaign,))

        query = 'INSERT INTO campaigns VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?)';
        if total_campaigns == 0:
            run_query(query, (campaign, group, 0, 0, 0, 0, seconds, 0, 1,))
            cursorClose()

        id_campaign = None
        db_campaign = run_query('SELECT id FROM campaigns WHERE name=?', (campaign,))
        for row in db_campaign:
            id_campaign = int(row[0])
        cursorClose()

        accounts = []
        db_accounts = run_query('SELECT id FROM accounts WHERE status=1', ())
        for row in db_accounts:
            data = {
                'id' : row[0]
            }
            accounts.append(data)
        cursorClose()

        for row in accounts:
            check = run_query_count('SELECT id FROM campaigns_accounts WHERE campaign_id=? and account_id=?', (id_campaign, row['id']))
            if check == 0:
                query = 'INSERT INTO campaigns_accounts VALUES(NULL, ?, ?, ?, ?)';
                run_query(query, (id_campaign, row['id'],0,1,))
                cursorClose()

        query = 'UPDATE campaigns SET status=? where id=?'
        run_query(query, (0,id_campaign,))
        cursorClose()

        t = threading.Thread(target=_scrapper, args=(account,channel,id_campaign,photo,limit,username,))
        t.start()

        return jsonify({'status': 200, 'message': 'Scrapper started', 'payload': {}})
    except Exception as e:
        return jsonify({'status': 422, 'message': str(e), 'payload': {}})
    except :
        return jsonify({'status': 422, 'message': 'An error occurred', 'payload': {}})


def status(jsonify, request):
    print('status')
    global cursorScrapperGlobal
    try:
        cursorClose()

        try:
            id_campaign = int(request.json['id_campaign'])
        except:
            return jsonify({'status': 422, 'message': 'Pass the id campaign', 'payload': {}})

        campaign = None
        db_campaign = run_query('SELECT * FROM campaigns WHERE id=?', (id_campaign,))
        for row in db_campaign:
            campaign = row
        cursorClose()

        if campaign == None:
            return jsonify({'status': 422, 'message': 'The campaign does not exist', 'payload': {}})

        data = {
            'name': campaign[1],
            'group': campaign[2],
            'total_users': campaign[3],
            'completed_users': campaign[4],
            'failed_users': campaign[5],
            'last_used': campaign[6],
            'seconds': campaign[7],
            'pause': campaign[8],
            'status': campaign[9]
        }

        return jsonify({'status': 200, 'message': 'Status campaign', 'payload': data})

    except Exception as e:
        return jsonify({'status': 422, 'message': str(e), 'payload': {}})
    except :
        return jsonify({'status': 422, 'message': 'An error occurred', 'payload': {}})