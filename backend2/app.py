import datetime
import json
import random
from urllib.parse import urlparse
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime 
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

app.secret_key = 'replace-this-with-your-own-very-secret-key'


app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mini_telegram_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



db = SQLAlchemy(app)
migrate = Migrate(app, db)

# MODELS


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.BigInteger, unique=True, index=True, nullable=False)
    username = db.Column(db.String(64))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    language = db.Column(db.String(8), default='en')
    coins = db.Column(db.Integer, default=0, nullable=False)
    ton = db.Column(db.Float, default=0.0, nullable=False)
    referral_earnings = db.Column(db.Integer, default=0, nullable=False)
    spins = db.Column(db.Integer, default=10, nullable=False)  # Default 10 spins
    ad_credit = db.Column(db.Float, default=0.0, nullable=False)
    ads_watched_today = db.Column(db.Integer, default=0, nullable=False)
    tasks_completed_today_for_spin = db.Column(db.Integer, default=0, nullable=False)
    friends_invited_today_for_spin = db.Column(db.Integer, default=0, nullable=False)
    banned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    last_login = db.Column(db.DateTime, default=datetime.now())
    
    # Relationships
    # tasks = db.relationship('Task', backref='user', lazy=True)
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    space_defender_progress = db.relationship('SpaceDefenderProgress', backref='user', uselist=False)
    street_racing_progress = db.relationship('StreetRacingProgress', backref='user', uselist=False)
    promo_code_uses = db.relationship('PromoCodeUse', backref='user', lazy=True)
    referrals = db.relationship('Referral', foreign_keys='Referral.referrer_id', backref='referrer', lazy=True)
    referred_by = db.relationship('Referral', foreign_keys='Referral.referred_id', backref='referred', uselist=False)

    def to_dict(self):
        """Converts the User object and its key relationships into a JSON-serializable dictionary."""
        
        # --- Handle Nested Relationship Data ---
        # For one-to-one relationships, we can serialize them directly.
        # It's important to check if they exist first.
        
        space_defender_data = None
        if self.space_defender_progress:
            space_defender_data = {
                "weaponLevel": self.space_defender_progress.weapon_level,
                "shieldLevel": self.space_defender_progress.shield_level,
                "speedLevel": self.space_defender_progress.speed_level
            }

        street_racing_data = None
        if self.street_racing_progress:
            street_racing_data = {
                "currentCar": self.street_racing_progress.current_car,
                "careerPoints": self.street_racing_progress.career_points
                # Note: Unlocked cars and upgrades are in separate tables,
                # so they would typically be fetched via their own API endpoints
                # to keep this initial user payload smaller.
            }
        
        # --- Main User Dictionary ---
        return {
            "id": self.id,
            "telegramId": self.telegram_id,
            "username": self.username,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "language": self.language,
            "coins": self.coins,
            "ton": self.ton,
            "referralEarnings": self.referral_earnings,
            "spins": self.spins,
            "adCredit": self.ad_credit,
            "adsWatchedToday": self.ads_watched_today,
            "tasksCompletedTodayForSpin": self.tasks_completed_today_for_spin,
            "friendsInvitedTodayForSpin": self.friends_invited_today_for_spin,
            "banned": self.banned,
            
            # Convert datetime objects to ISO 8601 string format, which is a standard.
            # Check if they exist to prevent errors on newly created objects.
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "lastLogin": self.last_login.isoformat() if self.last_login else None,
            
            # Include the serialized relationship data.
            "spaceDefenderProgress": space_defender_data,
            "streetRacingProgress": street_racing_data
        }




class SpaceDefenderProgress(db.Model):
    __tablename__ = "space_defender_progress"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    weapon_level = db.Column(db.Integer, default=1, nullable=False)
    shield_level = db.Column(db.Integer, default=1, nullable=False)
    speed_level = db.Column(db.Integer, default=1, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())

class StreetRacingProgress(db.Model):
    __tablename__ = "street_racing_progress"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    current_car = db.Column(db.Integer, default=0, nullable=False)
    career_points = db.Column(db.Integer, default=0, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())

class CarUnlock(db.Model):
    __tablename__ = "car_unlocks"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    car_id = db.Column(db.Integer, nullable=False)
    unlocked_at = db.Column(db.DateTime, default=datetime.now())
    
    __table_args__ = (db.UniqueConstraint('user_id', 'car_id', name='_user_car_uc'),)

class CarUpgrade(db.Model):
    __tablename__ = "car_upgrades"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    car_id = db.Column(db.Integer, nullable=False)
    upgrade_type = db.Column(db.String(32), nullable=False)  # engine, tires, nitro
    level = db.Column(db.Integer, default=0, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    
    __table_args__ = (db.UniqueConstraint('user_id', 'car_id', 'upgrade_type', name='_user_car_upgrade_uc'),)

class AdProgress(db.Model):
    __tablename__ = "ad_progress"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ad_type = db.Column(db.String(32), nullable=False)  # engine, tires, nitro
    progress = db.Column(db.Integer, default=0, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    
    __table_args__ = (db.UniqueConstraint('user_id', 'ad_type', name='_user_ad_type_uc'),)




#Task related tables 

class DailyTask(db.Model):
    __tablename__ = "daily_tasks"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    reward = db.Column(db.Integer, nullable=False)
    icon_name = db.Column(db.String(64))
    link = db.Column(db.String(255))
    action = db.Column(db.String(64))  # 'check_in', 'visit', etc.
    mandatory = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())


class UserDailyTask(db.Model):
    __tablename__ = "user_daily_tasks"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    daily_task_id = db.Column(db.Integer, db.ForeignKey('daily_tasks.id'), nullable=False)

    completed = db.Column(db.Boolean, default=False)
    claimed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)

    __table_args__ = (db.UniqueConstraint('user_id', 'daily_task_id', name='_user_daily_task_uc'),)


