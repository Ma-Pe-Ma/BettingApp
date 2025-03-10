class Default(object):
    # url of the site
    SITE_ADDRESS = 'betting.app'

    # email which will be notified for expiring certificates
    CERT_EMAIL = 'email@betting.app'

    # location of cache files
    CACHE_DIR = './cache'

    # the supported lanugages on the site
    SUPPORTED_LANGUAGES = {'en' : ['English', 'Angol'], 'hu' : ['Hungarian', 'Magyar']}
    # secret key for session handling
    SECRET_KEY = 'dev'

    # upload folder's name in the instance folder
    UPLOAD_FOLDER = 'upload'
    # allowed extensions to upload by the user
    ALLOWED_EXTENSIONS = ['csv', 'sqlite']

    # maximum lifetime of a session
    PERMANENT_SESSION_LIFETIME = 3600 * 24 * 45 # used by Flask
    SESSION_LIFE_TIME = 45 # in minutes, custom solution

    SQLALCHEMY_DATABASE_URI = 'sqlite:///flaskr.sqlite'
    MATCH_URL = 'https://path.fixture'

    BABEL_TRANSLATION_DIRECTORIES = './assets/translations'

    IDENT_URL = 'https://www.gravatar.com/avatar/{email_hash}?d=identicon&s=128'

    CACHE_TYPE = 'FileSystemCache'
    CACHE_DEFAULT_TIMEOUT = 300

    # USED BY APSCHEDULER
    SCHEDULER_TIMEZONE = 'UTC'

    # 0 - not using, 1 - email, 2 - browser notification
    DIRECT_MESSAGING = 0

    # to generate the vapid keys for push notification with node js: web-push generate-vapid-keys [--json]
    PUSH_KEYS = {
        'public' : 'public key',
        'private' : 'private key',
        'email' : 'mailto:YourNameHere@example.org'
    }

    INVITATION_KEYS = {
      'user' : 'registration',
      'admin' : 'admin'
    }

    DEADLINE_TIMES = {
      'register' : '2022-11-20 18:00',
      'group_evaluation' : '2022-11-29 19:00',
      'tournament_end' : '2022-12-22 23:59'
    }

    MATCH_TIME_LENGTH = {
      'base_time' : 2,
      'extra_time' : 2.5
    }

    BET_VALUES = {
      'starting_bet_amount' : 2000,
	    'max_group_bet_value' : 50,
	    'max_tournament_bet_value' : 200,
	    'default_max_bet_per_match' : 50
    }

    GROUP_BET_HIT_MAP = {
		  'h0' : 0,
		  'h1' : 1,
		  'h2' : 2,
		  'h3' : 0,
		  'h4' : 4
	  }

    BONUS_MULTIPLIERS = {
      "bullseye" : 4,
      "difference" : 1
    }

    DEBUG_START_TIME = '2024-06-14 16:00'
