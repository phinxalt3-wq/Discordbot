import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
APP_CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
GUILD_CONFIG_PATH = os.path.join(DATA_DIR, "guilds.json")
VOUCHES_PATH = os.path.join(DATA_DIR, "vouches.json")
WARNINGS_PATH = os.path.join(DATA_DIR, "warnings.json")
BLACKLIST_PATH = os.path.join(DATA_DIR, "blacklist.json")
WALLETS_PATH = os.path.join(DATA_DIR, "wallets.json")

def ensure_files():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(GUILD_CONFIG_PATH):
        with open(GUILD_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f)
    if not os.path.exists(VOUCHES_PATH):
        with open(VOUCHES_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f)
    if not os.path.exists(WARNINGS_PATH):
        with open(WARNINGS_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f)
    if not os.path.exists(BLACKLIST_PATH):
        with open(BLACKLIST_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f)
    if not os.path.exists(WALLETS_PATH):
        with open(WALLETS_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f)
    if not os.path.exists(APP_CONFIG_PATH):
        with open(APP_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump({
                "token": "",
                "client_id": "",
                "owner_id": None,
                "defaults": {
                    "payments": ["Crypto"],
                    "coins": {"buy_base_price": 0.0375, "sell_base_price": 0.015},
                    "mfa_prices": {
                        "buy": {"NON": 7.0, "VIP": 8.0, "VIP+": 9.5, "MVP": 11.0, "MVP+": 17.0},
                        "sell": {"NON": 6.0, "VIP": 7.0, "VIP+": 8.5, "MVP": 10.0, "MVP+": 15.0}
                    }
                },
                "images": {"ticket_banner": None, "mfa_banner": None, "coin_banner": None}
            }, f, indent=2)

def load_json(path):
    ensure_files()
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    ensure_files()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_app_config():
    return load_json(APP_CONFIG_PATH)

def save_app_config(cfg):
    save_json(APP_CONFIG_PATH, cfg)

def get_config(guild_id):
    data = load_json(GUILD_CONFIG_PATH)
    app = load_app_config()
    g = str(guild_id)
    if g not in data:
        defaults = app.get("defaults", {})
        data[g] = {
            "owners": [],
            "channels": defaults.get("channels", {"tickets": None, "vouches": None, "logs": None, "announcements": None}),
            "staff_role": None,
            "payments": defaults.get("payments", ["Crypto"]),
            "coins": defaults.get("coins", {"buy_base_price": 0.0375, "sell_base_price": 0.015}),
            "mfa_prices": defaults.get("mfa_prices", {
                "buy": {"NON": 7.0, "VIP": 8.0, "VIP+": 9.5, "MVP": 11.0, "MVP+": 17.0},
                "sell": {"NON": 6.0, "VIP": 7.0, "VIP+": 8.5, "MVP": 10.0, "MVP+": 15.0}
            }),
            "ticket_categories": defaults.get("ticket_categories", {}),
            "ticket_settings": defaults.get("ticket_settings", {}),
            "embed_settings": defaults.get("embed_settings", {}),
            "images": app.get("images", {"ticket_banner": None, "mfa_banner": None, "coin_banner": None})
        }
        save_json(GUILD_CONFIG_PATH, data)
    
    # Migrate old mfa_prices structure to new nested structure
    cfg = data[g]
    if "mfa_prices" in cfg:
        mfa_prices = cfg["mfa_prices"]
        # Check if it's the old flat structure (has direct rank keys)
        if isinstance(mfa_prices, dict) and "buy" not in mfa_prices and "sell" not in mfa_prices:
            # Old structure detected - migrate it
            old_prices = mfa_prices.copy()
            # Use old prices as buy prices, and calculate sell prices (90% of buy)
            buy_prices = old_prices.copy()
            sell_prices = {rank: price * 0.9 for rank, price in old_prices.items()}
            cfg["mfa_prices"] = {
                "buy": buy_prices,
                "sell": sell_prices
            }
            data[g] = cfg
            save_json(GUILD_CONFIG_PATH, data)
    
    return data[g]

def set_config(guild_id, cfg):
    data = load_json(GUILD_CONFIG_PATH)
    data[str(guild_id)] = cfg
    save_json(GUILD_CONFIG_PATH, data)

def add_owner(guild_id, user_id):
    cfg = get_config(guild_id)
    if user_id not in cfg["owners"]:
        cfg["owners"].append(user_id)
        set_config(guild_id, cfg)

def set_staff_role(guild_id, role_id):
    cfg = get_config(guild_id)
    cfg["staff_role"] = role_id
    set_config(guild_id, cfg)

def set_images(guild_id, ticket_banner=None, mfa_banner=None, coin_banner=None):
    cfg = get_config(guild_id)
    if ticket_banner is not None:
        cfg["images"]["ticket_banner"] = ticket_banner
    if mfa_banner is not None:
        cfg["images"]["mfa_banner"] = mfa_banner
    if coin_banner is not None:
        cfg["images"]["coin_banner"] = coin_banner
    set_config(guild_id, cfg)

def set_defaults(payments=None, coins=None, mfa_prices=None):
    app = load_app_config()
    if payments is not None:
        app["defaults"]["payments"] = payments
    if coins is not None:
        app["defaults"]["coins"] = coins
    if mfa_prices is not None:
        app["defaults"]["mfa_prices"] = mfa_prices
    save_app_config(app)

def record_vouch(guild_id, seller_id, rating):
    """Legacy function - kept for compatibility"""
    record_vouch_full(guild_id, seller_id, None, "", 0.0, "", rating, 0, None)

def record_vouch_full(guild_id, seller_id, vouched_by_id, product, value, review, rating, vouch_number, timestamp):
    """Record a vouch with full details"""
    v = load_json(VOUCHES_PATH)
    g = str(guild_id)
    s = str(seller_id)
    
    if g not in v:
        v[g] = {}
    if s not in v[g]:
        v[g][s] = {"count": 0, "sum_rating": 0, "vouches": []}
    
    # Keep ratings for stats
    v[g][s]["count"] += 1
    v[g][s]["sum_rating"] += rating
    
    # Store full vouch data
    vouch_data = {
        "vouch_number": vouch_number,
        "vouched_by_id": vouched_by_id,
        "product": product,
        "value": value,
        "review": review,
        "rating": rating,
        "timestamp": timestamp or datetime.utcnow().isoformat()
    }
    v[g][s]["vouches"].append(vouch_data)
    
    save_json(VOUCHES_PATH, v)

def get_vouch_count(guild_id, seller_id):
    """Get the number of vouches for a seller"""
    v = load_json(VOUCHES_PATH)
    g = str(guild_id)
    s = str(seller_id)
    if g not in v or s not in v[g]:
        return 0
    return len(v[g][s].get("vouches", []))

def get_all_vouches(guild_id):
    """Get all vouches for a guild (flattened list)"""
    v = load_json(VOUCHES_PATH)
    g = str(guild_id)
    if g not in v:
        return []
    
    all_vouches = []
    for seller_id, seller_data in v[g].items():
        vouches = seller_data.get("vouches", [])
        for vouch in vouches:
            vouch["seller_id"] = int(seller_id)
            all_vouches.append(vouch)
    
    return all_vouches

def get_vouch_stats(guild_id, seller_id):
    """Get vouch statistics (legacy - kept for compatibility)"""
    v = load_json(VOUCHES_PATH)
    g = str(guild_id)
    s = str(seller_id)
    if g in v and s in v[g]:
        d = v[g][s]
        avg = round(d["sum_rating"] / d["count"], 2) if d["count"] else 0
        return d["count"], avg
    return 0, 0.0

# Warning system
def add_warning(guild_id, user_id, warned_by_id, reason):
    """Add a warning to a user"""
    w = load_json(WARNINGS_PATH)
    g = str(guild_id)
    u = str(user_id)
    
    if g not in w:
        w[g] = {}
    if u not in w[g]:
        w[g][u] = []
    
    warning = {
        "warned_by_id": warned_by_id,
        "reason": reason,
        "timestamp": datetime.utcnow().isoformat()
    }
    w[g][u].append(warning)
    save_json(WARNINGS_PATH, w)

def get_warnings(guild_id, user_id):
    """Get all warnings for a user"""
    w = load_json(WARNINGS_PATH)
    g = str(guild_id)
    u = str(user_id)
    
    if g not in w or u not in w[g]:
        return []
    return w[g][u]

def get_warning_count(guild_id, user_id):
    """Get warning count for a user"""
    return len(get_warnings(guild_id, user_id))

# Blacklist system
def add_to_blacklist(guild_id, user_id, reason):
    """Add a user to the blacklist"""
    b = load_json(BLACKLIST_PATH)
    g = str(guild_id)
    u = str(user_id)
    
    if g not in b:
        b[g] = {}
    
    b[g][u] = {
        "reason": reason,
        "timestamp": datetime.utcnow().isoformat()
    }
    save_json(BLACKLIST_PATH, b)

def remove_from_blacklist(guild_id, user_id):
    """Remove a user from the blacklist"""
    b = load_json(BLACKLIST_PATH)
    g = str(guild_id)
    u = str(user_id)
    
    if g not in b or u not in b[g]:
        return False
    
    del b[g][u]
    save_json(BLACKLIST_PATH, b)
    return True

def is_blacklisted(guild_id, user_id):
    """Check if a user is blacklisted"""
    b = load_json(BLACKLIST_PATH)
    g = str(guild_id)
    u = str(user_id)
    
    return g in b and u in b[g]

# Wallet storage system
def add_wallet(guild_id, crypto_type, address):
    """Add a crypto wallet address"""
    w = load_json(WALLETS_PATH)
    g = str(guild_id)
    
    if g not in w:
        w[g] = {}
    
    w[g][crypto_type.upper()] = address
    save_json(WALLETS_PATH, w)

def get_wallet(guild_id, crypto_type):
    """Get a crypto wallet address"""
    w = load_json(WALLETS_PATH)
    g = str(guild_id)
    
    if g not in w:
        return None
    
    return w[g].get(crypto_type.upper())

def get_all_wallets(guild_id):
    """Get all wallet addresses for a guild"""
    w = load_json(WALLETS_PATH)
    g = str(guild_id)
    
    if g not in w:
        return {}
    
    return w[g]

def remove_wallet(guild_id, crypto_type):
    """Remove a crypto wallet address"""
    w = load_json(WALLETS_PATH)
    g = str(guild_id)
    
    if g not in w or crypto_type.upper() not in w[g]:
        return False
    
    del w[g][crypto_type.upper()]
    save_json(WALLETS_PATH, w)
    return True
