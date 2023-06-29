from datetime import datetime
from dateutil.parser import parse
import decimal

def datetime_converter(datetime_str):
    return parse(datetime_str)

pg_to_py_types = {
    'bigint': int,
    'bigserial': int,
    'bit': str,
    'bit varying': str,
    'boolean': bool,
    'box': str,  # custom Python class could be used
    'bytea': bytes,
    'character': str,
    'character varying': str,
    'cidr': str,  # consider ipaddress.IPv4Network or ipaddress.IPv6Network
    'circle': str,  # custom Python class could be used
    'date': datetime_converter,
    'double precision': float,
    'inet': str,  # consider ipaddress.IPv4Address or ipaddress.IPv6Address
    'integer': int,
    'interval': str,  # consider datetime.timedelta
    'json': str,  # consider using json.loads for conversion to Python dict
    'jsonb': str,  # consider using json.loads for conversion to Python dict
    'line': str,  # custom Python class could be used
    'lseg': str,  # custom Python class could be used
    'macaddr': str,
    'macaddr8': str,
    'money': decimal.Decimal,
    'numeric': decimal.Decimal,
    'path': str,  # custom Python class could be used
    'pg_lsn': str,
    'pg_snapshot': str,
    'point': str,  # custom Python class could be used
    'polygon': str,  # custom Python class could be used
    'real': float,
    'smallint': int,
    'smallserial': int,
    'serial': int,
    'text': str,
    'time': datetime_converter,
    'time with time zone': datetime_converter,
    'timestamp': datetime_converter,
    'timestamp with time zone': datetime_converter,
    'tsquery': str,
    'tsvector': str,
    'txid_snapshot': str,
    'uuid': str,
    'xml': str,  # consider using xml.etree.ElementTree for conversion to Python XML object
}
