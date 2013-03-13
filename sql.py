import sqlite3 as sql

conn = None 
dbName = 'design.sqlite3'

def initDB(language, topDir) :
  global dbName
  global conn
  conn = sql.connect(dbName)
  c = conn.cursor()
  # initialize 
  query = '''DROP TABLE IF EXISTS files'''
  c.execute(query)
  query = '''
    CREATE TABLE 
    files
    ( language TEXT 
    , name TEXT NOT NULL
    , path TEXT NOT NULL
    , name_regex TEXT 
    , top_dir TEXT 
    , status TEXT
    , comment TEXT
    )'''
  c.execute(query)
    
  query = '''DROP TABLE IF EXISTS hier'''
  c.execute(query)
  query = '''
    CREATE TABLE
    hier
    ( unit_name TEXT
    , unit_type TEXT 
    , instance_of TEXT 
    , file_name TEXT NOT NULL
    , file_path TEXT NOT NULL
    , comment TEXT 
    , PRIMARY KEY(unit_name, unit_type, file_path, file_name)
    ) 
    '''
  c.execute(query)

  query = '''DROP TABLE IF EXISTS elements'''
  c.execute(query)
  query = '''
    CREATE TABLE 
    elements 
    ( name TEXT
    , type TEXT 
    , scope_name TEXT 
    , scope_type TEXT 
    , expression TEXT 
    , PRIMARY KEY(name, type)
    ) 
    '''
  c.execute(query)
  conn.commit()

def closeDB() :
  global conn
  conn.close()
