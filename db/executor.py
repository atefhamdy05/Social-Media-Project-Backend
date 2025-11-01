import cx_Oracle
from project.helper import DotDict
import logging
from django.conf import settings
from django.utils.translation import gettext as _
import re

logger = logging.getLogger(__name__)

def connect_to_oracle(confs):
    try:
        # https://stackoverflow.com/questions/10455863/making-a-dictionary-list-with-cx-oracle
        dsn_tns = cx_Oracle.makedsn(confs.ip, confs.port, confs.schema)
        conn    = cx_Oracle.connect(confs.username, confs.password, dsn_tns)
    except Exception as e :
        logger.error(f'Connection error: {e}')

        

        return None

    return conn

def connect_to_oracle_with_default_confs(confs):
    if not confs:
        return connect_to_oracle(
                    DotDict({
                        'ip'       : settings.ORCL_IP,
                        'port'     : settings.ORCL_PORT,
                        'schema'   : settings.ORCL_SCHEMA,
                        'username' : settings.ORCL_USERNAME,
                        'password' : settings.ORCL_PASSWORD,
                    })
                )
    
    return connect_to_oracle(DotDict(confs))

def execute_query(query, params={}, is_dict=True, fetch_size=None):

    connection = connect_to_oracle_with_default_confs()
    if not connection:
        return {
            'data': None,
            'error': _('something went wrong while connecting to db')
        }
    cursor      = connection.cursor()

    try:
        cursor.execute(query, params)
    except Exception as e:
        return {
            'data': None,
            'error': _('something went wrong while getting data') + str(e),
        }

    # --- unified fetch logic ---
    fetcher = cursor.fetchall if fetch_size is None else lambda: cursor.fetchmany(fetch_size)
    rows = fetcher()

    # --- format data ---
    if is_dict:
        columns = [col[0].lower() for col in cursor.description]
        data = [dict(zip(columns, row)) for row in rows]
        error = None if data else _('this search has no data')
    else:
        data, error = rows, _('this search has no data')

    return {"data": data, "error": error}




def validate_and_execute(query, params={}):

    connection = connect_to_oracle_with_default_confs()
    if not connection:
        return True

    cursor      = connection.cursor()
    
    

    # 1. Find placeholders {something}
    placeholders = re.findall(r"{(\w+)}", query)

    # 2. Replace {param} with :param for Oracle binding
    safe_query = query
    params = {}
    for ph in placeholders:
        safe_query = safe_query.replace(f"{{{ph}}}", f":{ph}")
        params[ph] = params.get(ph)  # <-- if not provided, default = None

    try:
        cursor.execute(safe_query, params)
    except Exception:
        return False

    return True

