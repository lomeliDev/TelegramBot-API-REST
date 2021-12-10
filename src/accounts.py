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

def export(jsonify, request, make_response):
    print('export')
    global cursorAccountsGlobal
    try:
        cursorClose()

        SQL = """
            SELECT
                api_id,
                api_hash,
                phone,
                alias
            FROM
                accounts
        """
        db_campaigns = run_query(SQL, ())
        dataExport = "api_id;api_hash;phone;alias\n"
        for row in db_campaigns:
            dataExport = dataExport + str(row[0]) + ";"
            dataExport = dataExport + str(row[1]) + ";"
            dataExport = dataExport + str(row[2]) + ";"
            dataExport = dataExport + str(row[3]) + "\n"
        cursorClose()

        output = make_response(dataExport)
        output.headers["Content-Disposition"] = "attachment; filename=export_accounts_.csv"
        output.headers["Content-type"] = "text/csv"
        return output

    except Exception as e:
        return jsonify({'status': 422, 'message': str(e), 'payload': {}})
    except :
        return jsonify({'status': 422, 'message': 'An error occurred', 'payload': {}})

def importAccounts(jsonify, request):
    print('importAccounts')
    global cursorAccountsGlobal
    try:
        cursorClose()

        letters = string.ascii_lowercase
        nameFile = ''.join(random.choice(letters) for i in range(64)) + ".csv"

        delimiter = ";"

        try:
            uploaded_file = request.files['file']
        except:
            return jsonify({'status': 422, 'message': 'Send all parameters', 'payload': {}})

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

                search_id = run_query_count('SELECT id FROM accounts WHERE phone=?', (str(line[2]),))

                if search_id == 0:
                    query = 'INSERT INTO accounts VALUES(NULL, ?, ?, ?, ?, ?)';
                    run_query(query, (line[0], line[1], line[2], line[3], 1,))
                    cursorClose()

            return jsonify({'status': 200, 'message': 'The accounts were imported', 'payload': {}})
        else:
            return jsonify({'status': 422, 'message': 'error, upload csv file', 'payload': {}})        
        
    except Exception as e:
        return jsonify({'status': 422, 'message': str(e), 'payload': {}})
    except :
        return jsonify({'status': 422, 'message': 'An error occurred', 'payload': {}})   


def errors(jsonify, request):
    print('errors')
    global cursorAccountsGlobal
    try:
        cursorClose()

        db_campaigns = run_query('SELECT * FROM accounts_errors', ())
        accounts = []
        for row in db_campaigns:
            data = {
                'account_id': row[1],
                'error': row[2],
                'last_used': row[3]
            }
            accounts.append(data)
        cursorClose()

        return jsonify({'status': 200, 'message': 'Account errors', 'payload': accounts})

    except Exception as e:
        return jsonify({'status': 422, 'message': str(e), 'payload': {}})
    except :
        return jsonify({'status': 422, 'message': 'An error occurred', 'payload': {}})


def deleteErrors(jsonify, request):
    print('deleteErrors')
    global cursorAccountsGlobal
    try:
        cursorClose()

        db_accounts = run_query('SELECT id FROM accounts WHERE status=3', ())
        accounts = []
        for row in db_accounts:
            data = {
                'id': row[0]
            }
            accounts.append(data)
        cursorClose()

        for row in accounts:
            run_query('DELETE FROM accounts WHERE id = ?', (row['id'],))
            cursorClose()
            run_query('DELETE FROM accounts_errors WHERE account_id = ?', (row['id'],))
            cursorClose()
            run_query('DELETE FROM campaigns_accounts WHERE account_id = ?', (row['id'],))
            cursorClose()

        cursorClose()

        return jsonify({'status': 200, 'message': 'Accounts Data', 'payload': {}})
    except Exception as e:
        return jsonify({'status': 422, 'message': str(e), 'payload': {}})
    except :
        return jsonify({'status': 422, 'message': 'An error occurred', 'payload': {}})