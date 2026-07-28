import os
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
    ConversationHandler,
    PicklePersistence,
)

import strings
import database
import watermark
import location_options

# Enable logging
is_production = os.getenv("ENV", "").lower() == "production"

log_handlers = [logging.StreamHandler()]
if not is_production:
    log_handlers.append(logging.FileHandler("bot_debug.log", encoding='utf-8'))

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=log_handlers
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
CHANNEL_ID = os.getenv("CHANNEL_ID")
# Channel username for subscription check (without @)
SUBSCRIPTION_CHANNEL = os.getenv("SUBSCRIPTION_CHANNEL", "meznagna_26")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set!")

# ─── Conversation States ───────────────────────────────────────────────────────
(
    CHOOSING_ROLE,
    OWNER_TITLE,
    OWNER_CATEGORY,
    OWNER_CITY,
    OWNER_PRICE,
    OWNER_PHOTO,
    OWNER_CONTACT,
    OWNER_PAYMENT,
    SEEKER_MENU,
    SEEKER_CITY,
    SEARCH_QUERY,
    ADMIN_BROADCAST,
    OWNER_MENU,
    SEEKER_CATEGORY,
    SEEKER_LOOKING_FOR_DESC,
    SEEKER_LOOKING_FOR_CONTACT,
    LOOKING_FOR_PAYMENT,
    SEEKER_LOOKING_FOR_PURPOSE,
    SEEKER_ALERT_CATEGORY,
    SEEKER_ALERT_CITY,
    SEEKER_ALERT_NEIGHBORHOOD,
    OWNER_LOOKING_FOR_DATE,
) = range(22)


# ─── Subscription Check ────────────────────────────────────────────────────────

async def is_subscribed(bot, user_id: int) -> bool:
    """Return True if the user is a member of the subscription channel."""
    try:
        member = await bot.get_chat_member(chat_id=f"@{SUBSCRIPTION_CHANNEL}", user_id=user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception as e:
        logger.warning(f"Could not check subscription for {user_id}: {e}")
        # If we can't check (e.g. bot not in channel), allow through
        return True


async def send_subscribe_prompt(update: Update):
    """Send the subscription prompt with a join + verify button."""
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 ቻናሉን ይቀላቀሉ (Join Channel)", url=strings.SUBSCRIBE_CHANNEL_URL)],
        [InlineKeyboardButton(strings.SUBSCRIBE_BTN, callback_data="check_subscription")],
    ])
    await update.message.reply_text(
        strings.SUBSCRIBE_PROMPT,
        reply_markup=keyboard,
        parse_mode='HTML'
    )


# ─── Keyboards ────────────────────────────────────────────────────────────────

def get_main_keyboard():
    keyboard = [
        [strings.ROLE_SELLER, strings.ROLE_LANDLORD],
        [strings.ROLE_BUYER, strings.ROLE_RENTER],
        [strings.ROLE_SERVICE_PROVIDER, strings.ROLE_SERVICE_SEEKER],
        [strings.HELP_BTN]
    ]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)


def get_photo_keyboard():
    """Keyboard shown while user is uploading photos."""
    return ReplyKeyboardMarkup(
        [[strings.DONE_PHOTOS_BTN], [strings.SKIP], [strings.CANCEL]],
        resize_keyboard=True
    )


# ─── Start & Cancel ───────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Received start command from {update.effective_user.id}")
    user = update.effective_user
    database.add_user(user.id, user.username)

    if user.id in ADMIN_IDS:
        database.add_user(user.id, user.username, role='admin')
        await update.message.reply_text(strings.ADMIN_TITLE)

    # Subscription check (skip for admins)
    if user.id not in ADMIN_IDS:
        subscribed = await is_subscribed(context.bot, user.id)
        if not subscribed:
            await send_subscribe_prompt(update)
            return CHOOSING_ROLE

    await update.message.reply_text(
        strings.WELCOME_MSG,
        reply_markup=get_main_keyboard(),
        parse_mode='HTML'
    )
    return CHOOSING_ROLE


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        strings.CANCEL_MSG, reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def timeout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Called when a conversation times out due to inactivity."""
    if update and update.effective_message:
        await update.effective_message.reply_text(
            strings.TIMEOUT_MSG, reply_markup=get_main_keyboard()
        )
    return ConversationHandler.END


# ─── Subscription Callback ────────────────────────────────────────────────────

async def handle_check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the 'I joined the channel' button."""
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    subscribed = await is_subscribed(context.bot, user.id)
    if subscribed:
        await query.edit_message_text(strings.SUBSCRIBED_OK, parse_mode='HTML')
        # Send main keyboard
        await context.bot.send_message(
            chat_id=user.id,
            text=strings.WELCOME_MSG,
            reply_markup=get_main_keyboard(),
            parse_mode='HTML'
        )
    else:
        await query.edit_message_text(strings.NOT_SUBSCRIBED_MSG, parse_mode='HTML',
                                      reply_markup=InlineKeyboardMarkup([
                                          [InlineKeyboardButton("📢 ቻናሉን ይቀላቀሉ", url=strings.SUBSCRIBE_CHANNEL_URL)],
                                          [InlineKeyboardButton(strings.SUBSCRIBE_BTN, callback_data="check_subscription")],
                                      ]))


# ─── Location helpers ─────────────────────────────────────────────────────────

def parse_city_and_location(value: str):
    raw = (value or "").strip()
    if not raw:
        return "", ""

    for sep in [" - ", " -", "- ", " / ", "/", ",", ";"]:
        if sep in raw:
            parts = [part.strip() for part in raw.split(sep, 1)]
            if len(parts) == 2:
                return parts[0], parts[1]

    return raw, ""


# ─── Owner Flow ───────────────────────────────────────────────────────────────

