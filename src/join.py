#!/bin/env python3

import os, sqlite3, sys, socks, threading, socket, requests, string, random, asyncio, datetime, time
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest, InviteToChannelRequest
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError
from telethon.errors.rpcerrorlist import BotsTooMuchError, BotGroupsBlockedError, ChannelInvalidError
from telethon.errors.rpcerrorlist import ChannelPrivateError, ChatAdminRequiredError, ChatInvalidError
from telethon.errors.rpcerrorlist import ChatWriteForbiddenError, InputUserDeactivatedError, UsersTooMuchError
from telethon.errors.rpcerrorlist import UserBannedInChannelError, UserBlockedError, UserBotError
from telethon.errors.rpcerrorlist import UserChannelsTooMuchError, UserIdInvalidError, UserKickedError
from telethon.errors.rpcerrorlist import ChatWriteForbiddenError, InputUserDeactivatedError, UsersTooMuchError, UserNotMutualContactError

cursorJoinGlobal = None
db_name = 'db.db'

def cursorClose():
    global cursorJoinGlobal
    try:
        cursorJoinGlobal.close()
        cursorJoinGlobal = None
    except:
        pass

def run_query(query, parameters = ()):
    global cursorJoinGlobal
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursorJoinGlobal = cursor
        result = cursor.execute(query, parameters)
        conn.commit()
    return result   

def run_query_count( query, parameters = ()):
    global cursorJoinGlobal
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursorJoinGlobal = cursor
        result = cursor.execute(query, parameters)
        rows = cursor.fetchall()
        result = len (rows)
        conn.commit()
        try:
            cursor.close()
        except:
            pass
    return result

def join(jsonify, request):
    print('join')
    global cursorJoinGlobal
    try:
        cursorClose()

        try:
            id = int(request.json['id'])
        except:
            return jsonify({'status': 422, 'message': 'Send all parameters', 'payload': {}})

        check_proxy = run_query_count('SELECT * FROM campaigns where id=?', (id,))

        if check_proxy == 0:
            return jsonify({'status': 422, 'message': 'The campaign does not exist', 'payload': {}})

        db_campaigns = run_query('SELECT * FROM campaigns', ())
        campaigns = None
        for row in db_campaigns:
            campaigns = {
                'id': row[0],
                'name': row[1],
                'group': row[2],
                'total_users': row[3],
                'completed_users': row[4],
                'failed_users': row[5],
                'last_used': row[6],
                'seconds': row[7],
                'pause': row[8],
                'status': row[9]
            }
        cursorClose()

        if int(campaigns["status"]) != 1:
            return jsonify({'status': 422, 'message': 'The campaign is inactive', 'payload': {}})

        if int(campaigns["pause"]) != 1:
            return jsonify({'status': 422, 'message': 'The campaign is on pause', 'payload': {}})
        
        if int(campaigns["total_users"]) <= (int(campaigns["completed_users"]) + int(campaigns["failed_users"])):
            return jsonify({'status': 422, 'message': 'The campaign is over', 'payload': {}})

        currentTime = int(datetime.datetime.now().timestamp() * 1000)
        lastTime = int(campaigns["last_used"])
        seconds = int(campaigns["seconds"]) * 1000
    
        if lastTime >= currentTime:
            return jsonify({'status': 422, 'message': 'The last round is higher than the current date', 'payload': {}})

        if (currentTime - lastTime) <= seconds:
            return jsonify({'status': 422, 'message': 'The campaign time is not yet fulfilled', 'payload': {}})

        query = 'UPDATE campaigns SET "last_used"=? where id=?'
        run_query(query, (currentTime,id,))
        cursorClose()

        SQL = """
            SELECT
                accounts.*, 
                campaigns."group"
            FROM
                campaigns_accounts
                INNER JOIN
                accounts
                ON 
                    campaigns_accounts.account_id = accounts.id
                INNER JOIN
                campaigns
                ON 
                    campaigns_accounts.campaign_id = campaigns.id
            WHERE
                campaigns_accounts.campaign_id = ?
                AND campaigns_accounts."join" = 1
                AND campaigns_accounts.status = 1
        """
        #AND accounts.id = 5

        db_accounts = run_query(SQL, (id,))
        accounts = []
        for row in db_accounts:
            accounts.append(row)
        cursorClose()

        if len(accounts) == 0:
            return jsonify({'status': 422, 'message': 'You do not have active accounts', 'payload': {}})

        for row in accounts:
            t = threading.Thread(target=_join, args=(id,row,))
            t.start()

        return jsonify({'status': 200, 'message': 'OK', 'payload': {}})
    except Exception as e:
        return jsonify({'status': 422, 'message': str(e), 'payload': {}})
    except :
        return jsonify({'status': 422, 'message': 'An error occurred', 'payload': {}})

def _statusJoin(id, status, message, check, campaign_id):
    global cursorJoinGlobal
    
    if message != "":
        print(message)

    cursorClose()
    if check:
        query = 'UPDATE users SET "status"=? , "message"=? where id=?'
        run_query(query, (status,message,id,))
        cursorClose()

    db_proxie = run_query('SELECT completed_users, failed_users FROM campaigns WHERE id=?', (campaign_id,))
    completed_users = 0
    failed_users = 0
    for row in db_proxie:
        completed_users = int(row[0])
        failed_users = int(row[1])
    cursorClose()

    if check:
        if status == 1:
            completed_users = completed_users + 1
            query = 'UPDATE campaigns SET "completed_users"=? where id=?'
            run_query(query, (completed_users,campaign_id,))
            cursorClose()
        else:
            failed_users = failed_users + 1
            query = 'UPDATE campaigns SET "failed_users"=? where id=?'
            run_query(query, (failed_users,campaign_id,))
            cursorClose()