class PartnerTask(db.Model):
    __tablename__ = "partner_tasks"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    reward = db.Column(db.Integer, nullable=False)
    icon_name = db.Column(db.String(64))
    link = db.Column(db.String(255))
    active = db.Column(db.Boolean, default=True)

    required_level = db.Column(db.Integer, nullable=False)

    # Ownership by user (not admin)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_by_user = db.relationship('User', backref='partner_tasks', lazy=True)

    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())


class UserPartnerTask(db.Model):
    __tablename__ = "user_partner_tasks"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    partner_task_id = db.Column(db.Integer, db.ForeignKey('partner_tasks.id'), nullable=False)

    # Track user’s current level
    current_level = db.Column(db.Integer, default=0, nullable=False)

    completed = db.Column(db.Boolean, default=False)
    claimed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)

    __table_args__ = (db.UniqueConstraint('user_id', 'partner_task_id', name='_user_partner_task_uc'),)


#Unified Table for Social & Game Tasks

# class Task(db.Model):
#     __tablename__ = "tasks"
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(255), nullable=False)
#     description = db.Column(db.Text)
#     reward = db.Column(db.Integer, default=0, nullable=False)

#     category = db.Column(db.String(32), nullable=False)  # 'Social', 'Game'
#     created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

#     task_type = db.Column(db.String(64), nullable=False)  # 'share', 'invite', 'play_game'
#     icon_name = db.Column(db.String(64))
#     link = db.Column(db.String(255))
#     active = db.Column(db.Boolean, default=True)

#     created_at = db.Column(db.DateTime, default=datetime.now())
#     updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())

# class UserTask(db.Model):
#     __tablename__ = "user_tasks"
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
#     task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)

#     completed = db.Column(db.Boolean, default=False)
#     claimed = db.Column(db.Boolean, default=False)
#     progress = db.Column(db.Integer, default=0)  # useful for multi-step tasks
#     completed_at = db.Column(db.DateTime)

#     __table_args__ = (db.UniqueConstraint('user_id', 'task_id', name='_user_task_uc'),)





class Transaction(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(32), nullable=False)  # Deposit, Withdrawal, Reward, Purchase
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(8), default='COINS')  # COINS, TON
    status = db.Column(db.String(32), default='Completed')  # Pending, Completed, Failed
    description = db.Column(db.Text)
    reference_id = db.Column(db.String(128))  # For external references
    created_at = db.Column(db.DateTime, default=datetime.now())

class CompletionTier(db.Model):
    __tablename__ = "completion_tiers"
    id = db.Column(db.Integer, primary_key=True)
    completions = db.Column(db.Integer, nullable=False, unique=True)
    cost = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())

class PromoCode(db.Model):
    __tablename__ = "promo_codes"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), unique=True, nullable=False)
    type = db.Column(db.String(32), nullable=False)  # COINS, SPINS, TON_AD_CREDIT
    value = db.Column(db.Float, nullable=False)
    max_uses = db.Column(db.Integer, nullable=False)
    expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.now())

class PromoCodeUse(db.Model):
    __tablename__ = "promo_code_uses"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    promo_code_id = db.Column(db.Integer, db.ForeignKey('promo_codes.id'), nullable=False)
    used_at = db.Column(db.DateTime, default=datetime.now())
    
    __table_args__ = (db.UniqueConstraint('user_id', 'promo_code_id', name='_user_promo_code_uc'),)

class Referral(db.Model):
    __tablename__ = "referrals"
    id = db.Column(db.Integer, primary_key=True)
    referrer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    referred_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    reward_claimed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now())

class SpinWheelPrize(db.Model):
    __tablename__ = "spin_wheel_prizes"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(32), nullable=False)  # COINS, SPINS, TON, etc.
    value = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    label = db.Column(db.String(32), nullable=False)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now())

class SpinResult(db.Model):
    __tablename__ = "spin_results"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    prize_id = db.Column(db.Integer, db.ForeignKey('spin_wheel_prizes.id'), nullable=False)
    spun_at = db.Column(db.DateTime, default=datetime.now())

class SpinStorePackage(db.Model):
    __tablename__ = "spin_store_packages"
    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.String(32), unique=True, nullable=False)  # e.g., 'sp10'
    spins = db.Column(db.Integer, nullable=False)
    cost_ton = db.Column(db.Float, nullable=False)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now())

class AdminUser(db.Model):
    __tablename__ = "admin_users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    permissions = db.Column(db.Text)  # Comma-separated permissions
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)






class UserCampaign(db.Model):
    __tablename__ = "user_campaigns"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    campaign_type = db.Column(db.String(64), nullable=False)  # Game, Social, Partner
    link = db.Column(db.String(255))
    goal = db.Column(db.Integer)
    cost = db.Column(db.Float)
    status = db.Column(db.String(32), default='Active')  # Active, Completed, Expired
    progress = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    

class LanguageOption(db.Model):
    __tablename__ = "language_options"
    id = db.Column(db.Integer, primary_key=True)
    language_id = db.Column(db.String(8), unique=True, nullable=False)  # en, ar, es, etc.
    name = db.Column(db.String(64), nullable=False)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now())

class SystemSetting(db.Model):
    __tablename__ = "system_settings"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())

#seeding users 

