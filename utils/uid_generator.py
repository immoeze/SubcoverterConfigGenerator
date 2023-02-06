import uuid

def touch_uid(username: str) -> str:
    """
    return a 8letters len str, call 'user id'
    """
    return str(uuid.uuid5(uuid.NAMESPACE_OID, username))[0:8]
