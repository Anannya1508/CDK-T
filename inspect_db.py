import sqlite3, os
path=r'c:\\CDK-T\\app\\instance\\ckd_users.db'
print('exists',os.path.exists(path), 'path', path)
try:
    conn=sqlite3.connect(path)
    cur=conn.cursor()
    cur.execute('PRAGMA table_info(prediction_history)')
    cols=cur.fetchall()
    print('cols', cols)
    conn.close()
except Exception as e:
    print('error', e)
