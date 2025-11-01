from django.conf import settings
import cx_Oracle
import logging

logger = logging.getLogger(__name__)

class OraclePoolManager:
    conn = None

    def __init__(self, confs=None):
        try:
            if not confs:
                dsn_tns = cx_Oracle.makedsn(settings.ORCL_IP, settings.ORCL_PORT, settings.ORCL_SCHEMA)
                self.conn = cx_Oracle.connect(settings.ORCL_USERNAME, settings.ORCL_PASSWORD, dsn_tns)
            else:
                dsn_tns = cx_Oracle.makedsn(confs.ip, confs.port, confs.schema)
                self.conn = cx_Oracle.connect(confs.username, confs.password, dsn_tns)

        except Exception as e:
            logger.error(f'Connection error: {e}')
            self.conn = None
            
            

    def get_connection(self):
        return self.conn

oracle_pool = OraclePoolManager()
