#!/bin/env python3

import os, sqlite3, sys, socks, threading, socket, requests, string, random, asyncio
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest

cursorCampaignsGlobal = None
db_name = 'db.db'

def cursorClose():
    global cursorCampaignsGlobal
    try:
        cursorCampaignsGlobal.close()
        cursorCampaignsGlobal = None
    except:
        pass

def run_query(query, parameters = ()):
    global cursorCampaignsGlobal
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursorCampaignsGlobal = cursor
        result = cursor.execute(query, parameters)
        conn.commit()
    return result   

def run_query_count( query, parameters = ()):
    global cursorCampaignsGlobal
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursorCampaignsGlobal = cursor
        result = cursor.execute(query, parameters)
        rows = cursor.fetchall()
        result = len (rows)
        conn.commit()
        try:
            cursor.close()
        except:
            pass
    return result

def all(jsonify, request):
    print('all')
    global cursorCampaignsGlobal
    try:
        cursorClose()

        db_campaigns = run_query('SELECT * FROM campaigns', ())
        campaigns = []
        for row in db_campaigns:
            data = {
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
            campaigns.append(data)
        cursorClose()

        return jsonify({'status': 200, 'message': 'Campaigns Data', 'payload': campaigns})
    except Exception as e:
        return jsonify({'status': 422, 'message': str(e), 'payload': {}})
    except :
        return jsonify({'status': 422, 'message': 'An error occurred', 'payload': {}})

def accounts(jsonify, request):
    print('accounts')
    global cursorCampaignsGlobal
    try:
        cursorClose()

        try:
            id = int(request.json['id'])
        except:
            return jsonify({'status': 422, 'message': 'Send all parameters', 'payload': {}})

        SQL = """
            SELECT
                campaigns_accounts.id, 
                campaigns_accounts.account_id, 
                campaigns_accounts.last_used, 
                accounts.phone, 
                accounts.alias,
                campaigns_accounts.status,
                campaigns_accounts."join"
            FROM
                campaigns_accounts
                INNER JOIN
                accounts
                ON 
                    campaigns_accounts.account_id = accounts.id
            WHERE
                campaigns_accounts.campaign_id = ?
        """
        db_campaigns = run_query(SQL, (id,))
        campaigns = []
        for row in db_campaigns:
            data = {
                'id': row[0],
                'account_id': row[1],
                'last_used': row[2],
                'phone': row[3],
                'alias': row[4],
                'status': row[5],
                'join': row[6]
            }
            campaigns.append(data)
        cursorClose()

        return jsonify({'status': 200, 'message': 'Campaigns Accounts Data', 'payload': campaigns})
    except Exception as e:
        return jsonify({'status': 422, 'message': str(e), 'payload': {}})
    except :
        return jsonify({'status': 422, 'message': 'An error occurred', 'payload': {}})

def users(jsonify, request):
    print('users')
    global cursorCampaignsGlobal
    try:
        cursorClose()

        try:
            id = int(request.json['id'])
        except:
            return jsonify({'status': 422, 'message': 'Send all parameters', 'payload': {}})

        SQL = """
            SELECT
                users.id, 
                users.account_id, 
                users.uuid, 
                users.access_hash, 
                users.username, 
                users.name, 
                users.phone, 
                users.message, 
                users.last_used, 
                users.status, 
                accounts.alias, 
                accounts.phone AS account_phone
            FROM
                users
                LEFT JOIN accounts
                ON users.account_id = accounts.id
            WHERE
                users.campaign_id = ?
        """
        db_campaigns = run_query(SQL, (id,))
        campaigns = []
        for row in db_campaigns:
            data = {
                'id': row[0],
                'account_id': row[1],
                'uuid': row[2],
                'access_hash': row[3],
                'username': row[4],
                'name': row[5],
                'phone': row[6],
                'message': row[7],
                'last_used': row[8],
                'status': row[9],
                'alias': row[10],
                'account_phone': row[11]
            }
            campaigns.append(data)
        cursorClose()

        return jsonify({'status': 200, 'message': 'Campaigns Users Data', 'payload': campaigns})
    except Exception as e:
        return jsonify({'status': 422, 'message': str(e), 'payload': {}})
    except :
        return jsonify({'status': 422, 'message': 'An error occurred', 'payload': {}})

def delete(jsonify, request):
    print('delete')
    global cursorCampaignsGlobal
    try:
        cursorClose()

        try:
            id = int(request.json['id'])
        except:
            return jsonify({'status': 422, 'message': 'Send all parameters', 'payload': {}})

        check_proxy = run_query_count('SELECT * FROM campaigns where id=?', (id,))

        if check_proxy == 0:
            return jsonify({'status': 422, 'message': 'The campaign does not exist', 'payload': {}})

        run_query('DELETE FROM campaigns WHERE id = ?', (id,))
        run_query('DELETE FROM campaigns_accounts WHERE campaign_id = ?', (id,))
        run_query('DELETE FROM users WHERE campaign_id = ?', (id,))
        cursorClose()

        return jsonify({'status': 200, 'message': 'The campaign was successfully removed', 'payload': {}})
    except Exception as e:
        return jsonify({'status': 422, 'message': str(e), 'payload': {}})
    except :
        return jsonify({'status': 422, 'message': 'An error occurred', 'payload': {}})

def pause(jsonify, request):
    print('pause')
    global cursorCampaignsGlobal
    try:
        cursorClose()

        try:
            pause = int(request.json['pause'])
            id = int(request.json['id'])

            if pause != 0 and pause != 1:
                return jsonify({'status': 422, 'message': 'enter a valid value for the pause', 'payload': {}})    
        except:
            return jsonify({'status': 422, 'message': 'Send all parameters', 'payload': {}})

        check_proxy = run_query_count('SELECT * FROM campaigns where id=?', (id,))

        if check_proxy == 0:
            return jsonify({'status': 422, 'message': 'The campaign does not exist', 'payload': {}})

        run_query('UPDATE campaigns SET pause=? where id=?', (pause,id,))
        cursorClose()

        return jsonify({'status': 200, 'message': 'The campaign status was updated', 'payload': {}})
    except Exception as e:
        return jsonify({'status': 422, 'message': str(e), 'payload': {}})
    except :
        return jsonify({'status': 422, 'message': 'An error occurred', 'payload': {}})

def export(jsonify, request, make_response, id):
    print('export')
    global cursorCampaignsGlobal
    try:
        cursorClose()

        check_proxy = run_query_count('SELECT * FROM campaigns where id=?', (id,))

        if check_proxy == 0:
            return jsonify({'status': 422, 'message': 'The campaign does not exist', 'payload': {}})

        SQL = """
            SELECT
                users.id, 
                users.account_id, 
                users.uuid, 
                users.access_hash, 
                users.username, 
                users.name, 
                users.phone, 
                users.message, 
                users.last_used, 
                users.status, 
                accounts.alias, 
                accounts.phone AS account_phone
            FROM
                users
                LEFT JOIN accounts
                ON users.account_id = accounts.id
            WHERE
                users.campaign_id = ?
        """
        db_campaigns = run_query(SQL, (id,))
        dataExport = "campaign_id;account_id;uuid;access_hash;username;name;phone;message;last_used;status;alias;account_phone\n"
        for row in db_campaigns:
            dataExport = dataExport + str(id) + ";"
            dataExport = dataExport + str(row[1]) + ";"
            dataExport = dataExport + str(row[2]) + ";"
            dataExport = dataExport + str(row[3]) + ";"
            dataExport = dataExport + str(row[4]) + ";"
            dataExport = dataExport + str(row[5]) + ";"
            dataExport = dataExport + str(row[6]) + ";"
            dataExport = dataExport + str(row[7]) + ";"
            dataExport = dataExport + str(row[8]) + ";"
            dataExport = dataExport + str(row[9]) + ";"
            dataExport = dataExport + str(row[10]) + ";"
            dataExport = dataExport + str(row[11]) + "\n"
        cursorClose()

        output = make_response(dataExport)
        output.headers["Content-Disposition"] = "attachment; filename=export_campaign_.csv"
        output.headers["Content-type"] = "text/csv"
        return output

    except Exception as e:
        return jsonify({'status': 422, 'message': str(e), 'payload': {}})
    except :
        return jsonify({'status': 422, 'message': 'An error occurred', 'payload': {}})

def importCampaigns(jsonify, request):
    print('importCampaigns')
    global cursorCampaignsGlobal
    try:
        cursorClose()

        letters = string.ascii_lowercase
        nameFile = ''.join(random.choice(letters) for i in range(64)) + ".csv"

        delimiter = ";"

        try:
            id = int(request.values.get('id'))
            uploaded_file = request.files['file']
        except:
            return jsonify({'status': 422, 'message': 'Send all parameters', 'payload': {}})

        check_proxy = run_query_count('SELECT * FROM campaigns where id=?', (id,))

        if check_proxy == 0:
            return jsonify({'status': 422, 'message': 'The campaign does not exist', 'payload': {}})

        if uploaded_file.filename != '':
            uploaded_file.save("./tmp/" + nameFile)

            file1 = open("./tmp/" + nameFile, 'r')
            Lines = file1.readlines()
            file1.close()

            if os.path.exists("./tmp/" + nameFile):
                os.remove("./tmp/" + nameFile)

            x = 0
            for line in Lines:
                x = x + 1
                if x == 1:
                    continue

                line = line.replace("\n", "")
                line = line.split(delimiter)

                search_id = run_query_count('SELECT id FROM users WHERE campaign_id=? AND uuid=?', (id, str(line[2])))

                if search_id == 0:
                    query = 'INSERT INTO users VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)';
                    run_query(query, (id, 0, line[2], line[3], line[4], line[5], line[6], "", 1, 0,))
                    cursorClose()

            return jsonify({'status': 200, 'message': 'The accounts were imported', 'payload': {}})
        else:
            return jsonify({'status': 422, 'message': 'error, upload csv file', 'payload': {}})        
        
    except Exception as e:
        return jsonify({'status': 422, 'message': str(e), 'payload': {}})
    except :
        return jsonify({'status': 422, 'message': 'An error occurred', 'payload': {}})       

def _statusJoined(id, status):
    global cursorCampaignsGlobal
    cursorClose()
    query = 'UPDATE campaigns_accounts SET "join"=? where id=?'
    run_query(query, (status,id,))
    cursorClose()

def _joined(id, data):
    try:
        global cursorCampaignsGlobal

        cursorClose()
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
            _statusJoined(int(data[6]), 2)
            return
        except:
            _statusJoined(int(data[6]), 2)
            return

        client.connect()
        query = 'UPDATE campaigns_accounts SET "join"=? where id=?'
        if not client.is_user_authorized():
            run_query(query, (2,int(data[6]),))
            cursorClose()
            return

        try:
            client(JoinChannelRequest(str(data[7])))
            _statusJoined(int(data[6]), 1)
        except Exception as e:
            _statusJoined(int(data[6]), 2)
        except:
            _statusJoined(int(data[6]), 2)

        cursorClose()
        client.disconnect()

    except Exception as e:
        _statusJoined(int(data[6]), 2)
    except:
        _statusJoined(int(data[6]), 2)

def joined(jsonify, request):
    print('joined')
    global cursorCampaignsGlobal
    try:
        cursorClose()

        try:
            id = int(request.json['id'])
        except:
            return jsonify({'status': 422, 'message': 'Send all parameters', 'payload': {}})

        check_proxy = run_query_count('SELECT * FROM campaigns where id=?', (id,))

        if check_proxy == 0:
            return jsonify({'status': 422, 'message': 'The campaign does not exist', 'payload': {}})

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

        SQL = """
            SELECT
                accounts.*, 
                campaigns_accounts.id as account_id, 
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
                AND campaigns_accounts."join" = 0
                AND campaigns_accounts.status = 1
        """

        db_accounts = run_query(SQL, (id,))
        accounts = []
        for row in db_accounts:
            accounts.append(row)
        cursorClose()
        
        for row in accounts:
            t = threading.Thread(target=_joined, args=(id,row,))
            t.start()
        
        return jsonify({'status': 200, 'message': 'Accounts are joining the campaign group', 'payload': {}})
    except Exception as e:
        return jsonify({'status': 422, 'message': str(e), 'payload': {}})
    except :
        return jsonify({'status': 422, 'message': 'An error occurred while parsing the accounts', 'payload': {}})