@app.cli.command("seed-users")
def seed_users():
    

    users = [
    User(
        telegram_id=111111111,
        username="alice",
        first_name="Alice",
        last_name="Wonder",
        language="en",
        coins=500,
        ton=1.25,
        referral_earnings=100,
        spins=5,
        ad_credit=200.0,
        created_at=datetime.now(),
        last_login=datetime.now()
    ),
    User(
        telegram_id=222222222,
        username="bob",
        first_name="Bob",
        last_name="Builder",
        language="en",
        coins=250,
        ton=0.5,
        referral_earnings=50,
        spins=3,
        ad_credit=75.0,
        created_at=datetime.now(),
        last_login=datetime.now()
    ),
    User(
        telegram_id=333333333,
        username="charlie",
        first_name="Charlie",
        last_name="Brown",
        language="ar",
        coins=100,
        ton=0.0,
        referral_earnings=0,
        spins=10,
        ad_credit=0.0,
        created_at=datetime.now(),
        last_login=datetime.now()
    )
]
    db.session.add_all(users)
    db.session.commit()

    print("✅ Users seeded")

@app.cli.command("seed-admin")
def seed_admin():
    """Creates an initial admin user for the application."""
    
    # --- Define your default admin credentials here ---
    # IMPORTANT: Change the password for a real production environment.
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "admin"
    
    # Check if the admin user already exists to avoid errors
    if AdminUser.query.filter_by(username=ADMIN_USERNAME).first():
        print(f"Admin user '{ADMIN_USERNAME}' already exists. Skipping.")
        return

    print(f"Creating initial admin user: {ADMIN_USERNAME}")

    # Create a new admin user instance
    new_admin = AdminUser(
        username=ADMIN_USERNAME,
        # Give the first admin all permissions. A wildcard '*' is a common convention.
        permissions='*', 
        active=True
    )

    # Use the secure method to hash and set the password
    new_admin.set_password(ADMIN_PASSWORD)

    # Add the new admin to the database session and commit
    db.session.add(new_admin)
    db.session.commit()

    print(f"✅ Admin user '{ADMIN_USERNAME}' created successfully.")
    print("You can now log in to the admin panel.")

def user_campaign_to_dict(campaign: UserCampaign):
    return {
        "id": campaign.id,
        "userId": campaign.user_id,
        "campaignType": campaign.campaign_type,
        "link": campaign.link,
        "goal": campaign.goal,
        "cost": campaign.cost,
        "status": campaign.status,
        "progress": campaign.progress,
        "createdAt": campaign.created_at.isoformat() if campaign.created_at else None,
        "updatedAt": campaign.updated_at.isoformat() if campaign.updated_at else None
    }


# IMPORTANT: This function needs to be updated to use sessions
def current_user():
    if  'user_id' in session:
        return User.query.get(session['user_id'])
    return  User.query.get(2) # No user is logged in


def get_setting(key, default=None):
    s = SystemSetting.query.filter_by(key=key).first()
    if not s:
        return default
    try:
        return json.loads(s.value)
    except Exception:
        return s.value

def set_setting(key, value):
    payload = json.dumps(value) if not isinstance(value, str) else value
    s = SystemSetting.query.filter_by(key=key).first()
    if not s:
        s = SystemSetting(key=key, value=payload, description=None)
        db.session.add(s)
    else:
        s.value = payload
    s.updated_at = now()
    db.session.commit()
    return value

def require_admin():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token.startswith('mock_token_'):
        return None
    try:
        admin_id = int(token.split('_')[-1])
    except Exception:
        return None
    return AdminUser.query.get(admin_id)

# def task_to_dict(t: Task):
#     return {
#         "id": t.id,
#         "title": t.title,
#         "description": t.description,
#         "reward": t.reward,
#         "category": t.category,
#         "taskType": t.task_type,
#         "iconName": t.icon_name,
#         "link": t.link,
#         "active": t.active,
#         "createdByUserId": t.created_by_user_id,
#         "createdAt": t.created_at.isoformat() if t.created_at else None,
#         "updatedAt": t.updated_at.isoformat() if t.updated_at else None,
#     }

def daily_task_to_dict(t: DailyTask, user: User):
    # include claimed/completed (derived from UserDailyTask)
    udt = UserDailyTask.query.filter_by(user_id=user.id, daily_task_id=t.id).first()
    return {
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "reward": t.reward,
        "iconName": t.icon_name,
        "link": t.link,
        "action": t.action,
        "mandatory": t.mandatory,
        "active": t.active,
        "claimed": bool(udt.claimed) if udt else False,
        "completed": bool(udt.completed) if udt else False,
    }

def partner_task_to_dict(p: PartnerTask, user: User = None):
    obj = {
        "id": p.id,
        "title": p.title,
        "description": p.description,
        "reward": p.reward,
        "iconName": p.icon_name,
        "link": p.link,
        "active": p.active,
        "requiredLevel": p.required_level,
    }
    if user:
        upt = UserPartnerTask.query.filter_by(user_id=user.id, partner_task_id=p.id).first()
        obj.update({
            "currentLevel": upt.current_level if upt else 0,
            "completed": bool(upt.completed) if upt else False,
            "claimed": bool(upt.claimed) if upt else False,
        })
    return obj

def user_campaign_to_dict(c: UserCampaign):
    return {
        "id": c.id,
        "userId": c.user_id,
        "campaignType": c.campaign_type,  # Game | Social | Partner
        "link": c.link,
        "goal": c.goal,
        "cost": c.cost,
        "status": c.status,  # Active | Completed | Expired
        "progress": c.progress,
        "createdAt": c.created_at.isoformat() if c.created_at else None,
        "updatedAt": c.updated_at.isoformat() if c.updated_at else None,
    }



# ENDPOINTS







# ----------------------------
# Helpers
# ----------------------------

CONVERSION_RATE = 1000  # 1 TON => 1000 coins (adjust if you store in SystemSetting)

def now():
    return datetime.now()


# In your main app.py file

