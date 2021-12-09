#!/bin/env python3

import os, sqlite3, sys, socks, threading, socket, requests, string, random

cursorProxisGlobal = None
db_name = 'db.db'

def cursorClose():
    global cursorProxisGlobal
    try:
        cursorProxisGlobal.close()
    except:
        pass

def run_query(query, parameters = ()):
    global cursorProxisGlobal
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursorProxisGlobal = cursor
        result = cursor.execute(query, parameters)
        conn.commit()
    return result   

def run_query_count( query, parameters = ()):
    global cursorProxisGlobal
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursorProxisGlobal = cursor
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
    global cursorProxisGlobal
    try:
        db_proxies = run_query('SELECT * FROM proxies', ())
        proxies = []
        for row in db_proxies:
            data = {
                'id': row[0],
                'ip': row[1],
                'port': row[2],
                'username': row[3],
                'password': row[4],
                'status': row[5]
            }
            proxies.append(data)
        cursorClose()

        return jsonify({'status': 200, 'message': 'Proxis Data', 'payload': proxies})
    except Exception as e:
        return jsonify({'status': 422, 'message': str(e), 'payload': {}})
    except :
        return jsonify({'status': 422, 'message': 'An error occurred', 'payload': {}})

def add(jsonify, request):
    print('add')
    global cursorProxisGlobal
    try:
        cursorClose()

        try:
            ip = request.json['ip']
            port = int(request.json['port'])
            user = request.json['user']
            password = request.json['password']
        except:
            return jsonify({'status': 422, 'message': 'Send all parameters', 'payload': {}})

        check_proxy = run_query_count('SELECT * FROM proxies where ip=?', (ip,))

        if check_proxy > 0:
            return jsonify({'status': 422, 'message': 'The proxy already exists', 'payload': {}})  

        try:
            socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, ip, port, False, user, password)
            socket.socket = socks.socksocket
            url = u'https://ipapi.co/8.8.8.8/csv/'
            codeProxi = int(requests.get(url).status_code)

            if codeProxi != 200 and codeProxi != 429:
                return jsonify({'status': 422, 'message': 'The proxy is wrong', 'payload': {}})

        except Exception as e:
            return jsonify({'status': 422, 'message': str(e), 'payload': {}})
        except :
            return jsonify({'status': 422, 'message': 'An error occurred', 'payload': {}})

        query = 'INSERT INTO proxies VALUES(NULL, ?, ?, ?, ?, ?)';
        run_query(query, (ip, port, user, password, 1,))
        cursorClose()

        return jsonify({'status': 200, 'message': 'Proxi saved successfully', 'payload': {}})
    except Exception as e:
        return jsonify({'status': 422, 'message': str(e), 'payload': {}})
    except :
        return jsonify({'status': 422, 'message': 'An error occurred', 'payload': {}})


def delete(jsonify, request):
    print('delete')
    global cursorProxisGlobal
    try:
        cursorClose()

        try:
            id = int(request.json['id'])
        except:
            return jsonify({'status': 422, 'message': 'Send all parameters', 'payload': {}})

        check_proxy = run_query_count('SELECT * FROM proxies where id=?', (id,))

        if check_proxy == 0:
            return jsonify({'status': 422, 'message': 'The proxy does not exist', 'payload': {}})

        run_query('DELETE FROM proxies WHERE id = ?', (id,))
        cursorClose()

        return jsonify({'status': 200, 'message': 'The proxy was successfully removed', 'payload': {}})
    except Exception as e:
        return jsonify({'status': 422, 'message': str(e), 'payload': {}})
    except :
        return jsonify({'status': 422, 'message': 'An error occurred', 'payload': {}})            

def _test(data):
    query = 'UPDATE proxies SET status=? where id=?'
    try:
        cursorClose()
        run_query(query, (0,data['id'],))
        cursorClose()

        try:
            socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, data['ip'], int(data['port']), False, data['username'], data['password'])
            socket.socket = socks.socksocket
            url = u'https://ipapi.co/8.8.8.8/csv/'
            codeProxi = int(requests.get(url).status_code)

            if codeProxi != 200 and codeProxi != 429:
                run_query(query, (2,data['id'],))
                cursorClose()
                return

            run_query(query, (1,data['id'],))
            cursorClose()

        except :
            run_query(query, (2,data['id'],))
            cursorClose()

    except :
        run_query(query, (2,data['id'],))
        cursorClose()  

def test(jsonify, request):
    print('test')
    global cursorProxisGlobal
    try:
        cursorClose()

        db_proxies = run_query('SELECT * FROM proxies', ())
        proxies = []
        for row in db_proxies:
            data = {
                'id': row[0],
                'ip': row[1],
                'port': row[2],
                'username': row[3],
                'password': row[4],
                'status': row[5]
            }
            proxies.append(data)
        cursorClose()

        for row in proxies:
            t = threading.Thread(target=_test, args=(row,))
            t.start()

        return jsonify({'status': 200, 'message': 'Proxies are being checked', 'payload': {}})
    except Exception as e:
        return jsonify({'status': 422, 'message': str(e), 'payload': {}})
    except :
        return jsonify({'status': 422, 'message': 'An error occurred', 'payload': {}})

def _import(row):
    try:
        cursorClose()

        check_proxy = run_query_count('SELECT * FROM proxies where ip=?', (row['ip'],))

        if check_proxy > 0:
            return

        try:
            socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, row['ip'], int(row['port']), False, row['username'], row['password'])
            socket.socket = socks.socksocket
            url = u'https://ipapi.co/8.8.8.8/csv/'
            codeProxi = int(requests.get(url).status_code)
            if codeProxi == 200 or codeProxi == 429:
                query = 'INSERT INTO proxies VALUES(NULL, ?, ?, ?, ?, ?)';
                run_query(query, (row['ip'], row['port'], row['username'], row['password'], 1,))
                cursorClose()
        except :
            return
    except :
        pass

def importProxis(jsonify, request):
    print('importProxis')
    global cursorProxisGlobal
    try:

        letters = string.ascii_lowercase
        nameFile = ''.join(random.choice(letters) for i in range(64)) + ".csv"

        try:
            delimiter = request.values.get('delimiter')
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

            proxis = []
            for line in Lines:
                line = line.replace("\n", "")
                line = line.split(delimiter)
                data = {
                    'ip': line[0],
                    'port': int(line[1]),
                    'username': line[2],
                    'password': line[3]
                }
                proxis.append(data)
            
            for proxi in proxis:
                t = threading.Thread(target=_import, args=(proxi,))
                t.start()

            return jsonify({'status': 200, 'message': 'The proxies are being imported, wait a moment when they are validated', 'payload': {}})
        else:
            return jsonify({'status': 422, 'message': 'error, upload csv file', 'payload': {}})        
        
    except Exception as e:
        return jsonify({'status': 422, 'message': str(e), 'payload': {}})
    except :
        return jsonify({'status': 422, 'message': 'An error occurred', 'payload': {}})        