async def owner_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role_text = update.message.text
    if role_text == strings.ROLE_SERVICE_PROVIDER:
        context.user_data["listing_type"] = 'service'
        context.user_data["sub_role"] = strings.ROLE_SERVICE_PROVIDER
    elif role_text == strings.ROLE_SELLER:
        context.user_data["listing_type"] = 'property'
        context.user_data["sub_role"] = strings.ROLE_SELLER
    else:  # ROLE_LANDLORD
        context.user_data["listing_type"] = 'property'
        context.user_data["sub_role"] = strings.ROLE_LANDLORD

    keyboard = [[strings.OWNER_ADD_NEW], [strings.OWNER_MANAGE], [strings.OWNER_VIEW_LOOKING_FOR], [strings.BACK]]
    await update.message.reply_text(
        strings.OWNER_MENU_MSG, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return OWNER_MENU

async def owner_view_looking_for(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["in_looking_for_search"] = True
    context.user_data["in_looking_for_post"] = False
    context.user_data["seeker_listing_type"] = context.user_data.get("listing_type", "property")
    context.user_data["seeker_property_purpose"] = None
    return await seeker_ask_category(update, context)


async def owner_add_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show category selection keyboard based on the role chosen on the home screen."""
    listing_type = context.user_data.get("listing_type", "property")

    if listing_type == "service":
        categories = [
            [strings.SERVICE_CATEGORY_HOUSE],
            [strings.SERVICE_CATEGORY_VEHICLE],
            [strings.SERVICE_CATEGORY_ELECTRONICS],
            [strings.SERVICE_CATEGORY_COSMETICS],
        ]
    else:
        categories = [
            [strings.CATEGORY_HOUSE],
            [strings.CATEGORY_VEHICLE],
            [strings.CATEGORY_FURNITURE],
            [strings.CATEGORY_ELECTRONICS],
            [strings.CATEGORY_COSMETICS],
        ]
    categories.append([strings.CANCEL])

    await update.message.reply_text(
        strings.OWNER_ASK_CATEGORY,
        reply_markup=ReplyKeyboardMarkup(categories, resize_keyboard=True, one_time_keyboard=True)
    )
    return OWNER_CATEGORY


async def owner_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save chosen category then ask for the listing description."""
    context.user_data["category"] = update.message.text
    await update.message.reply_text(
        strings.OWNER_START,
        reply_markup=ReplyKeyboardMarkup([[strings.CANCEL]], resize_keyboard=True)
    )
    return OWNER_TITLE


async def owner_manage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    listings = database.get_listings_by_owner(user_id)

    if not listings:
        await update.message.reply_text(strings.OWNER_NO_LISTINGS)
        return OWNER_MENU

    context.user_data['current_listings'] = listings
    context.user_data['is_for_owner'] = True
    await send_listing_page(update, context, 0)
    return OWNER_MENU

async def seeker_manage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    listings = database.get_listings_by_owner(user_id)

    if not listings:
        await update.message.reply_text(strings.OWNER_NO_LISTINGS) # Reusing string
        return SEEKER_MENU

    context.user_data['current_listings'] = listings
    context.user_data['is_for_owner'] = True
    await send_listing_page(update, context, 0)
    return SEEKER_MENU

async def seeker_manage_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    alerts = database.get_alerts_by_user(user_id)
    if not alerts:
        await update.message.reply_text(strings.ALERT_LIST_EMPTY)
        return SEEKER_MENU
    
    for alert in alerts:
        a_id, a_tgid, a_cat, a_city, a_neigh, a_purp, a_date = alert
        
        purpose_am = {"buy": "ግዢ (Buy)", "rent": "ኪራይ (Rent)", "service": "አገልግሎት (Service)"}.get(a_purp or "", "ያልተገለጸ (Any)")
        cat = a_cat or "ሁሉም (All)"
        loc = f"{a_city or 'ሁሉም'} - {a_neigh or 'ሁሉም'}"
        
        text = strings.ALERT_LIST_ITEM.format(purpose=purpose_am, category=cat, location=loc, date=a_date)
        keyboard = [[InlineKeyboardButton(strings.ALERT_DELETE_BTN, callback_data=f"deletealert_{a_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, parse_mode='HTML', reply_markup=reply_markup)
    return SEEKER_MENU


async def owner_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    category_prefix = context.user_data.get("category", "")
    if category_prefix:
        context.user_data["title"] = f"{category_prefix} - {update.message.text}"
    else:
        context.user_data["title"] = update.message.text
    # Ask city — pass no pre-selected city yet
    context.user_data.pop("city", None)
    keyboard = ReplyKeyboardMarkup(location_options.get_city_keyboard(), resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(strings.OWNER_ASK_CITY, reply_markup=keyboard)
    return OWNER_CITY


async def owner_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected_value = update.message.text.strip()
    city = context.user_data.get("city")

    if not city:
        if selected_value not in location_options.CITY_OPTIONS:
            await update.message.reply_text(
                strings.OWNER_ASK_CITY,
                reply_markup=ReplyKeyboardMarkup(location_options.get_city_keyboard(), resize_keyboard=True, one_time_keyboard=True),
            )
            return OWNER_CITY

        context.user_data["city"] = selected_value
        neighborhood_keyboard = location_options.get_neighborhood_keyboard(selected_value)
        keyboard = ReplyKeyboardMarkup(neighborhood_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(strings.OWNER_ASK_LOCATION, reply_markup=keyboard)
        return OWNER_CITY

    # Now picking neighborhood
    city_value = context.user_data["city"]
    valid_neighborhoods = location_options.get_neighborhoods_for_city(city_value)
    if selected_value not in valid_neighborhoods:
        neighborhood_keyboard = location_options.get_neighborhood_keyboard(city_value)
        keyboard = ReplyKeyboardMarkup(neighborhood_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(strings.OWNER_ASK_LOCATION, reply_markup=keyboard)
        return OWNER_CITY

    context.user_data["neighborhood"] = selected_value
    context.user_data["location"] = location_options.build_location_string(city_value, selected_value)
    await update.message.reply_text(
        strings.OWNER_ASK_PRICE,
        reply_markup=ReplyKeyboardMarkup([[strings.CANCEL]], resize_keyboard=True)
    )
    return OWNER_PRICE


async def owner_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import re
    price_text = update.message.text.strip()
    if not price_text:
        await update.message.reply_text(strings.PRICE_INVALID)
        return OWNER_PRICE

    # Try to extract a numeric value; if none, accept the text as-is (descriptive price)
    cleaned = re.sub(r'[^\d.]', '', price_text.replace(',', ''))
    if cleaned:
        try:
            price_val = float(cleaned)
            if price_val <= 0:
                raise ValueError
            context.user_data["price"] = price_text  # store original text
        except (ValueError, TypeError):
            await update.message.reply_text(strings.PRICE_INVALID)
            return OWNER_PRICE
    else:
        # Descriptive price like "ሶስት ሺ ብር" — accept it
        if len(price_text) < 2:
            await update.message.reply_text(strings.PRICE_INVALID)
            return OWNER_PRICE
        context.user_data["price"] = price_text

    # Reset photo list and show multi-photo prompt
    context.user_data["photos"] = []
    await update.message.reply_text(
        strings.OWNER_ASK_PHOTO,
        reply_markup=get_photo_keyboard(),
        parse_mode='HTML'
    )
    return OWNER_PHOTO


def _looks_like_phone_number(text: str) -> bool:
    import re
    if not text:
        return False
    cleaned = re.sub(r'[^0-9+]', '', text)
    return bool(re.search(r'\d{7,}', cleaned))


async def owner_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming photos — keep collecting until user presses 'Finished'."""
    if "photos" not in context.user_data:
        context.user_data["photos"] = []

    if update.message.photo:
        try:
            photo_file = await update.message.photo[-1].get_file()
            photo_bytes = await photo_file.download_as_bytearray()
            watermarked = watermark.apply_watermark(bytes(photo_bytes))
            sent = await update.message.reply_photo(photo=watermarked, caption="✅ ፎቶ ተቀብሏል (watermarked)")
            photo_id = sent.photo[-1].file_id
        except Exception as e:
            logger.warning(f"Watermark failed, using original: {e}")
            photo_id = update.message.photo[-1].file_id

        context.user_data["photos"].append(photo_id)
        count = len(context.user_data["photos"])
        await update.message.reply_text(
            strings.PHOTO_ADDED_MSG.format(count=count),
            reply_markup=get_photo_keyboard(),
            parse_mode='HTML'
        )
        return OWNER_PHOTO

    # Text received while in photo state
    return await owner_photo_text(update, context)


async def owner_photo_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages in the photo upload state."""
    if update.message.contact:
        context.user_data["contact"] = update.message.contact.phone_number
        return await owner_contact(update, context)

    text = update.message.text.strip() if update.message.text else ""

    if text in (strings.SKIP, "/skip", "ዝለል"):
        return await owner_skip_photo(update, context)

    if text in (strings.DONE, strings.DONE_PHOTOS_BTN, "📸 ፎቶ መጫን ጨርሻለሁ"):
        return await owner_done_photo(update, context)

    if _looks_like_phone_number(text):
        return await owner_contact(update, context)

    await update.message.reply_text(
        strings.OWNER_ASK_PHOTO,
        reply_markup=get_photo_keyboard(),
        parse_mode='HTML'
    )
    return OWNER_PHOTO


async def owner_skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["photos"] = []
    await update.message.reply_text(
        strings.OWNER_ASK_CONTACT,
        reply_markup=ReplyKeyboardMarkup([[strings.CANCEL]], resize_keyboard=True)
    )
    return OWNER_CONTACT


async def owner_done_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "photos" not in context.user_data or not context.user_data["photos"]:
        context.user_data["photos"] = []

    await update.message.reply_text(
        strings.OWNER_ASK_CONTACT,
        reply_markup=ReplyKeyboardMarkup([[strings.CANCEL]], resize_keyboard=True)
    )
    return OWNER_CONTACT


async def owner_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact:
        context.user_data["contact"] = update.message.contact.phone_number
    else:
        context.user_data["contact"] = update.message.text

    user_id = update.effective_user.id

    # Fixed 50 birr fee
    fee = strings.FIXED_FEE
    context.user_data["fee"] = fee

    # Join photo IDs with comma
    photos_str = ",".join(context.user_data.get("photos", [])) if context.user_data.get("photos") else None

    # Determine property purpose for property listings (sell vs rent)
    property_purpose = None
    if context.user_data.get("listing_type") == 'property':
        sub = context.user_data.get("sub_role", "")
        if sub == strings.ROLE_SELLER:
            property_purpose = 'sell'
        elif sub == strings.ROLE_LANDLORD:
            property_purpose = 'rent'

    listing_id = database.add_listing(
        user_id,
        context.user_data["title"],
        context.user_data["location"],
        context.user_data["price"],
        photos_str,
        context.user_data["contact"],
        fee_amount=fee,
        listing_type=context.user_data.get("listing_type", "property"),
        property_purpose=property_purpose,
    )
    context.user_data["listing_id"] = listing_id

    payment_prompt = (
        strings.OWNER_ASK_PAYMENT_SERVICE
        if context.user_data.get("listing_type") == "service"
        else strings.OWNER_ASK_PAYMENT_PROPERTY
    )
    try:
        await update.message.reply_text(
            payment_prompt,
            reply_markup=ReplyKeyboardMarkup([[strings.CANCEL]], resize_keyboard=True),
            parse_mode='HTML'
        )
    except BadRequest as e:
        logger.error(f"BadRequest sending payment prompt; falling back to plain text. error={e}")
        await update.message.reply_text(
            payment_prompt,
            reply_markup=ReplyKeyboardMarkup([[strings.CANCEL]], resize_keyboard=True),
            parse_mode=None
        )
    return OWNER_PAYMENT


async def owner_submit_txid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        payment_photo_id = update.message.photo[-1].file_id
        txid = f"photo:{payment_photo_id}"
        display_txid = "[ክፍያ ስክሪንሾት ተልኳል / Screenshot]"
    else:
        payment_photo_id = None
        txid = update.message.text
        display_txid = txid

    listing_id = context.user_data["listing_id"]
    database.update_listing_txid(listing_id, txid)

    # Notify Admin
    owner = update.effective_user.username or update.effective_user.first_name

    listing_type = context.user_data.get("listing_type", "property")
    sub_role = context.user_data.get("sub_role", "")
    if listing_type == "service":
        listing_type_am = "አገልግሎት"
    elif sub_role == strings.ROLE_SELLER:
        listing_type_am = "ሽያጭ"
    elif sub_role == strings.ROLE_LANDLORD:
        listing_type_am = "ኪራይ"
    else:
        listing_type_am = "ያልታወቀ"

    admin_msg = strings.ADMIN_APPROVE_REQ.format(
        owner=owner,
        title=context.user_data["title"],
        city=context.user_data.get("city", "አልተገለጸም"),
        neighborhood=context.user_data.get("neighborhood", "አልተገለጸም"),
        contact=context.user_data["contact"],
        price=context.user_data["price"],
        listing_type_am=listing_type_am,
        txid=display_txid
    )

    keyboard = [
        [
            InlineKeyboardButton(strings.ADMIN_APPROVE, callback_data=f"approve_{listing_id}"),
            InlineKeyboardButton(strings.ADMIN_REJECT, callback_data=f"reject_{listing_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    photo_ids = context.user_data.get("photos", [])

    for admin_id in ADMIN_IDS:
        if payment_photo_id:
            try:
                await context.bot.send_photo(chat_id=admin_id, photo=payment_photo_id, caption="💳 የክፍያ ማረጋገጫ (Payment Proof)")
            except Exception as e:
                logger.error(f"Failed to send payment photo to admin {admin_id}: {e}")
        try:
            if photo_ids:
                if len(photo_ids) == 1:
                    await context.bot.send_photo(chat_id=admin_id, photo=photo_ids[0], caption=admin_msg, reply_markup=reply_markup)
                else:
                    from telegram import InputMediaPhoto
                    media = [InputMediaPhoto(media=photo_ids[0], caption=admin_msg)]
                    for pid in photo_ids[1:]:
                        media.append(InputMediaPhoto(media=pid))
                    await context.bot.send_media_group(chat_id=admin_id, media=media)
                    await context.bot.send_message(chat_id=admin_id, text="መቆጣጠሪያ:", reply_markup=reply_markup)
            else:
                await context.bot.send_message(chat_id=admin_id, text=admin_msg, reply_markup=reply_markup)
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")

    await update.message.reply_text(strings.OWNER_PAYMENT_PENDING, reply_markup=get_main_keyboard())
    return CHOOSING_ROLE


# ─── Seeker Flow ──────────────────────────────────────────────────────────────

async def seeker_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role_text = update.message.text
    if role_text == strings.ROLE_BUYER:
        context.user_data["seeker_listing_type"] = 'property'
        context.user_data["seeker_property_purpose"] = 'sell'
    elif role_text == strings.ROLE_RENTER:
        context.user_data["seeker_listing_type"] = 'property'
        context.user_data["seeker_property_purpose"] = 'rent'
    elif role_text == strings.ROLE_SERVICE_SEEKER:
        context.user_data["seeker_listing_type"] = 'service'
        context.user_data["seeker_property_purpose"] = None
    else:
        context.user_data["seeker_listing_type"] = None
        context.user_data["seeker_property_purpose"] = None

    keyboard = [
        [strings.SEEKER_SEARCH],
        [strings.SEEKER_LOOKING_FOR],
        [strings.SEEKER_MANAGE],
        [strings.SEEKER_CREATE_ALERT, strings.SEEKER_MANAGE_ALERTS],
        [strings.BACK]
    ]
    await update.message.reply_text(
        strings.SEEKER_MENU_MSG, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return SEEKER_MENU


async def seeker_ask_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    listing_type = context.user_data.get("seeker_listing_type", "property")
    if listing_type == "service":
        categories = [
            [strings.SERVICE_CATEGORY_HOUSE],
            [strings.SERVICE_CATEGORY_VEHICLE],
            [strings.SERVICE_CATEGORY_ELECTRONICS],
            [strings.SERVICE_CATEGORY_COSMETICS],
            ["ሁሉም"]
        ]
    else:
        categories = [
            [strings.CATEGORY_HOUSE],
            [strings.CATEGORY_VEHICLE],
            [strings.CATEGORY_FURNITURE],
            [strings.CATEGORY_ELECTRONICS],
            [strings.CATEGORY_COSMETICS],
            ["ሁሉም"]
        ]
    categories.append([strings.CANCEL])

    await update.message.reply_text(
        strings.SEEKER_ASK_CATEGORY,
        reply_markup=ReplyKeyboardMarkup(categories, resize_keyboard=True, one_time_keyboard=True)
    )
    return SEEKER_CATEGORY


async def seeker_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cat = update.message.text
    if "ሁሉም" in cat:
        cat = None
    context.user_data["seeker_category"] = cat
    context.user_data.pop("seeker_city", None)
    context.user_data.pop("seeker_neighborhood", None)
    keyboard = ReplyKeyboardMarkup(location_options.get_city_keyboard(), resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(strings.SEEKER_ASK_CITY, reply_markup=keyboard)
    return SEEKER_CITY


async def view_all_listings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("seeker_city", None)
    context.user_data.pop("seeker_neighborhood", None)
    keyboard = ReplyKeyboardMarkup(location_options.get_city_keyboard(), resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(strings.SEEKER_ASK_CITY, reply_markup=keyboard)
    return SEEKER_CITY


async def seeker_browse_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected_value = update.message.text.strip()
    seeker_city = context.user_data.get("seeker_city")

    if not seeker_city:
        if selected_value not in location_options.CITY_OPTIONS:
            keyboard = ReplyKeyboardMarkup(location_options.get_city_keyboard(), resize_keyboard=True, one_time_keyboard=True)
            await update.message.reply_text(strings.SEEKER_ASK_CITY, reply_markup=keyboard)
            return SEEKER_CITY

        context.user_data["seeker_city"] = selected_value
        neighborhood_keyboard = location_options.get_neighborhood_keyboard(selected_value)
        keyboard = ReplyKeyboardMarkup(neighborhood_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(strings.SEEKER_ASK_SEARCH, reply_markup=keyboard)
        return SEEKER_CITY

    # Neighborhood was selected
    city_value = seeker_city
    valid_neighborhoods = location_options.get_neighborhoods_for_city(city_value)
    if selected_value not in valid_neighborhoods:
        neighborhood_keyboard = location_options.get_neighborhood_keyboard(city_value)
        keyboard = ReplyKeyboardMarkup(neighborhood_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(strings.SEEKER_ASK_SEARCH, reply_markup=keyboard)
        return SEEKER_CITY

    city = seeker_city
    neighborhood = selected_value
    context.user_data.pop("seeker_city", None)
    context.user_data.pop("seeker_neighborhood", None)

    if context.user_data.get("in_looking_for_post"):
        context.user_data["looking_for_city"] = city
        context.user_data["looking_for_neighborhood"] = neighborhood
        await update.message.reply_text(
            strings.SEEKER_ASK_LOOKING_FOR,
            reply_markup=ReplyKeyboardMarkup([[strings.CANCEL]], resize_keyboard=True),
            parse_mode='HTML'
        )
        return SEEKER_LOOKING_FOR_DESC

    if context.user_data.get("in_looking_for_search"):
        # Ask for date filter first
        context.user_data["lf_search_city"] = city
        context.user_data["lf_search_neighborhood"] = neighborhood
        keyboard = [
            [strings.FILTER_24_HOURS],
            [strings.FILTER_7_DAYS],
            [strings.FILTER_ALL_TIME],
        ]
        await update.message.reply_text(
            strings.OWNER_ASK_DATE_FILTER,
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        )
        return OWNER_LOOKING_FOR_DATE

    listings = database.get_listings_by_city(
        city,
        listing_type=context.user_data.get("seeker_listing_type"),
        property_purpose=context.user_data.get("seeker_property_purpose"),
        category=context.user_data.get("seeker_category"),
    )
    if neighborhood and neighborhood != "ሁሉም":
        listings = [
            listing for listing in listings
            if neighborhood in (listing[3] or "")
        ]

    if not listings:
        await update.message.reply_text(strings.SEEKER_NO_MATCH)
        return SEEKER_MENU

    context.user_data['current_listings'] = listings
    context.user_data['is_for_owner'] = False
    await send_listing_page(update, context, 0)
    return SEEKER_MENU


async def search_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("seeker_city", None)
    context.user_data.pop("seeker_neighborhood", None)
    keyboard = ReplyKeyboardMarkup(location_options.get_city_keyboard(), resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(strings.SEEKER_ASK_CITY, reply_markup=keyboard)
    return SEEKER_CITY


async def execute_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    if ',' in query:
        city_query, neighborhood_query = [part.strip() for part in query.split(',', 1)]
    else:
        city_query, neighborhood_query = query, None

    listings = database.search_listings_by_location(
        city_query, neighborhood_query,
        listing_type=context.user_data.get("seeker_listing_type"),
        property_purpose=context.user_data.get("seeker_property_purpose"),
        category=context.user_data.get("seeker_category"),
    )
    if not listings:
        await update.message.reply_text(strings.SEEKER_NO_MATCH)
        return SEEKER_MENU

    context.user_data['current_listings'] = listings
    context.user_data['is_for_owner'] = False
    await send_listing_page(update, context, 0)
    return SEEKER_MENU


# ─── "Looking For" (Seeker post a request) ────────────────────────────────────

async def owner_looking_for_date_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the date filter selection for Looking For listings."""
    from datetime import datetime, timedelta
    text = update.message.text
    city = context.user_data.get("lf_search_city", "")
    neighborhood = context.user_data.get("lf_search_neighborhood", "")

    listings = database.get_listings_by_city(
        city,
        listing_type='looking_for',
        property_purpose=context.user_data.get("seeker_property_purpose"),
        category=context.user_data.get("seeker_category"),
    )
    if neighborhood and neighborhood != "ሁሉም":
        listings = [lst for lst in listings if neighborhood in (lst[3] or "")]

    if text == strings.FILTER_24_HOURS:
        cutoff = datetime.now() - timedelta(days=1)
    elif text == strings.FILTER_7_DAYS:
        cutoff = datetime.now() - timedelta(days=7)
    else:
        cutoff = None

    if cutoff:
        filtered = []
        for lst in listings:
            try:
                created = datetime.strptime(lst[7], "%Y-%m-%d %H:%M:%S")
                if created >= cutoff:
                    filtered.append(lst)
            except Exception:
                filtered.append(lst)
        listings = filtered

    if not listings:
        await update.message.reply_text(strings.SEEKER_NO_MATCH)
        return OWNER_MENU

    context.user_data['current_listings'] = listings
    context.user_data['is_for_owner'] = False
    await send_listing_page(update, context, 0)
    return OWNER_MENU


async def seeker_looking_for_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Seeker clicked 'Looking For' — skip purpose if already known."""
    context.user_data["in_looking_for_post"] = True
    context.user_data["in_looking_for_search"] = False
    
    listing_type = context.user_data.get("seeker_listing_type")
    prop_purpose = context.user_data.get("seeker_property_purpose")
    
    if listing_type == 'service':
        context.user_data["looking_for_purpose"] = 'service'
    elif prop_purpose == 'sell':
        context.user_data["looking_for_purpose"] = 'buy'
    elif prop_purpose == 'rent':
        context.user_data["looking_for_purpose"] = 'rent'
    else:
        context.user_data["looking_for_purpose"] = None
        
    return await seeker_ask_category(update, context)



async def seeker_create_alert_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the Create Alert flow — ask for category."""
    context.user_data["in_create_alert"] = True
    listing_type = context.user_data.get("seeker_listing_type", "property")
    if listing_type == "service":
        categories = [
            [strings.SERVICE_CATEGORY_HOUSE],
            [strings.SERVICE_CATEGORY_VEHICLE],
            [strings.SERVICE_CATEGORY_ELECTRONICS],
            [strings.SERVICE_CATEGORY_COSMETICS],
            ["ሁሉም"]
        ]
    else:
        categories = [
            [strings.CATEGORY_HOUSE],
            [strings.CATEGORY_VEHICLE],
            [strings.CATEGORY_FURNITURE],
            [strings.CATEGORY_ELECTRONICS],
            [strings.CATEGORY_COSMETICS],
            ["ሁሉም"]
        ]
    categories.append([strings.CANCEL])
    await update.message.reply_text(
        strings.SEEKER_ASK_CATEGORY,
        reply_markup=ReplyKeyboardMarkup(categories, resize_keyboard=True, one_time_keyboard=True)
    )
    return SEEKER_ALERT_CATEGORY

async def seeker_alert_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["alert_category"] = text
    keyboard = ReplyKeyboardMarkup(location_options.get_city_keyboard() + [["ሁሉም"]], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(strings.SEEKER_ASK_CITY, reply_markup=keyboard)
    return SEEKER_ALERT_CITY

async def seeker_alert_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["alert_city"] = text
    if text == "ሁሉም":
        # Skip neighborhood
        telegram_id = update.effective_user.id
        database.add_alert(
            telegram_id=telegram_id,
            category=context.user_data.get("alert_category", "ሁሉም"),
            city="ሁሉም",
            neighborhood="ሁሉም",
            property_purpose=context.user_data.get("seeker_property_purpose")
        )
        await update.message.reply_text(strings.SEEKER_ALERT_CREATED, parse_mode='HTML', reply_markup=ReplyKeyboardMarkup([[strings.BACK]], resize_keyboard=True))
        return SEEKER_MENU
    neighborhood_keyboard = location_options.get_neighborhood_keyboard(text)
    keyboard = ReplyKeyboardMarkup(neighborhood_keyboard + [["ሁሉም"]], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(strings.SEEKER_ASK_SEARCH, reply_markup=keyboard)
    return SEEKER_ALERT_NEIGHBORHOOD

async def seeker_alert_neighborhood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    telegram_id = update.effective_user.id
    database.add_alert(
        telegram_id=telegram_id,
        category=context.user_data.get("alert_category", "ሁሉም"),
        city=context.user_data.get("alert_city", "ሁሉም"),
        neighborhood=text,
        property_purpose=context.user_data.get("seeker_property_purpose")
    )
    await update.message.reply_text(strings.SEEKER_ALERT_CREATED, parse_mode='HTML', reply_markup=ReplyKeyboardMarkup([[strings.BACK]], resize_keyboard=True))
    return SEEKER_MENU


async def seeker_looking_for_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save the description/price text and ask for contact."""
    desc = update.message.text.strip()
    if not desc:
        await update.message.reply_text(strings.SEEKER_ASK_LOOKING_FOR, parse_mode='HTML')
        return SEEKER_LOOKING_FOR_DESC
    context.user_data["looking_for_desc"] = desc
    await update.message.reply_text(
        strings.SEEKER_ASK_CONTACT_FOR_LOOKING,
        reply_markup=ReplyKeyboardMarkup([[strings.CANCEL]], resize_keyboard=True)
    )
    return SEEKER_LOOKING_FOR_CONTACT


async def seeker_looking_for_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save contact, create a pending DB listing, then show the 50-birr payment prompt."""
    if update.message.contact:
        contact = update.message.contact.phone_number
    else:
        contact = update.message.text.strip()

    user_id = update.effective_user.id
    desc = context.user_data.get("looking_for_desc", "")
    category = context.user_data.get("seeker_category") or "ሁሉም"

    city = context.user_data.get("looking_for_city", "")
    neighborhood = context.user_data.get("looking_for_neighborhood", "")
    location = f"{city} - {neighborhood}" if neighborhood and neighborhood != "ሁሉም" else city

    # Store in DB as a 'looking_for' listing so admin can approve/reject
    listing_id = database.add_listing(
        user_id,
        title=f"🔎 ፈላጊ — {category}",
        location=location,
        price=desc,           # their budget/description goes in price field
        photo_file_id=None,
        contact_phone=contact,
        fee_amount=strings.FIXED_FEE,
        listing_type='looking_for',
        property_purpose=context.user_data.get("looking_for_purpose"),
    )
    context.user_data["looking_for_listing_id"] = listing_id
    context.user_data["looking_for_contact"] = contact

    # Show 50-birr payment prompt
    try:
        await update.message.reply_text(
            strings.SEEKER_ASK_PAYMENT_LOOKING_FOR,
            reply_markup=ReplyKeyboardMarkup([[strings.CANCEL]], resize_keyboard=True),
            parse_mode='HTML'
        )
    except BadRequest as e:
        logger.error(f"BadRequest sending looking-for payment prompt: {e}")
        await update.message.reply_text(
            strings.SEEKER_ASK_PAYMENT_LOOKING_FOR,
            reply_markup=ReplyKeyboardMarkup([[strings.CANCEL]], resize_keyboard=True),
        )
    return LOOKING_FOR_PAYMENT


async def seeker_looking_for_txid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive payment screenshot/txid and notify admins with Approve/Reject buttons."""
    if update.message.photo:
        payment_photo_id = update.message.photo[-1].file_id
        txid = f"photo:{payment_photo_id}"
        display_txid = "[ክፍያ ስክሪንሾት ተልኳል / Screenshot]"
    else:
        payment_photo_id = None
        txid = update.message.text.strip()
        display_txid = txid

    listing_id = context.user_data.get("looking_for_listing_id")
    if not listing_id:
        await update.message.reply_text("❌ ስህተት ተፈጥሯል። እባክዎን እንደገና ይሞክሩ /start")
        return CHOOSING_ROLE

    database.update_listing_txid(listing_id, txid)

    # Build admin notification
    seeker_name = update.effective_user.username or update.effective_user.first_name
    desc = context.user_data.get("looking_for_desc", "")
    category = context.user_data.get("seeker_category") or "ሁሉም"
    contact = context.user_data.get("looking_for_contact", "")

    purpose_val = context.user_data.get("looking_for_purpose", "")
    purpose_am = {"buy": "ግዢ (Buy)", "rent": "ኪራይ (Rent)", "service": "አገልግሎት (Service)"}.get(purpose_val, purpose_val)

    admin_msg = strings.SEEKER_LOOKING_FOR_ADMIN.format(
        seeker=seeker_name,
        category=category,
        city=context.user_data.get("looking_for_city", "አልተገለጸም"),
        neighborhood=context.user_data.get("looking_for_neighborhood", "አልተገለጸም"),
        purpose=purpose_am,
        description=desc,
        contact=contact,
        txid=display_txid,
    )

    approve_reject = InlineKeyboardMarkup([[
        InlineKeyboardButton(strings.ADMIN_APPROVE, callback_data=f"approve_{listing_id}"),
        InlineKeyboardButton(strings.ADMIN_REJECT, callback_data=f"reject_{listing_id}"),
    ]])

    for admin_id in ADMIN_IDS:
        if payment_photo_id:
            try:
                await context.bot.send_photo(
                    chat_id=admin_id,
                    photo=payment_photo_id,
                    caption="💳 የክፍያ ማረጋገጫ — ፈላጊ ጥያቄ (Payment Proof)"
                )
            except Exception as e:
                logger.error(f"Failed to send looking-for payment photo to admin {admin_id}: {e}")
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=admin_msg,
                reply_markup=approve_reject,
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id} about looking-for: {e}")

    await update.message.reply_text(
        strings.SEEKER_LOOKING_FOR_SENT,
        reply_markup=get_main_keyboard(),
        parse_mode='HTML'
    )
    return CHOOSING_ROLE


# ─── Listing Display ──────────────────────────────────────────────────────────

async def send_listing_page(update: Update, context: ContextTypes.DEFAULT_TYPE, current_idx: int):
    listings = context.user_data.get('current_listings', [])

    if not listings:
        listings = database.get_all_listings()
        context.user_data['current_listings'] = listings
        context.user_data['is_for_owner'] = False
        logger.info(f"DEBUG: Reloaded {len(listings)} listings from DB for pagination")

    if not listings or current_idx < 0 or current_idx >= len(listings):
        return

    for_owner = context.user_data.get('is_for_owner', False)
    is_admin = update.effective_user.id in ADMIN_IDS
    item = listings[current_idx]
    listing_id = item[0]

    from telegram import InputMediaPhoto

    status_msg = ""
    if for_owner or is_admin:
        status_map = {
            'pending': '⏳ Pending',
            'paid': '✅ Active',
            'rented': '🔒 Unlisted',
            'expired': '⏳ Expired',
        }
        status_text = status_map.get(item[8], item[8]) if len(item) > 8 else "Unknown"

        tx_val = item[10] if len(item) > 10 and item[10] else ""
        if tx_val.startswith("photo:"):
            tx_info = "\n🎫 TXID: [ክፍያ ስክሪንሾት (Screenshot)]"
        else:
            tx_info = f"\n🎫 TXID: {tx_val}" if tx_val else ""

        status_msg = f"\n📊 Status: {status_text}{tx_info}"

    page_indicator = f"\n\n📄 {current_idx + 1}/{len(listings)}"

    listing_type_val = item[12] if len(item) > 12 and item[12] else 'property'
    property_purpose_val = item[13] if len(item) > 13 and item[13] else None

    if listing_type_val == 'service':
        listing_type_am = "አገልግሎት"
    elif property_purpose_val == 'sell':
        listing_type_am = "ሽያጭ"
    elif property_purpose_val == 'rent':
        listing_type_am = "ኪራይ"
    else:
        listing_type_am = "ያልታወቀ"

    text = strings.LISTING_TEMPLATE.format(
        title=item[2],
        location=item[3],
        price=item[4],
        contact=item[6],
        listing_type_am=listing_type_am,
        date=item[7]
    ) + status_msg + page_indicator

    nav_row = []
    if current_idx > 0:
        nav_row.append(InlineKeyboardButton(strings.BTN_PREV, callback_data=f"page_{current_idx-1}"))
    if current_idx < len(listings) - 1:
        nav_row.append(InlineKeyboardButton(strings.BTN_NEXT, callback_data=f"page_{current_idx+1}"))

    keyboard = []
    if nav_row:
        keyboard.append(nav_row)

    if is_admin:
        keyboard.append([InlineKeyboardButton(strings.ADMIN_DELETE, callback_data=f"delete_{item[0]}")])

    if for_owner:
        listing_type = item[12] if len(item) > 12 else 'property'
        if item[8] == 'expired' and listing_type == 'service':
            keyboard.append([InlineKeyboardButton(strings.OWNER_RENEW_BTN, callback_data=f"renew_{item[0]}")])
        elif item[8] != 'rented':
            keyboard.append([InlineKeyboardButton(strings.OWNER_UNLIST_BTN, callback_data=f"unlist_{item[0]}")])
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    photo_ids = item[5].split(",") if item[5] else []

    if is_admin and len(item) > 10 and item[10] and item[10].startswith("photo:"):
        payment_photo = item[10].split(":", 1)[1]
        photo_ids.append(payment_photo)

    chat_id = update.effective_chat.id
    func = context.bot.send_photo
    func_text = context.bot.send_message
    func_media_group = context.bot.send_media_group

    send_args = {"chat_id": chat_id}

    if len(photo_ids) > 1:
        media = [InputMediaPhoto(media=photo_ids[0], caption=text, parse_mode='HTML')]
        for pid in photo_ids[1:]:
            media.append(InputMediaPhoto(media=pid))

        sent_messages = await func_media_group(media=media, **send_args)
        context.user_data['last_media_group_ids'] = [m.message_id for m in sent_messages]

        if keyboard:
            await func_text(text="መቆጣጠሪያ (Controls):", reply_markup=reply_markup, **send_args)
    elif len(photo_ids) == 1:
        context.user_data['last_media_group_ids'] = []
        await func(photo=photo_ids[0], caption=text, reply_markup=reply_markup, parse_mode='HTML', **send_args)
    else:
        context.user_data['last_media_group_ids'] = []
        await func_text(text=text, reply_markup=reply_markup, parse_mode='HTML', **send_args)


# ─── Callbacks ────────────────────────────────────────────────────────────────

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    log_msg = f"DEBUG: Callback query received: {query.data} from {update.effective_user.id}"
    logger.info(log_msg)
    print(log_msg)
    await query.answer()

    # Subscription check
    if query.data == "check_subscription":
        return await handle_check_subscription(update, context)

    if query.data.startswith("page_"):
        idx = int(query.data.split("_")[1])
        try:
            last_media_ids = context.user_data.get('last_media_group_ids', [])
            for mid in last_media_ids:
                try:
                    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=mid)
                except:
                    pass
            context.user_data['last_media_group_ids'] = []

            await query.message.delete()
        except:
            pass
        await send_listing_page(update, context, idx)

    elif query.data.startswith("deletealert_"):
        alert_id = int(query.data.split("_")[1])
        database.delete_alert(alert_id, update.effective_user.id)
        try:
            await query.edit_message_text(strings.ALERT_DELETED_MSG)
        except:
            pass

    elif query.data.startswith("delete_"):
        if update.effective_user.id not in ADMIN_IDS:
            return

        listing_id = query.data.split("_")[1]
        database.delete_listing(listing_id)
        if query.message.photo:
            await query.edit_message_caption(caption=f"{query.message.caption}\n\n❌ {strings.ADMIN_DELETE_CONFIRM}")
        else:
            await query.edit_message_text(text=f"{query.message.text}\n\n❌ {strings.ADMIN_DELETE_CONFIRM}")

    elif query.data.startswith("unlist_"):
        listing_id = int(query.data.split("_")[1])
        listing = database.get_listing_by_id(listing_id)
        if not listing or listing[1] != update.effective_user.id:
            return

        database.unlist_listing(listing_id)
        if query.message.photo:
            await query.edit_message_caption(caption=f"{query.message.caption}\n\n{strings.OWNER_UNLIST_CONFIRM}")
        else:
            await query.edit_message_text(text=f"{query.message.text}\n\n{strings.OWNER_UNLIST_CONFIRM}")

    elif query.data.startswith("renew_"):
        listing_id = int(query.data.split("_")[1])
        listing = database.get_listing_by_id(listing_id)
        if not listing or listing[1] != update.effective_user.id:
            return
        if len(listing) > 12 and listing[12] != 'service':
            return
        database.renew_listing(listing_id)
        context.user_data["listing_id"] = listing_id
        await context.bot.send_message(chat_id=update.effective_chat.id, text=strings.OWNER_RENEW_PROMPT)
        return OWNER_PAYMENT

    elif query.data.startswith("approve_"):
        if update.effective_user.id not in ADMIN_IDS:
            return

        listing_id = int(query.data.split("_")[1])
        database.approve_listing(listing_id)

        listing = database.get_listing_by_id(listing_id)
        if listing:
            owner_id = listing[1]
            listing_type_val = listing[12] if len(listing) > 12 and listing[12] else 'property'

            if listing_type_val == 'looking_for':
                try:
                    await context.bot.send_message(chat_id=owner_id, text=strings.SEEKER_LOOKING_FOR_APPROVED, parse_mode='HTML')
                except:
                    pass

                if CHANNEL_ID:
                    try:
                        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
                        property_purpose_val = listing[13] if len(listing) > 13 and listing[13] else None
                        purpose_am = {"buy": "ግዢ (Buy)", "rent": "ኪራይ (Rent)", "service": "አገልግሎት (Service)"}.get(property_purpose_val or "", "ያልተገለጸ")

                        # listing[2] = title (we used title as description for looking_for)
                        # listing[3] = location (city - neighborhood)
                        # listing[6] = contact
                        loc = listing[3] or ""
                        city_part, neigh_part = loc.split(" - ", 1) if " - " in loc else (loc, "ያልተገለጸ")
                        title_parts = (listing[2] or "").split(" — ", 1)
                        category_part = title_parts[1] if len(title_parts) > 1 else title_parts[0]
                        desc_part = listing[4] or ""  # price field stores description for looking_for

                        post_text = strings.LOOKING_FOR_CHANNEL_POST.format(
                            seeker=str(owner_id),
                            city=city_part.strip(),
                            neighborhood=neigh_part.strip(),
                            purpose=purpose_am,
                            category=category_part.strip(),
                            description=desc_part,
                            contact=listing[6] or "ያልተገለጸ"
                        )

                        bot_username = (await context.bot.get_me()).username
                        bot_link = f"https://t.me/{bot_username}"
                        lf_keyboard = [[InlineKeyboardButton("ወደ ቦቱ ይግቡ (View in Bot)", url=bot_link)]]
                        lf_reply_markup = InlineKeyboardMarkup(lf_keyboard)

                        await context.bot.send_message(chat_id=CHANNEL_ID, text=post_text, parse_mode='HTML', reply_markup=lf_reply_markup)
                    except Exception as e:
                        logger.error(f"Failed to post looking_for to channel: {e}")
            else:
                try:
                    await context.bot.send_message(chat_id=owner_id, text=strings.OWNER_PAYMENT_SUCCESS)
                except:
                    pass

                if CHANNEL_ID:
                    try:
                        from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto

                        property_purpose_val = listing[13] if len(listing) > 13 and listing[13] else None

                        if listing_type_val == 'service':
                            listing_type_am = "አገልግሎት"
                        elif property_purpose_val == 'sell':
                            listing_type_am = "ሽያጭ"
                        elif property_purpose_val == 'rent':
                            listing_type_am = "ኪራይ"
                        else:
                            listing_type_am = "ያልታወቀ"

                        text = strings.LISTING_TEMPLATE.format(
                            title=listing[2],
                            location=listing[3],
                            price=listing[4],
                            contact=listing[6],
                            listing_type_am=listing_type_am,
                            date=listing[7]
                        )

                        bot_username = (await context.bot.get_me()).username
                        bot_link = f"https://t.me/{bot_username}"
                        channel_keyboard = [[InlineKeyboardButton("ወደ ቦቱ ይግቡ (View in Bot)", url=bot_link)]]
                        channel_reply_markup = InlineKeyboardMarkup(channel_keyboard)

                        photo_ids = listing[5].split(",") if listing[5] else []

                        if len(photo_ids) > 1:
                            media = [InputMediaPhoto(media=photo_ids[0], caption=text, parse_mode='HTML')]
                            for pid in photo_ids[1:]:
                                media.append(InputMediaPhoto(media=pid))
                            await context.bot.send_media_group(chat_id=CHANNEL_ID, media=media)
                            await context.bot.send_message(chat_id=CHANNEL_ID, text="በቦቱ ላይ ለማየት (To view in bot):", reply_markup=channel_reply_markup)
                        elif len(photo_ids) == 1:
                            await context.bot.send_photo(chat_id=CHANNEL_ID, photo=photo_ids[0], caption=text, parse_mode='HTML', reply_markup=channel_reply_markup)
                        else:
                            await context.bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode='HTML', reply_markup=channel_reply_markup)

                        # Fire search alerts
                        alert_users = database.get_matching_alerts(
                            category=listing[2] or "",
                            location=listing[3] or "",
                            property_purpose=property_purpose_val
                        )
                        for uid in alert_users:
                            try:
                                await context.bot.send_message(
                                    chat_id=uid,
                                    text=strings.ALERT_NOTIFICATION_MSG.format(title=listing[2]),
                                    parse_mode='HTML'
                                )
                            except Exception as alert_err:
                                logger.warning(f"Could not notify alert user {uid}: {alert_err}")
                    except Exception as e:
                        logger.error(f"Failed to post to channel {CHANNEL_ID}: {e}")

        try:
            await query.edit_message_text(text=f"{query.message.text}\n\n✅ {strings.ADMIN_APPROVE_CONFIRM}")
        except Exception:
            pass

    elif query.data.startswith("reject_"):
        if update.effective_user.id not in ADMIN_IDS:
            return
        listing_id = query.data.split("_")[1]
        listing = database.get_listing_by_id(listing_id)
        if listing:
            owner_id = listing[1]
            try:
                await context.bot.send_message(chat_id=owner_id, text=strings.OWNER_LISTING_REJECTED)
            except Exception as e:
                logger.error(f"Failed to notify owner {owner_id} about rejection: {e}")
        database.delete_listing(listing_id)
        await query.edit_message_text(text=f"{query.message.text}\n\n❌ {strings.CANCEL_MSG}")


# ─── Admin Features ───────────────────────────────────────────────────────────

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text(strings.ADMIN_ONLY)
        return

    users = database.get_all_users()
    total = database.get_total_user_count()
    roles = [u[2] for u in users]
    owners_count = roles.count('owner') + roles.count('admin')
    seekers_count = total - owners_count

    all_listings = database.execute_query("SELECT listing_type, status FROM listings", fetchall=True)
    active_property = sum(1 for r in (all_listings or []) if r[1] == 'paid' and r[0] in ('property', None))
    active_service = sum(1 for r in (all_listings or []) if r[1] == 'paid' and r[0] == 'service')
    active_looking = sum(1 for r in (all_listings or []) if r[1] == 'paid' and r[0] == 'looking_for')
    pending_count = sum(1 for r in (all_listings or []) if r[1] == 'pending')
    total_active = active_property + active_service + active_looking

    await update.message.reply_text(
        strings.ADMIN_STATS.format(
            total=total,
            active=total_active,
            active_property=active_property,
            active_service=active_service,
            active_looking=active_looking,
            pending=pending_count,
            owners=owners_count,
            seekers=seekers_count
        ),
        parse_mode='HTML'
    )


async def admin_pending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View all listings waiting for admin approval."""
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text(strings.ADMIN_ONLY)
        return

    pending_listings = database.get_pending_listings_with_txid()

    if not pending_listings:
        await update.message.reply_text(strings.ADMIN_NO_PENDING)
        return

    await update.message.reply_text(strings.ADMIN_PENDING_TITLE, parse_mode='HTML')

    context.user_data['current_listings'] = pending_listings
    context.user_data['is_for_owner'] = True
    await send_listing_page(update, context, 0)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        strings.HELP_MSG,
        reply_markup=get_main_keyboard(),
        parse_mode='HTML'
    )


async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text(strings.ADMIN_ONLY)
        return ConversationHandler.END

    await update.message.reply_text(strings.ADMIN_BROADCAST_PROMPT, reply_markup=ReplyKeyboardMarkup([[strings.CANCEL]], resize_keyboard=True))
    return ADMIN_BROADCAST


async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return ConversationHandler.END

    msg_text = update.message.text
    if msg_text == strings.CANCEL:
        return await cancel(update, context)

    users = database.get_all_users()
    count = 0
    for user in users:
        try:
            await update.message.copy_message(chat_id=user[0])
            count += 1
        except Exception as e:
            logger.error(f"Failed to send broadcast to {user[0]}: {e}")

    await update.message.reply_text(strings.ADMIN_BROADCAST_DONE.format(count=count), reply_markup=get_main_keyboard())
    return CHOOSING_ROLE


# ─── Health Check ─────────────────────────────────────────────────────────────

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        return


def run_health_check_server():
    port = int(os.getenv("PORT", 7860))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    logger.info(f"Health check server started on port {port}")
    server.serve_forever()


def _normalize_webhook_url(webhook_url: str) -> tuple[str, str]:
    if not webhook_url.startswith("http"):
        webhook_url = f"https://{webhook_url}"

    url_path = f"/{BOT_TOKEN}"
    if not webhook_url.endswith(url_path):
        webhook_url = f"{webhook_url.rstrip('/')}{url_path}"

    return webhook_url, url_path


def _resolve_webhook_url() -> str | None:
    webhook_url = (os.getenv("WEBHOOK_URL") or "").strip()
    if webhook_url:
        return webhook_url
    # Railway injects RAILWAY_PUBLIC_DOMAIN when a public URL is enabled
    railway_domain = (os.getenv("RAILWAY_PUBLIC_DOMAIN") or "").strip()
    if railway_domain:
        return railway_domain
    return None


def _start_webhook(application: Application, port: int) -> None:
    webhook_url = _resolve_webhook_url()
    if not webhook_url:
        raise ValueError(
            "WEBHOOK_URL environment variable is required when BOT_UPDATE_MODE=webhook. "
            "On Railway, enable a public domain (Settings → Networking) or set WEBHOOK_URL "
            "to your app URL (e.g. your-app.up.railway.app)."
        )

    webhook_url, url_path = _normalize_webhook_url(webhook_url)

    logger.info(f"Starting bot in WEBHOOK mode on port {port}...")
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=url_path,
        webhook_url=webhook_url,
        secret_token=os.getenv("WEBHOOK_SECRET") or None,
    )


def _start_polling(application: Application) -> None:
    logger.warning("=" * 60)
    logger.warning("No WEBHOOK_URL found. Starting bot in POLLING mode...")
    logger.warning("WARNING: Polling mode DELETES the production webhook!")
    logger.warning("If your bot is deployed on Railway, it will STOP receiving")
    logger.warning("updates there until you redeploy or manually set webhook.")
    logger.warning("=" * 60)
    threading.Thread(target=run_health_check_server, daemon=True).start()

    logger.info("Bot is now polling for updates...")
    application.run_polling(
        poll_interval=1.0,
        timeout=20,
        bootstrap_retries=5,
        drop_pending_updates=True,
    )


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    database.init_db()

    async def post_init(application: Application):
        me = await application.bot.get_me()
        msg = f"BOT IDENTITY: Bot is running as @{me.username} (ID: {me.id})"
        logger.info(msg)
        print(msg)

        from telegram import BotCommand
        await application.bot.set_my_commands([
            BotCommand("start", "🚀 ማውጫ"),
            BotCommand("help", "ℹ️ መመሪያ"),
            BotCommand("cancel", "❌ አቋርጥ")
        ])

        async def debug_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
            d_msg = f"GLOBAL DEBUG: Received update: {update.to_dict()}"
            logger.info(d_msg)
            print(d_msg)

        application.add_handler(CallbackQueryHandler(debug_all), group=-1)

    persistence_path = os.getenv("PERSISTENCE_PATH", "bot_data.pickle")
    persistence = PicklePersistence(filepath=persistence_path)

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .persistence(persistence)
        .post_init(post_init)
        .connect_timeout(30.0)
        .read_timeout(30.0)
        .write_timeout(30.0)
        .build()
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_ROLE: [
                MessageHandler(filters.Text(strings.ROLE_SELLER), owner_start),
                MessageHandler(filters.Text(strings.ROLE_LANDLORD), owner_start),
                MessageHandler(filters.Text(strings.ROLE_BUYER), seeker_start),
                MessageHandler(filters.Text(strings.ROLE_RENTER), seeker_start),
                MessageHandler(filters.Text(strings.ROLE_SERVICE_PROVIDER), owner_start),
                MessageHandler(filters.Text(strings.ROLE_SERVICE_SEEKER), seeker_start),
                MessageHandler(filters.Text(strings.HELP_BTN), help_command),
                CallbackQueryHandler(handle_callback),
            ],
            OWNER_MENU: [
                MessageHandler(filters.Text(strings.OWNER_ADD_NEW), owner_add_new),
                MessageHandler(filters.Text(strings.OWNER_MANAGE), owner_manage),
                MessageHandler(filters.Text(strings.OWNER_VIEW_LOOKING_FOR), owner_view_looking_for),
                MessageHandler(filters.Text(strings.BACK), start),
                CallbackQueryHandler(handle_callback),
            ],
            OWNER_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Text(strings.CANCEL), owner_category)],
            OWNER_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Text(strings.CANCEL), owner_title)],
            OWNER_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Text(strings.CANCEL), owner_city)],
            OWNER_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Text(strings.CANCEL), owner_price)],
            OWNER_PHOTO: [
                MessageHandler(filters.PHOTO, owner_photo),
                CommandHandler("skip", owner_skip_photo),
                MessageHandler(filters.Text(strings.SKIP), owner_skip_photo),
                MessageHandler(filters.Text(strings.DONE_PHOTOS_BTN), owner_done_photo),
                MessageHandler(filters.Text(strings.DONE), owner_done_photo),
                MessageHandler((filters.TEXT | filters.CONTACT) & ~filters.COMMAND & ~filters.Text(strings.CANCEL), owner_photo_text),
            ],
            OWNER_CONTACT: [MessageHandler((filters.TEXT | filters.CONTACT) & ~filters.COMMAND & ~filters.Text(strings.CANCEL), owner_contact)],
            OWNER_PAYMENT: [MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND & ~filters.Text(strings.CANCEL), owner_submit_txid)],
            # Seeker
            SEEKER_MENU: [
                MessageHandler(filters.Text(strings.SEEKER_SEARCH), seeker_ask_category),
                MessageHandler(filters.Text(strings.SEEKER_LOOKING_FOR), seeker_looking_for_start),
                MessageHandler(filters.Text(strings.SEEKER_MANAGE), seeker_manage),
                MessageHandler(filters.Text(strings.SEEKER_CREATE_ALERT), seeker_create_alert_start),
                MessageHandler(filters.Text(strings.SEEKER_MANAGE_ALERTS), seeker_manage_alerts),
                MessageHandler(filters.Text(strings.BACK), start),
                CallbackQueryHandler(handle_callback),
            ],
            SEEKER_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Text(strings.CANCEL), seeker_category)],
            SEEKER_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Text(strings.CANCEL), seeker_browse_city)],
            SEARCH_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Text(strings.CANCEL), execute_search)],
            ADMIN_BROADCAST: [MessageHandler(filters.ALL & ~filters.COMMAND & ~filters.Text(strings.CANCEL), broadcast_message)],
            # Looking For flow
            SEEKER_LOOKING_FOR_PURPOSE: [
                MessageHandler(filters.ALL, seeker_looking_for_start)
            ],

            SEEKER_ALERT_CATEGORY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Text(strings.CANCEL), seeker_alert_category)
            ],
            SEEKER_ALERT_CITY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Text(strings.CANCEL), seeker_alert_city)
            ],
            SEEKER_ALERT_NEIGHBORHOOD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Text(strings.CANCEL), seeker_alert_neighborhood)
            ],
            OWNER_LOOKING_FOR_DATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Text(strings.CANCEL), owner_looking_for_date_filter)
            ],
            SEEKER_LOOKING_FOR_DESC: [
                MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Text(strings.CANCEL), seeker_looking_for_description)
            ],
            SEEKER_LOOKING_FOR_CONTACT: [
                MessageHandler((filters.TEXT | filters.CONTACT) & ~filters.COMMAND & ~filters.Text(strings.CANCEL), seeker_looking_for_contact)
            ],
            LOOKING_FOR_PAYMENT: [
                MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND & ~filters.Text(strings.CANCEL), seeker_looking_for_txid)
            ],
            # Timeout
            ConversationHandler.TIMEOUT: [MessageHandler(filters.ALL, timeout_handler)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            MessageHandler(filters.Text(strings.CANCEL), cancel),
            CommandHandler("start", start)
        ],
        conversation_timeout=900,  # 15 minutes
        persistent=True,
        name="main_conversation",
        per_message=False,
    )

    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(handle_callback), group=1)
    application.add_handler(CommandHandler("admin", admin_stats))
    application.add_handler(CommandHandler("stats", admin_stats))
    application.add_handler(CommandHandler("admin_pending", admin_pending))
    application.add_handler(CommandHandler("pending", admin_pending))
    application.add_handler(CommandHandler("broadcast", broadcast_start))
    application.add_handler(CommandHandler("help", help_command))

    # Schedule daily listings checks
    job_queue = application.job_queue
    if job_queue:
        from datetime import time, timezone, timedelta
        eat_tz = timezone(timedelta(hours=3))  # East Africa Time (UTC+3)
        async def expire_listings_job(context: ContextTypes.DEFAULT_TYPE):
            database.expire_old_listings()

        job_queue.run_daily(
            expire_listings_job,
            time=time(hour=3, minute=0, tzinfo=eat_tz)
        )

    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.error(msg="Exception while handling an update:", exc_info=context.error)
    application.add_error_handler(error_handler)

    update_mode = (os.getenv("BOT_UPDATE_MODE") or "webhook").strip().lower()
    port = int(os.getenv("PORT", 7860))

    if update_mode == "webhook":
        _start_webhook(application, port)
    elif update_mode == "polling":
        _start_polling(application)
    else:
        raise ValueError(
            f"Invalid BOT_UPDATE_MODE={update_mode!r}. Use 'webhook' or 'polling'."
        )


if __name__ == "__main__":
    main()