def _account(id, campaign_id, status, error, check):
    cursorClose()

    if check:
        query = 'UPDATE campaigns_accounts SET "status"=? where account_id=?'
        run_query(query, (status,id,))
        cursorClose()
        query = 'UPDATE accounts SET "status"=? where id=?'
        run_query(query, (status,id,))
        cursorClose()

    currentTime = int(datetime.datetime.now().timestamp() * 1000)
    query = 'INSERT INTO accounts_errors VALUES(NULL, ?, ?, ?)';
    run_query(query, (id,error,currentTime,))
    cursorClose()

def _join(id, data):
    try:
        global cursorJoinGlobal
        time.sleep(random.randrange(1, 5))
        currentTime = int(datetime.datetime.now().timestamp() * 1000)

        cursorClose()

        query = 'UPDATE campaigns_accounts SET "last_used"=? where account_id=?'
        run_query(query, (currentTime,int(data[0]),))
        cursorClose()

        db_proxie = run_query('SELECT * FROM proxies WHERE status=1 ORDER BY RANDOM() LIMIT 1', ())
        proxie = ['', '', '', '']
        for row in db_proxie:
            proxie[0] = str(row[1])
            proxie[1] = str(row[2])
            proxie[2] = str(row[3])
            proxie[3] = str(row[4])
        cursorClose()

        SQL = """
            SELECT
                users.id, 
                users.uuid, 
                users.access_hash, 
                users.username, 
                users.status
            FROM
                users
            WHERE
                users.campaign_id = ?
                AND users.status = 0
                AND users.username != ''
            ORDER BY
                RANDOM()
            LIMIT 1
        """

        db_user = run_query(SQL, (id,))
        user = None
        for row in db_user:
            user = row
        cursorClose()

        if user == None:
            return

        query = 'UPDATE users SET "last_used"=? where id=?'
        run_query(query, (currentTime,int(user[0]),))
        cursorClose()

        client = None

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            client = TelegramClient("sessions/" + str(data[3]), str(data[1]), str(data[2]), proxy=("socks5", str(proxie[0]), int(proxie[1]), True, proxie[2], proxie[3]), loop=loop)
        except Exception as e:
            return
        except:
            return

        client.connect()
        if not client.is_user_authorized():
            return

        cursorClose()

        try:
            user_to_add = client.get_input_entity(user[3])
            client(InviteToChannelRequest(str(data[6]), [user_to_add]))
            _statusJoin(int(user[0]), 1, "", True, id)
        except PeerFloodError:
            _statusJoin(int(user[0]), 2, "PeerFloodError", False, id)
            _account(int(data[0]), id, 3, "PeerFloodError", False)
        except UserPrivacyRestrictedError:
            _statusJoin(int(user[0]), 2, "UserPrivacyRestrictedError", False, id)
        except BotsTooMuchError:
            _statusJoin(int(user[0]), 2, "BotsTooMuchError", False, id)
        except BotGroupsBlockedError:
            _statusJoin(int(user[0]), 2, "BotGroupsBlockedError", False, id)
        except ChannelInvalidError:
            _statusJoin(int(user[0]), 2, "ChannelInvalidError", False, id)
        except ChannelPrivateError:
            _statusJoin(int(user[0]), 2, "ChannelPrivateError", False, id)
            _account(int(data[0]), id, 3, "ChannelPrivateError", False)
        except ChatAdminRequiredError:
            _statusJoin(int(user[0]), 2, "ChatAdminRequiredError", False, id)
            _account(int(data[0]), id, 3, "ChatAdminRequiredError", False)
        except ChatInvalidError:
            _statusJoin(int(user[0]), 2, "ChatInvalidError", False, id)
        except ChatWriteForbiddenError:
            _statusJoin(int(user[0]), 2, "ChatWriteForbiddenError", False, id)
            _account(int(data[0]), id, 3, "ChatWriteForbiddenError", False)
        except InputUserDeactivatedError:
            _statusJoin(int(user[0]), 2, "InputUserDeactivatedError", True, id)
        except UsersTooMuchError:
            _statusJoin(int(user[0]), 2, "UsersTooMuchError", False, id)
        except UserBannedInChannelError:
            _statusJoin(int(user[0]), 2, "UserBannedInChannelError", False, id)
            _account(int(data[0]), id, 3, "UserBannedInChannelError", True)
        except UserBlockedError:
            _statusJoin(int(user[0]), 2, "UserBlockedError", True, id)
        except UserBotError:
            _statusJoin(int(user[0]), 2, "UserBotError", False, id)
        except UserChannelsTooMuchError:
            _statusJoin(int(user[0]), 2, "UserChannelsTooMuchError", True, id)
        except UserIdInvalidError:
            _statusJoin(int(user[0]), 2, "UserIdInvalidError", True, id)
        except UserKickedError:
            _statusJoin(int(user[0]), 2, "UserKickedError", True, id)
        except UserNotMutualContactError:
            _statusJoin(int(user[0]), 2, "UserNotMutualContactError", True, id)
        except UserPrivacyRestrictedError:
            _statusJoin(int(user[0]), 2, "UserPrivacyRestrictedError", False, id)
        except Exception as e:
            print(e)
            _statusJoin(int(user[0]), 2, "Error", False, id)
        except:
            _statusJoin(int(user[0]), 2, "Error", False, id)

        client.disconnect()

    except Exception as e:
        print(e)
        pass
    except :
        pass