# --- Make sure you have these imports at the top of your file ---

from urllib.parse import unquote # <-- ADD THIS IMPORT

# ... other imports ...

# NEW ENDPOINT: /auth/telegram
@app.post('/auth/telegram')
def auth_with_telegram():
    data = request.get_json()
    init_data_str = data.get('initData')

    if not init_data_str:
        return jsonify({"error": "initData is required"}), 400

    # !!! CRITICAL SECURITY STEP: You MUST validate the hash here !!!
    # (Your validation logic would go here)

    # Step 1: Parse the initData string into a dictionary
    params = dict(p.split('=') for p in init_data_str.split('&'))

    # Step 2: Get the raw, URL-encoded user string
    user_param_encoded = params.get('user')
    if not user_param_encoded:
        return jsonify({"error": "User data is missing from initData"}), 400

    # Step 3: **THIS IS THE FIX** - Decode the URL-encoded string
    user_param_decoded = unquote(user_param_encoded)

    # Step 4: Now, safely parse the decoded string as JSON
    try:
        user_data = json.loads(user_param_decoded)
    except json.JSONDecodeError:
        return jsonify({"error": "Failed to decode user JSON"}), 400
    
    telegram_id = user_data.get('id')
    if not telegram_id:
        return jsonify({"error": "Invalid user data in initData"}), 400

    # Find or create the user
    user = User.query.filter_by(telegram_id=telegram_id).first()
    if not user:
        user = User(
            telegram_id=telegram_id,
            username=user_data.get('username'),
            first_name=user_data.get('first_name'),
            last_name=user_data.get('last_name'),
            language=user_data.get('language_code'),
            # Ensure new users get default values for your app's fields
            coins=0,
            spins=10,
            ton=0.0
        )
        db.session.add(user)
    
    # Always update last_login for returning users
    user.last_login = datetime.now()
    db.session.commit()

    # Store the user's ID in the session to log them in
    session['user_id'] = user.id

    # Return the user's data
    return jsonify(user.to_dict())


# In your Flask app.py file

@app.post('/dev/login/<int:user_id>')
def dev_login(user_id):
    """
    Establishes a session for a specific user for development purposes.
    This function is the necessary first step before `current_user()` will work.
    """
    # Security check to prevent this from running in production.
    if  app.debug:
        return jsonify({"message": "This endpoint is for development only"}), 403

    # Step 1: Query the database for the user.
    user = User.query.get(user_id)

    # Step 2: **CRITICAL CHECK** - Handle the case where the user does not exist.
    if not user:
        # If no user is found, stop immediately and send a clear error message.
        # This prevents the `AttributeError` and ensures no invalid session is created.
        app.logger.error(f"DEV LOGIN FAILED: No user found with ID: {user_id}")
        return jsonify({"message": f"User with ID {user_id} not found."}), 404

    # Step 3: If the user was found, ESTABLISH the session.
    # This is the action that makes `current_user()` work on the next request.
    session.clear()
    session['user_id'] = user.id
    
    app.logger.info(f"DEV LOGIN SUCCESS: Session created for User ID {user.id} ({user.username})")

    # Step 4: Return the user's data to the frontend. This call is now safe.
    return jsonify(user.to_dict())




# NEW ENDPOINT for the updated fetchUser
@app.get('/user/me')
def get_current_user():
    user = current_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    return jsonify(user.to_dict()) # Return the logged-in user's data








# ----------------------------
# User-facing app
# ----------------------------

@app.get('/user')
def fetch_user():
    u = current_user()
    if not u:
        return jsonify({"error": "No users found"}), 404
    return jsonify({
        "id": u.id,
        "telegramId": u.telegram_id,
        "username": u.username,
        "firstName": u.first_name,
        "lastName": u.last_name,
        "language": u.language,
        "coins": u.coins,
        "ton": u.ton,
        "referralEarnings": u.referral_earnings,
        "spins": u.spins,
        "adCredit": u.ad_credit,
        "adsWatchedToday": u.ads_watched_today,
        "tasksCompletedTodayForSpin": u.tasks_completed_today_for_spin,
        "friendsInvitedTodayForSpin": u.friends_invited_today_for_spin,
        "createdAt": u.created_at.isoformat() if u.created_at else None,
        "lastLogin": u.last_login.isoformat() if u.last_login else None,
    })





@app.get('/daily-tasks')
def fetch_daily_tasks():
    u = current_user()
    tasks = DailyTask.query.order_by(DailyTask.id.asc()).all()
    return jsonify([daily_task_to_dict(t, u) for t in tasks])

@app.get('/game-tasks')
def fetch_game_tasks():
    # Return simplified mapping from UserCampaign (campaign_type='Game')
    # to match the mock's lightweight response
    conv = get_setting("CONVERSION_RATE", CONVERSION_RATE)
    campaigns = UserCampaign.query.filter_by(campaign_type='Game').order_by(UserCampaign.created_at.desc()).all()
    out = []
    for c in campaigns:
        host = None
        try:
            from urllib.parse import urlparse
            host = urlparse(c.link).hostname or "game"
        except Exception:
            host = "game"
        per_completion_reward_coins = (float(c.cost or 0) / float(c.goal or 1)) * 0.4 * float(conv)
        out.append({
            "id": c.id,
            "icon": "game",
            "title": f"Play {host}",
            "reward": per_completion_reward_coins
        })
    return jsonify(out)




ICONS = {
    'Game': '🎮',
    'Social': '📣',
    'Partner': '🎁',
}

