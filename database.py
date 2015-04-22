import os
import MySQLdb

def get_conn(conn_file=None, verbosity=0):
    """Get a connection to Stash DB.

    This function gets a connection object to a Stash DB. The DB information needs to be in a file in the
    users home directory. The information should be contained on separate lines in the following order:

        host
        username
        password

    Args:
        conn_file: A file containing the connection information for a Stash DB. Default is .stash_db.conn
        verbosity: Set the verbosity of the function.

    Returns:
        A MySQLdb connection object.
    """
    # Python 2.6 has issues with a .my.cnf file, so we have to go a different route.
    if conn_file is None:
        conn_file = os.path.join(os.getenv("HOME"), ".stash_db.conn")

    if verbosity > 0:
        print "Conn file:", conn_file

    with open(conn_file, 'r') as fd:
        host = fd.readline().strip()
        username = fd.readline().strip()
        password = fd.readline().strip()

    return MySQLdb.connect(host=host, user=username, passwd=password, db="stash")

def get_db_data(cursor, sql):
    """Execute and return SQL call.

    This function executes a SQL call and returns the selected information.

    Args:
        cursor: A cursor object from a DB connection.
        sql: A string that represents the requests SQL data selection.

    Returns:
        A list of N-element tuples where N is the number of columns in the SQL request. The size of the list
        is the number of rows selected.
    """
    cursor.execute(sql)
    return cursor.fetchall()
