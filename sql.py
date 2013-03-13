import sqlite3 as sql

conn = None 
dbName = 'design.sqlite3'

def initDB(language, topDir) :
  global db 
  conn = sql.connect(dbName)
  c = conn.cursor()
  # initialize 
  query = '''
    CREATE TABLE 
    info 
    ( language TEXT NOT NULL
    , start_time DATETIME
    , end_time DATETIME
    , top_dir TEXT NOT NULL
    , regex TEXT 
    , status TEXT
    , comment TEXT
    )'''
  c.execute(query)

  query = '''REPLACE INTO info
    (language, start_time, top_dir)
    VALUES 
    (?, 'now()', ?)'''
  c.execute(query, [language, topDir])
    
  query = '''
      CREATE TABLE
      heir
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

  query = '''
  CREATE TABLE 
  elements 
  ( name TEXT
  , type TEXT 
  , scope_name TEXT 
  , scope_type TEXT 
  , expression TEXT 
  , PRIMARY KEY(name, type)
  )'''
  c.execute(query)

  conn.commit()