@app.get('/quests')
def get_all_user_campaigns_and_partner_tasks():
    quests = []

    # --- Partner Tasks ---
    partner_tasks = PartnerTask.query.filter_by(active=True).all()
    for pt in partner_tasks:
        quests.append({
            'id': f'q_partner_{pt.id}',
            'icon': ICONS["Partner"],
            'title': pt.title,
            'reward': pt.reward,
            'currentProgress': 0,
            'totalProgress': pt.required_level
        })

    # --- User Campaigns ---
    user_campaigns = UserCampaign.query.order_by(UserCampaign.created_at.desc()).all()
    for uc in user_campaigns:
        quests.append({
            'id': f'q_campaign_{uc.id}',
            'icon': ICONS["Social"],  # Example: use campaign type as icon name
            'title': f"{uc.campaign_type}",
            'reward': int(uc.cost or 0),  # If cost represents payout
            'currentProgress': uc.progress or 0,
            'totalProgress': uc.goal or 1
        })

    return jsonify(quests)



@app.get('/transactions')
def fetch_transactions():
    u = current_user()
    txs = Transaction.query.filter_by(user_id=u.id).order_by(Transaction.created_at.desc()).all()
    out = []
    for t in txs:
        out.append({
            "id": t.id,
            "type": t.type,
            "amount": t.amount,
            "currency": t.currency,
            "status": t.status,
            "description": t.description,
            "referenceId": t.reference_id,
            "date": (t.created_at.date().isoformat() if t.created_at else None)
        })
    return jsonify(out)

@app.get('/friends')
def fetch_friends():
    # No Friend model in schema; return empty or add your own source later
    return jsonify([])

@app.get('/user-campaigns')
def fetch_user_campaigns():
    u = current_user()
    #u = User.query.get(2)
    
    cs = UserCampaign.query.filter_by(user_id=u.id).order_by(UserCampaign.created_at.desc()).all()
    return jsonify([user_campaign_to_dict(c) for c in cs])




@app.get('/partner-campaigns')
def fetch_partner_campaigns():
    # Show the whole catalog of partner tasks + user's progress
    # u = current_user()
    user_campaigns = UserCampaign.query.filter_by(campaign_type='Partner').all()

    def serialize_campaign(c: UserCampaign):
        partner_task = PartnerTask.query.filter_by(link=c.link).first()
        return {
            "id": c.id,
            "link": c.link,
            "goal": c.goal,
            "cost": c.cost,
            "completions": c.progress,
            "status": c.status,
            "requiredLevel": partner_task.required_level if partner_task else 1  # ✅ fix
        }

    return jsonify([serialize_campaign(c) for c in user_campaigns])




@app.post('/user-campaigns')
def add_user_campaign():
    """
    Body: { link: str, goal: int, cost: float, category?: 'Social'|'Game' }
    Deduct adCredit, create UserCampaign.
    """


    u = current_user()

    app.logger.error(f" FAILED: No user found with ID: {u}")

    data = request.get_json(force=True) or {}

    # # Get user from request body (for Postman) or from current_user()
    # user_id = data.get("user_id")
    # if user_id:
    #     u = User.query.get(user_id)
    #     if not u:
    #         return jsonify({"success": False, "message": "User not found"}), 404
    # else:
    #     u = current_user()
    #     if not u:
    #         return jsonify({"success": False, "message": "Authentication required"}), 401


    link = data.get('link', '')

    category = "Social"  # default
    
    if "t.me" in link:
        parsed = urlparse(link)
        path = parsed.path.strip("/")  # e.g. "EmpiresBattleBot"
        
        if path.lower().endswith("bot"):
            category = "Game"
        else:
            category = "Social"

    goal = int(data.get('goal') or 1)
    cost = float(data.get('cost') or 0.0)

    if (u.ad_credit or 0.0) < cost:
        return jsonify({"success": False, "message": "Insufficient ad balance. Please add funds."}), 400

    u.ad_credit = float(u.ad_credit) - cost

    c = UserCampaign(
        user_id=u.id,
        campaign_type=category,  # 'Social' or 'Game'
        link=link,
        goal=goal,
        cost=cost,
        status='Active',
        progress=0
    )
    db.session.add(c)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Campaign created successfully!",
        "newCampaign": user_campaign_to_dict(c),
        "user": {"id": u.id, "adCredit": u.ad_credit, "coins": u.coins, "spins": u.spins}
    })




@app.post('/partner-tasks')
def add_partner_task():
    """
    Body: { link: str, goal: int, cost: float, level: int }
    Deduct adCredit, create PartnerTask (catalog) + a UserCampaign(row) with campaign_type='Partner' for tracking cost/goal/progress.
    """
    u = current_user()
    # u=User.query.get(2)
    # created_by_user_id=u.id


    data = request.get_json(force=True) or {}
    link = data.get('link')
    goal = int(data.get('goal') or 1)
    cost = float(data.get('cost') or 0.0)
    level = int(data.get('level') or 1)

    if (u.ad_credit or 0.0) < cost:
        return jsonify({"success": False, "message": "Insufficient ad balance. Please add funds."}), 400

    u.ad_credit = float(u.ad_credit) - cost

    # Create the PartnerTask definition (reward is up to you; use coins-per-completion heuristic or set via admin)
    # Here we set a neutral reward; you can compute from cost/goal if desired
    pt = PartnerTask(
        title=f"Partner task to reach level {level}",
        description=None,
        reward=0,  # reward distribution can be handled when completions happen
        icon_name=None,
        link=link,
        active=True,
        required_level=level,
        created_by_user_id=u.id  # ✅ This is the fix

    )
    db.session.add(pt)
    db.session.flush()  # get pt.id

    # Create a tracking campaign entry for the creator
    uc = UserCampaign(
        user_id=u.id,
        campaign_type='Partner',
        link=link,
        goal=goal,
        cost=cost,
        status='Active',
        progress=0
    )
    db.session.add(uc)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Partner task created successfully!",
        "newCampaign": user_campaign_to_dict(uc),
        "user": {"id": u.id, "adCredit": u.ad_credit, "coins": u.coins, "spins": u.spins}
    })

