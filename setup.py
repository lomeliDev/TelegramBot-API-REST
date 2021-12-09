#!/bin/env python3

import os, sys, time, sqlite3

re = "\033[1;31m"
gr = "\033[1;32m"
cy = "\033[1;36m"

class Setup:

    db_name = 'db.db'

    def run_query(self, query, parameters=()):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            result = cursor.execute(query, parameters)
            conn.commit()
            try:
                cursor.close()
            except:
                pass
        return result

    def initDatabase(self):
        self.run_query('CREATE TABLE IF NOT EXISTS "proxies" ( "id" INTEGER NOT NULL UNIQUE, "ip" TEXT NOT NULL, "port" TEXT NOT NULL, "user" TEXT NOT NULL, "password" TEXT NOT NULL,"status"	INTEGER NOT NULL, PRIMARY KEY("id" AUTOINCREMENT));')
        self.run_query('CREATE TABLE IF NOT EXISTS "accounts" ("id"	INTEGER NOT NULL, "api_id"	TEXT NOT NULL UNIQUE, "api_hash"	TEXT NOT NULL UNIQUE, "phone"	TEXT NOT NULL UNIQUE, "alias"	TEXT NOT NULL UNIQUE,"status"	INTEGER NOT NULL, PRIMARY KEY("id" AUTOINCREMENT));')
        self.run_query('CREATE TABLE IF NOT EXISTS "campaigns" ("id" INTEGER NOT NULL UNIQUE, "name" TEXT NOT NULL, "total_users" INTEGER NOT NULL, "completed_users" INTEGER NOT NULL, "failed_users" INTEGER NOT NULL, "status" INTEGER NOT NULL,PRIMARY KEY("id" AUTOINCREMENT));')
        self.run_query('CREATE TABLE IF NOT EXISTS "users" ("id" INTEGER NOT NULL UNIQUE, "campaign_id"	INTEGER NOT NULL,"uuid"	TEXT ,"access_hash"	TEXT,"username"	TEXT , "name" TEXT, "status" INTEGER NOT NULL,PRIMARY KEY("id" AUTOINCREMENT));')

    def clear(self):
        os.system('clear')

    def logo(self):
        print(f"""
            {re}╔╦╗{cy}┌─┐┬  ┌─┐{re}╔═╗  ╔═╗{cy}┌─┐┬─┐┌─┐┌─┐┌─┐┬─┐
            {re} ║ {cy}├┤ │  ├┤ {re}║ ╦  ╚═╗{cy}│  ├┬┘├─┤├─┘├┤ ├┬┘
            {re} ╩ {cy}└─┘┴─┘└─┘{re}╚═╝  ╚═╝{cy}└─┘┴└─┴ ┴┴  └─┘┴└─
                        version : 1.0.0
                    youtube.com/lomelidev
                    autor : Miguel Lomeli
        """)

    def __init__(self):
        self.clear()
        self.logo()
        self.initDatabase()
        print(gr+'['+cy+'+'+gr+']'+cy+' the installation will take about 10 minutes to fully install.')
        input_csv = input(gr+'['+cy+'+'+gr+']'+cy+' are you sure to install the scraper? (y/n): ').lower()
        if input_csv == "y":
            print(gr+'['+cy+'+'+gr+']'+cy+' this may take some time ...')
            os.system("""
                python3 -m pip install cython numpy pandas
                python3 -m pip install telethon tulir-telethon requests configparser
                python3 -m pip install PyMySQL socks PySocks flask asyncio
                python3 -m pip install csv sqlite3 random
                """)    
            self.clear()
            self.logo()
            print(gr+"Installation finished ...")
            pass
        else:
            print(gr+"we wait for you soon ...")

Setup()
