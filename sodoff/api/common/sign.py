from hashlib import md5

SIGN_KEY = '11A0CC5A-C4DF-4A0E-931C-09A44C9966AE'

def generate_signature(key, text):
  totaltext = key + text
  totaltext_bytes = totaltext.encode('utf-8')
  hashed = md5(totaltext_bytes)
  return hashed.hexdigest()