@app.post('/ad-credit/deposit')
def deposit_ad_credit():
    """
    Body: { amount: float }
    """
    u = current_user()


    data = request.get_json(force=True) or {}
    amount = float(data.get('amount') or 0.0)
    u.ad_credit = float(u.ad_credit or 0) + amount

    tx = Transaction(
        user_id=u.id,
        type='Deposit',
        amount=amount,
        currency='TON',
        status='Completed',
        description='Ad credit deposit',
        reference_id=None,
        created_at=now()
    )
    db.session.add(tx)
    db.session.commit()

    return jsonify({"success": True, "user": {"id": u.id, "adCredit": u.ad_credit}})

@app.post('/daily-tasks/<int:task_id>/claim')
def claim_daily_task(task_id: int):
    u = current_user()
    dtask = DailyTask.query.get(task_id)
    if not dtask:
        return jsonify({"success": False, "user": None}), 404

    udt = UserDailyTask.query.filter_by(user_id=u.id, daily_task_id=dtask.id).first()
    if not udt:
        udt = UserDailyTask(user_id=u.id, daily_task_id=dtask.id, completed=True, claimed=False)
        db.session.add(udt)

    if udt.claimed:
        return jsonify({"success": False, "user": None}), 400

    # credit coins
    u.coins += int(dtask.reward or 0)
    udt.claimed = True
    udt.completed = True
    udt.completed_at = now()

    # +1 spin if daily limit not reached (50)
    if (u.tasks_completed_today_for_spin or 0) < 50:
        u.spins += 1
        u.tasks_completed_today_for_spin = int(u.tasks_completed_today_for_spin or 0) + 1

    db.session.commit()
    return jsonify({"success": True, "user": {
        "id": u.id, "coins": u.coins, "spins": u.spins,
        "tasksCompletedTodayForSpin": u.tasks_completed_today_for_spin
    }})

@app.post('/referrals/claim')
def claim_referral_earnings():
    u = current_user()
    if (u.referral_earnings or 0) <= 0:
        return jsonify({"success": False, "user": None}), 400
    u.coins += int(u.referral_earnings)
    u.referral_earnings = 0
    db.session.commit()
    return jsonify({"success": True, "user": {"id": u.id, "coins": u.coins}})

@app.post('/withdrawals')
def execute_withdrawal():
    """
    Body: { amountInTon: number }
    Converts to coins using CONVERSION_RATE and withdraws.
    """
    u = current_user()
    data = request.get_json(force=True) or {}
    amount_ton = float(data.get('amountInTon') or 0.0)
    conv = float(get_setting("CONVERSION_RATE", CONVERSION_RATE))
    amount_coins = amount_ton * conv

    if (u.coins or 0) < amount_coins:
        return jsonify({"success": False, "user": None}), 400

    u.coins -= amount_coins
    u.ton = float(u.ton or 0) + amount_ton

    tx = Transaction(
        user_id=u.id,
        type='Withdrawal',
        amount=amount_ton,
        currency='TON',
        status='Completed',
        description='User withdrawal',
        reference_id=None,
        created_at=now()
    )
    db.session.add(tx)
    db.session.commit()
    return jsonify({"success": True, "user": {"id": u.id, "coins": u.coins, "ton": u.ton}})

@app.post('/spin-wheel')
def spin_wheel():
    u = current_user()
    if (u.spins or 0) <= 0:
        return jsonify({
            "success": False,
            "prize": {"type": "ERROR", "value": 0, "label": "No spins left"},
            "user": {"id": u.id, "spins": u.spins}
        }), 400

    u.spins -= 1

    prizes = SpinWheelPrize.query.filter_by(active=True).all()
    if not prizes:
        return jsonify({"success": False, "message": "No prizes configured", "user": {"id": u.id, "spins": u.spins}}), 500

    total_weight = sum(p.weight for p in prizes)
    r = random.uniform(0, total_weight)
    upto = 0
    selected = prizes[-1]
    for p in prizes:
        if upto + p.weight >= r:
            selected = p
            break
        upto += p.weight

    # Apply prize
    if selected.type == 'COINS':
        u.coins += int(selected.value or 0)
    elif selected.type == 'SPINS':
        u.spins += int(selected.value or 0)
    elif selected.type == 'TON':
        u.ton = float(u.ton or 0) + float(selected.value or 0)

    # Log spin result
    sr = SpinResult(user_id=u.id, prize_id=selected.id, spun_at=now())
    db.session.add(sr)
    db.session.commit()

    return jsonify({
        "success": True,
        "prize": {"type": selected.type, "value": selected.value, "label": selected.label},
        "user": {"id": u.id, "coins": u.coins, "spins": u.spins, "ton": u.ton}
    })

@app.post('/spins/watch-ad')
def watch_ad_for_spin():
    u = current_user()
    if (u.ads_watched_today or 0) >= 50:
        return jsonify({"success": False, "message": "Daily limit for ad spins reached."}), 400
    u.ads_watched_today = int(u.ads_watched_today or 0) + 1
    u.spins = int(u.spins or 0) + 1
    db.session.commit()
    return jsonify({"success": True, "message": "+1 Spin!", "user": {"id": u.id, "spins": u.spins}})

