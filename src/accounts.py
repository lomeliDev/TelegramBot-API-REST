#!/bin/env python3

import os, sqlite3, sys, socks, threading, socket, requests, string, random

cursorAccountsGlobal = None
db_name = 'db.db'

def cursorClose():
    global cursorAccountsGlobal
    try:
        cursorAccountsGlobal.close()
    except:
        pass

def run_query(query, parameters = ()):
    global cursorAccountsGlobal
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursorAccountsGlobal = cursor
        result = cursor.execute(query, parameters)
        conn.commit()
    return result   

def run_query_count( query, parameters = ()):
    global cursorAccountsGlobal
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursorAccountsGlobal = cursor
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
    global cursorAccountsGlobal
    try:
        db_accounts = run_query('SELECT * FROM accounts', ())
        accounts = []
        for row in db_accounts:
            data = {
                'id': row[0],
                'api_id': row[1],
                'api_hash': row[2],
                'phone': row[3],
                'alias': row[4],
                'status': row[5]
            }
            accounts.append(data)
        cursorClose()

        return jsonify({'status': 200, 'message': 'Accounts Data', 'payload': accounts})
    except Exception as e:
        return jsonify({'status': 422, 'message': str(e), 'payload': {}})
    except :
        return jsonify({'status': 422, 'message': 'An error occurred', 'payload': {}})

def delete(jsonify, request):
    print('delete')
    global cursorAccountsGlobal
    try:
        cursorClose()

        try:
            id = int(request.json['id'])
        except:
            return jsonify({'status': 422, 'message': 'Send all parameters', 'payload': {}})

        check_account = run_query_count('SELECT * FROM accounts where id=?', (id,))

        if check_account == 0:
            return jsonify({'status': 422, 'message': 'The account does not exist', 'payload': {}})

        run_query('DELETE FROM accounts WHERE id = ?', (id,))
        cursorClose()

        return jsonify({'status': 200, 'message': 'The account was successfully removed', 'payload': {}})
    except Exception as e:
        return jsonify({'status': 422, 'message': str(e), 'payload': {}})
    except :
        return jsonify({'status': 422, 'message': 'An error occurred', 'payload': {}})            
