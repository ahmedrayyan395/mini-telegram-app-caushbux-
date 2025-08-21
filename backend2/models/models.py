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
    tasks = db.relationship('Task', backref='user', lazy=True)
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

class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    reward = db.Column(db.Integer, default=0, nullable=False)

    category = db.Column(db.String(32), nullable=False)  # 'Social', 'Game'
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    task_type = db.Column(db.String(64), nullable=False)  # 'share', 'invite', 'play_game'
    icon_name = db.Column(db.String(64))
    link = db.Column(db.String(255))
    active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())

class UserTask(db.Model):
    __tablename__ = "user_tasks"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)

    completed = db.Column(db.Boolean, default=False)
    claimed = db.Column(db.Boolean, default=False)
    progress = db.Column(db.Integer, default=0)  # useful for multi-step tasks
    completed_at = db.Column(db.DateTime)

    __table_args__ = (db.UniqueConstraint('user_id', 'task_id', name='_user_task_uc'),)





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