@app.post('/spins/complete-task')
def complete_task_for_spin():
    u = current_user()
    if (u.tasks_completed_today_for_spin or 0) >= 50:
        return jsonify({"success": False, "message": "Daily limit for task spins reached."}), 400
    u.tasks_completed_today_for_spin = int(u.tasks_completed_today_for_spin or 0) + 1
    u.spins = int(u.spins or 0) + 1
    db.session.commit()
    return jsonify({"success": True, "message": "+1 Spin for completing a task!", "user": {"id": u.id, "spins": u.spins}})

@app.post('/spins/invite-friend')
def invite_friend_for_spin():
    u = current_user()
    if (u.friends_invited_today_for_spin or 0) >= 50:
        return jsonify({"success": False, "message": "Daily limit for friend invite spins reached."}), 400
    u.friends_invited_today_for_spin = int(u.friends_invited_today_for_spin or 0) + 1
    u.spins = int(u.spins or 0) + 1
    db.session.commit()
    return jsonify({"success": True, "message": "+1 Spin for inviting a friend!", "user": {"id": u.id, "spins": u.spins}})

@app.post('/spins/buy')
def buy_spins():
    """
    Body: { packageId: string, currency: 'TON' | 'COINS' }
    """
    u = current_user()
    data = request.get_json(force=True) or {}
    package_id = data.get('packageId')
    currency = data.get('currency', 'COINS')

    pkg = SpinStorePackage.query.filter_by(package_id=package_id, active=True).first()
    if not pkg:
        return jsonify({"success": False, "message": "Invalid package selected."}), 400

    if currency == 'COINS':
        conv = float(get_setting("CONVERSION_RATE", CONVERSION_RATE))
        cost_in_coins = float(pkg.cost_ton) * conv
        if (u.coins or 0) < cost_in_coins:
            return jsonify({"success": False, "message": "Insufficient coin balance."}), 400
        u.coins -= cost_in_coins
    # TON purchase path normally requires on-chain/payment verification → skipped (like the mock)

    u.spins = int(u.spins or 0) + int(pkg.spins or 0)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": f"Successfully purchased {pkg.spins} spins!",
        "user": {"id": u.id, "spins": u.spins, "coins": u.coins}
    })

@app.post('/promo-codes/redeem')
def redeem_promo_code():
    """
    Body: { code: string }
    """
    u = current_user()
    data = request.get_json(force=True) or {}
    code = (data.get('code') or '').strip()

    pc = PromoCode.query.filter(func.lower(PromoCode.code) == code.lower()).first()
    if not pc:
        return jsonify({"success": False, "message": "Invalid promo code."}), 400

    # count uses
    uses_count = PromoCodeUse.query.filter_by(promo_code_id=pc.id).count()
    if pc.max_uses is not None and uses_count >= pc.max_uses:
        return jsonify({"success": False, "message": "This promo code has reached its usage limit."}), 400

    if pc.expires_at and pc.expires_at < now():
        return jsonify({"success": False, "message": "This promo code has expired."}), 400

    already = PromoCodeUse.query.filter_by(user_id=u.id, promo_code_id=pc.id).first()
    if already:
        return jsonify({"success": False, "message": "You have already used this promo code."}), 400

    reward_message = ''
    if pc.type == 'COINS':
        u.coins += int(pc.value)
        reward_message = f"{int(pc.value):,} Coins"
    elif pc.type == 'SPINS':
        u.spins += int(pc.value)
        reward_message = f"{int(pc.value)} free spin(s)"
    elif pc.type == 'TON_AD_CREDIT':
        u.ad_credit = float(u.ad_credit or 0) + float(pc.value)
        reward_message = f"{pc.value} TON in ad credits"

    use = PromoCodeUse(user_id=u.id, promo_code_id=pc.id, used_at=now())
    db.session.add(use)
    db.session.commit()

    return jsonify({"success": True, "message": f"Successfully redeemed! You received {reward_message}.", "user": {
        "id": u.id, "coins": u.coins, "spins": u.spins, "adCredit": u.ad_credit
    }})

# ----------------------------
# Admin-facing app
# ----------------------------

@app.post('/admin/login')
def admin_login():
    """
    Body: { username, password }
    Returns: { success, token? }
    """
    data = request.get_json(force=True) or {}
    username = data.get('username')
    password = data.get('password')
    admin = AdminUser.query.filter_by(username=username, active=True).first()
    if admin and admin.check_password(password):
        return jsonify({"success": True, "token": f"mock_token_{admin.id}"})
    return jsonify({"success": False}), 401



@app.get('/admin/dashboard-stats')
def fetch_dashboard_stats():
    admin = require_admin()
    if not admin:
        return jsonify({"error": "Unauthorized"}), 401
    total_users = User.query.count()
    total_coins = db.session.query(func.coalesce(func.sum(User.coins), 0)).scalar()
    total_withdrawals = db.session.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(Transaction.type == 'Withdrawal').scalar()
    tasks_completed = db.session.query(func.count(UserDailyTask.id)).filter(UserDailyTask.claimed == True).scalar()
    return jsonify({
        "totalUsers": total_users,
        "totalCoins": int(total_coins or 0),
        "totalWithdrawals": float(total_withdrawals or 0),
        "tasksCompleted": int(tasks_completed or 0)
    })

@app.get('/admin/users')
def fetch_all_users():
    admin = require_admin()
    # if not admin:
    #     return jsonify({"error": "Unauthorized"}), 401

    users = User.query.order_by(User.id.desc()).all()
    
    return jsonify([
        {
            "id": u.id,
            "name": u.username or f"{u.first_name or ''} {u.last_name or ''}".strip() or "Unknown",
            "coins": u.coins,
            "spins": u.spins,
            "adCredit": u.ad_credit,
            "banned": u.banned
        }
        for u in users
    ])

