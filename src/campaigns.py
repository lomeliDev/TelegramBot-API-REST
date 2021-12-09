#!/bin/env python3

import os, sqlite3, sys, socks, threading, socket, requests, string, random

cursorCampaignsGlobal = None
db_name = 'db.db'

def cursorClose():
    global cursorCampaignsGlobal
    try:
        cursorCampaignsGlobal.close()
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
                campaigns_accounts.status
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
                'status': row[5]
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
