class RetryableEmailError(Exception):
    """Temporary email failure (SMTP timeout, network glitch, redis hiccup, DB connection reset)"""
    pass

class PermanentEmailError(Exception):
    """Permanent failure (invalid email, user deleted, logic bug, wrong SQL query)"""
    pass