@app.patch('/admin/users/<int:user_id>')
def update_user(user_id: int):
    admin = require_admin()
    if not admin:
        return jsonify({"error": "Unauthorized"}), 401
    u = User.query.get_or_404(user_id)
    data = request.get_json(force=True) or {}
    # whitelist of updatable fields
    for field in ["username", "first_name", "last_name", "language", "coins", "ton", "spins", "ad_credit", "banned"]:
        if field in data:
            setattr(u, field, data[field])
    db.session.commit()
    return jsonify({"success": True, "user": {
        "id": u.id, "username": u.username, "coins": u.coins, "spins": u.spins, "adCredit": u.ad_credit
    }})

@app.get('/admin/promo-codes')
def fetch_all_promo_codes():
    admin = require_admin()
    if not admin:
        return jsonify({"error": "Unauthorized"}), 401
    pcs = PromoCode.query.order_by(PromoCode.created_at.desc()).all()
    out = []
    for p in pcs:
        used_count = PromoCodeUse.query.filter_by(promo_code_id=p.id).count()
        out.append({
            "id": p.id, "code": p.code, "type": p.type, "value": p.value,
            "maxUses": p.max_uses, "expiresAt": p.expires_at.isoformat() if p.expires_at else None,
            "usedCount": used_count
        })
    return jsonify(out)

@app.post('/admin/promo-codes')
def create_promo_code():
    admin = require_admin()
    if not admin:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json(force=True) or {}
    code = (data.get('code') or '').strip()
    if not code:
        return jsonify({"success": False}), 400
    exists = PromoCode.query.filter(func.lower(PromoCode.code) == code.lower()).first()
    if exists:
        return jsonify({"success": False}), 409
    pc = PromoCode(
        code=code,
        type=data.get('type'),
        value=float(data.get('value') or 0),
        max_uses=int(data.get('maxUses') or 0),
        expires_at=(datetime.fromisoformat(data['expiresAt']) if data.get('expiresAt') else None),
        created_at=now()
    )
    db.session.add(pc)
    db.session.commit()
    return jsonify({"success": True, "code": {
        "id": pc.id, "code": pc.code, "type": pc.type, "value": pc.value,
        "maxUses": pc.max_uses, "expiresAt": pc.expires_at.isoformat() if pc.expires_at else None
    }})

@app.get('/admin/settings')
def fetch_settings():
    admin = require_admin()
    if not admin:
        return jsonify({"error": "Unauthorized"}), 401
    # Read a few known settings; add more keys as needed
    auto_withdrawals = bool(get_setting("autoWithdrawals", False))
    ad_networks = get_setting("adNetworks", [])
    conv = float(get_setting("CONVERSION_RATE", CONVERSION_RATE))
    # Return admins list too (like mock)
    admins = AdminUser.query.filter_by(active=True).all()
    return jsonify({
        "autoWithdrawals": auto_withdrawals,
        "adNetworks": ad_networks,
        "CONVERSION_RATE": conv,
        "admins": [{"id": a.id, "username": a.username, "active": a.active} for a in admins]
    })

@app.patch('/admin/settings')
def update_settings():
    admin = require_admin()
    if not admin:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json(force=True) or {}
    if "autoWithdrawals" in data:
        set_setting("autoWithdrawals", bool(data["autoWithdrawals"]))
    if "adNetworks" in data:
        set_setting("adNetworks", data["adNetworks"])
    if "CONVERSION_RATE" in data:
        set_setting("CONVERSION_RATE", float(data["CONVERSION_RATE"]))
    return jsonify({"success": True, "settings": {
        "autoWithdrawals": get_setting("autoWithdrawals", False),
        "adNetworks": get_setting("adNetworks", []),
        "CONVERSION_RATE": float(get_setting("CONVERSION_RATE", CONVERSION_RATE))
    }})

@app.post('/admin/tasks')
def create_admin_task():
    """
    Body: { title, description?, reward, category: 'Daily'|'Game'|'Social'|'Partner', taskType?, iconName?, link? }
    Behaves like your mock: creates records in the appropriate tables.
    """
    admin = require_admin()
    if not admin:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json(force=True) or {}
    category = data.get('category')

    if category == 'Daily':
        t = DailyTask(
            title=data.get('title'),
            description=data.get('description'),
            reward=int(data.get('reward') or 0),
            icon_name=data.get('iconName'),
            link=data.get('link'),
            action=data.get('taskType') or 'visit',
            mandatory=bool(data.get('mandatory', False)),
            active=True
        )
        db.session.add(t)
        db.session.commit()
        return jsonify({"success": True, "task": {
            "id": t.id, "title": t.title, "reward": t.reward, "category": "Daily"
        }})

    elif category in ('Game', 'Social'):
        # Admin-created “campaign template” → store as UserCampaign with no owner (or admin-owned)
        uc = UserCampaign(
            user_id=None,  # admin-owned/global
            campaign_type=category,
            link=data.get('link') or 'https://t.me/example_bot',
            goal=1,
            cost=0.1,
            status='Active',
            progress=0
        )
        db.session.add(uc)
        db.session.commit()
        return jsonify({"success": True, "task": {"id": uc.id, "category": category}})

    elif category == 'Partner':
        # Create PartnerTask with a default required_level
        pt = PartnerTask(
            title=data.get('title') or 'Partner task',
            description=data.get('description'),
            reward=int(data.get('reward') or 0),
            icon_name=data.get('iconName'),
            link=data.get('link') or 'https://t.me/example_partner_bot',
            active=True,
            required_level=int(data.get('requiredLevel') or 5)
        )
        db.session.add(pt)
        db.session.commit()
        return jsonify({"success": True, "task": {"id": pt.id, "category": "Partner"}})

    return jsonify({"success": False}), 400



if __name__ == '__main__':
    
    app.run(debug=True)