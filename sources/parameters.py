import string

ALPHABET = [ u'\u03B5',u'\u03B4',u'\u03B6',u'\u03B7',u'\u03B8',u'\u03C2 ',u'\u03C6',
				u'\u03C8',u'\u03C9']
				
ALL_LINES = ['row', 'column', 'diagonal']
KEYS = ['left', 'down', 'right']
KEYS_TO_TRIAL_TYPE = {k:a for k, a in zip(KEYS, ALL_LINES)}