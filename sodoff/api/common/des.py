from Crypto.Cipher import DES3
from Crypto.Util.Padding import pad, unpad
from flask import request, Response
from werkzeug.datastructures import ImmutableMultiDict
from hashlib import md5
from base64 import b64decode, b64encode
from functools import wraps

ENCODING_WRAPPING_NONE = '{encrypted}'
ENCODING_WRAPPING_XML_STRING = '<?xml version="1.0" encoding="utf-8"?>\n<string>{encrypted}</string>'

BLOCK_SIZE = 8

# the key initially used by the game for the DWADragonsMain.xml file
ASCII_KEY = 'C92EC1AA-54CD-4D0C-A8D5-403FCCF1C0BD'
ASCII_CODING = 'utf-8'

# the key used for api requests
KEY = '56BB211B-CF06-48E1-9C1D-E40B5173D759'
CODING = 'utf-16-le'

# the key used for signing
SIGN_KEY = '11A0CC5A-C4DF-4A0E-931C-09A44C9966AE'

# converts the string keys as used by SoD to DES keys
def get_key(key_string, coding):
  key_bytes = key_string.encode(encoding=coding)
  key_hash = md5(key_bytes).digest()
  # repeat first 8 bytes at the end to get full 24 byte key array
  return key_hash + key_hash[:8]


def decrypt(input, key, coding):
  key = get_key(key, coding)
  cipher = DES3.new(key, DES3.MODE_ECB)
  base64_decoded = b64decode(input)
  decrypted = cipher.decrypt(base64_decoded)
  decrypted_unpadded = unpad(decrypted, BLOCK_SIZE)
  decrypted_string = decrypted_unpadded.decode(coding)
  return decrypted_string


def encrypt(input, key, coding, wrapping):
  key = get_key(key, coding)
  cipher = DES3.new(key, DES3.MODE_ECB)
  input_bytes = input.encode(encoding=coding)
  input_bytes_padded = pad(input_bytes, BLOCK_SIZE)
  encrypted = cipher.encrypt(input_bytes_padded)
  encrypted_string = b64encode(encrypted)
  return wrapping.format(encrypted=encrypted_string.decode('utf-8')).encode('utf-8')


def generate_signature(key, text):
  totaltext = key + text
  totaltext_bytes = totaltext.encode('utf-8')
  hashed = md5(totaltext_bytes)
  return hashed.hexdigest()


def encrypt_flask_response(wrapping):
  def decorator(view):
    @wraps(view)
    def wrapped_view(**kwargs):
      plaintext = view(**kwargs)
      return encrypt(plaintext, KEY, CODING, wrapping)
    return wrapped_view
  return decorator


def decrypt_flask_request(name):
  def decorator(view):
    @wraps(view)
    def wrapped_view(**kwargs):
      old_form = request.form.to_dict()
      old_form[name] = decrypt(old_form[name], KEY, CODING)
      request.form = ImmutableMultiDict(old_form)
      return view(**kwargs)
    return wrapped_view
  return decorator


def sign_flask_response(view):
  @wraps(view)
  def wrapped_view(**kwargs):
    out = view(**kwargs)
    plain = out
    if type(out) == bytes:
      plain = out.decode('utf-8')
    response = Response(out)
    response.headers['Signature'] = generate_signature(plain, SIGN_KEY)
    return response
  return wrapped_view


# TODO: this is a useful helper for decrypting strings easily
if __name__ == '__main__':
  rules = '''EV6xCtFqiuTAmQRvSlYaTsTyHQ+al47rqaMbZ5cr48dKCy9JH+BRuK4ILxEM3Us2KnfbL5uRCuSzDger5xNbEJ4CGc15qbTWiKvWEylCqacTnkkzPLANQB0kaDWfo3bXSoQTQCS+FpCLADzrpfGKtXoC7aGfAY/eFgo+ha/8mtboq0gLuZzM05QkAeo0BDz0OcJMk97+9Azs0WzEGxUwxugg64spl3uowDZRWmn4GLoEDzm73j12i49w7aGUO0FKx/cYtlaEoWj4sKqPBv
f53mgZP4mHP8SRFIVVxfSQPWyB7tnlYFsLzt+seVVl4L+DZsK72NhscF9Y4B/YSDe9zayZbBxw4PgeFIVVxfSQPWwGQaRu9j9MShOeSTM8sA1AHSRoNZ+jdtdKhBNAJL4WkIsAPOul8Yq1ujlErEC5zl0=
'''
  print(decrypt(rules.replace('\n', ''), KEY, CODING))

  # print(encrypt('<ParentLoginInfo xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><UserName xsi:nil="true" /><Email xsi:nil="true" /><ApiToken>00000000-0000-0000-0000-000000000000</ApiToken><UserID>00000000-0000-0000-0000-000000000000</UserID><AccountOwnerLoginInfo xsi:nil="true" /><CudosToken xsi:nil="true" /><ExpiryDate xsi:nil="true" /><LoginStatus>UserPolicyNotAccepted</LoginStatus><SendActivationReminder xsi:nil="true" /><UnAuthorized xsi:nil="true" /><IsUserAllowedToPlay xsi:nil="true" /><DaysToDelete>0</DaysToDelete><IsPreRegisteredUser xsi:nil="true" /><LoginDuration xsi:nil="true" /><IsGuestSynced xsi:nil="true" /><gsk xsi:nil="true" /><AdditionalData xsi:nil="true" /><MembershipID xsi:nil="true" /><UserPolicy xsi:nil="true" /></ParentLoginInfo>', KEY, CODING, ENCODING_WRAPPING_NONE))