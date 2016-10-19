import jinja2
import hashlib
import hmac
import random
from string import letters

SECRET = '0Ix.cF#2h1S?C*fQ6'

jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(['./templates', 'templates']), autoescape = True)

def make_salt():
	return ''.join(random.choice(letters) for x in xrange(5))

def make_pw_hash(name, pw, salt = None):
	if not salt:
		salt = make_salt()
	h = hashlib.sha256(name + pw + salt).hexdigest()
	return '%s|%s' % (h, salt)

def validate_pw(name, pw, h):
	salt = h.split('|')[1]
	return h == make_pw_hash(name, pw, salt)

def hash_user(user):
	return hmac.new(SECRET, user).hexdigest()

def make_secure_val(user):
	return '%s|%s' % (user, hash_user(user))

def check_secure_val(h):
	val = h.split('|')[0]
	if h == make_secure_val(val):
		return val

def render_str(template, **params):
	t = jinja_env.get_template(template)
	return t.render(params)