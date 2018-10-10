import string

ALPHABET = list(string.ascii_uppercase)
ALL_LINES = ['row', 'column', 'diagonal']
KEYS = ['left', 'down', 'right']
KEYS_TO_TRIAL_TYPE = {k:a for k, a in zip(KEYS, ALL_LINES)}