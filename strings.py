# strings.py
# Amharic translations for the Telegram Rental Bot

WELCOME_MSG = (
    "✨ <b>እንኳን በደህና መጡ!</b> ✨\n\n"
    "🏠 ይህ ቦት በኢትዮጵያ ሻጮችን፣ አከራዮችን፣ እና አገልግሎት ሰጪዎችን ከ ገዢዎች፣ ተከራዮች፣ እና አገልግሎት ፈላጊዎች ጋር በቀላሉ ያገናኛል።\n\n"
    "👇 <i>እባክዎን ከታች ካሉት አማራጮች አንዱን ይምረጡ፦</i>\n\n"
    "ተጨማሪ መረጃ t.me/meznagna_26 Telegram Channel ላይ ይመልከቱ ።"
)

# ── Channel subscription ──────────────────────────────────────────────────────
SUBSCRIBE_PROMPT = (
    # "📢 <b>እባክዎን ለቀጠናችን ቻናል ይጠቀሙ!</b>\n\n"
    "📢 <b>እባክዎን ቀጣዩን ቻናል ይጠቀሙ!</b>\n\n"
    "ቦቱን ለመጠቀም <b>@meznagna_26</b> ቻናላችንን ይቀላቀሉ፣ ከዚያ ቀጥለው <b>✅ ተቀላቀልኩ</b> ን ይጫኑ።"
)
SUBSCRIBE_BTN = "✅ ተቀላቀልኩ — ቀጥል"
SUBSCRIBE_CHANNEL_URL = "https://t.me/meznagna_26"
NOT_SUBSCRIBED_MSG = (
    "❌ <b>ቻናሉን እስካልተቀላቀሉ ቦቱ አይሰራም።</b>\n\n"
    "እባክዎን @meznagna_26 ቻናላችንን ይቀላቀሉ ከዚያ <b>✅ ተቀላቀልኩ</b> ን ይጫኑ።"
)
SUBSCRIBED_OK = "✅ አመሰግናለሁ! አሁን ቦቱን መጠቀም ይችላሉ።"

ROLE_OWNER = "ሻጭ/አከራይ/አገልግሎት ሰጪ"
ROLE_SEEKER = "ተከራይ/ገዢ/አገልግሎት ፈላጊ"
# Split roles for clearer buttons
ROLE_SELLER = "🛍️ ሻጭ"
ROLE_LANDLORD = "🔑 አከራይ"
ROLE_BUYER = "🛒 ገዢ"
ROLE_RENTER = "🏠 ተከራይ"
ROLE_SERVICE_PROVIDER = "🛠️ አገልግሎት ሰጪ"
ROLE_SERVICE_SEEKER = "🔍 አገልግሎት ፈላጊ"

# Owner Flow
OWNER_MENU_MSG = "ምን ማድረግ ይፈልጋሉ?"
OWNER_ADD_NEW = "አዲስ ምዝገባ መጀመር"
OWNER_MANAGE = "የተመዘገቡትን ማየት"
OWNER_NO_LISTINGS = "ምንም የተመዘገበ ነገር የሎትም።"
OWNER_UNLIST_BTN = "❌ ዝርዝሩን አጥፋ/አልቋል"
OWNER_UNLIST_CONFIRM = "ዝርዝሩ በተሳካ ሁኔታ ተነስቷል።"

OWNER_START = "እባክዎን የንብረቱን/የአገልግሎቱን አይነት አጭር መግለጫ ይጻፉ (ለምሳሌ፦ ባለ 2 ክፍል ኮንዶሚኒየም፣ የቧንቧ ጥገና፣ ...)"
OWNER_VIEW_LOOKING_FOR = "🔍 የፈላጊዎችን ፍላጎት እይ"

# Category selection
OWNER_ASK_CATEGORY = "📂 እባክዎን ምድቡን ይምረጡ:"
# Property categories
CATEGORY_HOUSE = "🏠 ቤት/መሬት"
CATEGORY_VEHICLE = "🚗 ተሽከርካሪ"
CATEGORY_FURNITURE = "🛋️ የቤት ፅቃ"
CATEGORY_ELECTRONICS = "📱 ኤሌክትሮንክስ"
CATEGORY_COSMETICS = "👗 ፋሽን/ዉበት"
# Service categories
SERVICE_CATEGORY_HOUSE = "🔧 ቤት ነክ አገልግሎቶች"
SERVICE_CATEGORY_VEHICLE = "🚗 ተሽከርካሪ ነክ አገልግሎቶች"
SERVICE_CATEGORY_ELECTRONICS = "📱 ኤሌክትሮንክስ ነክ አገልግሎቶች"
SERVICE_CATEGORY_COSMETICS = "👗 ፋሽን/ዉበት ነክ አገልግሎቶች"

OWNER_ASK_TYPE = 'እባክዎን ከሚከተሉት አማራጮች አንዱን ይምረጡ'
LISTING_SERVICE = "ሻጭ/አከራይ"
LISTING_PROPERTY = "አገልግሎት ሰጪ"

OWNER_ASK_CITY = "ንብረቱ/አገልግሎቱ በየትኛው ከተማ ይገኛል? ከታች ካለው ዝርዝር ይምረጡ።"
OWNER_ASK_LOCATION = "ሰፈሩ/አካባቢው የት ነው? ከታች ካለው ዝርዝር ይምረጡ።"
OWNER_ASK_PRICE = "ዋጋዉ ስንት ነው? (በቁጥር ወይም በቃላት ይጻፉ ― ለምሳሌ፦ 3500 ወይም «ሶስት ሺ አምስት መቶ ብር»)"

# ── Photo Upload ──────────────────────────────────────────────────────────────
OWNER_ASK_PHOTO = (
    "📷 <b>እባክዎን የንብረቱን/የአገልግሎቱን ፎቶ ይላኩ።</b>\n\n"
    "• ፎቶዎችን አንድ በ አንድ ይላኩ።\n"
    "• ሁሉም ፎቶዎች ሲያልቁ <b>📸 ፎቶ መጫን ጨርሻለሁ</b> ን ይጫኑ።\n"
    "• ፎቶ ከሌለዎት /skip ይጫኑ ወይም 'ዝለል' ይጻፉ።"
)
PHOTO_ADDED_MSG = "✅ ፎቶ {count} ተቀብሏል! ተጨማሪ ፎቶ ከኖረ ይላኩ፣ ካለቀ 📸 <b>ፎቶ መጫን ጨርሻለሁ</b> ን ይጫኑ።"
DONE_PHOTOS_BTN = "📸 ፎቶ መጫን ጨርሻለሁ"

PHOTO_UPLOADED = "ፎቶ ተልኳል።"
DONE = "ጨርሻለሁ"
OWNER_ASK_CONTACT = "እባክዎን ስልክ ቁጥርዎን ያስገቡ"

# Fixed fee = 50 birr (no percentage)
FIXED_FEE = 50

OWNER_ASK_PAYMENT_SERVICE = (
    "🙏 <b>ምዝገባው ሊጠናቀቅ ጥቂት ቀርቶታል!</b>\n\n"
    "በቦቱ ላይ ሆኖ ለፈላጊዎች እንዲታይ የአገልግሎት ምዝገባ ክፍያ <b>50 ብር</b> ብቻ ይከፍሉ።\n\n"
    "💰 <b>የክፍያ መጠን፦ 50 ብር</b>\n"
    "⏳ <b>ዝርዝሩ ለ30 ቀናት ያህል ብቻ ይቆያል።</b>\n"
    "👤 <b>ስም፦ ሳምሶን ማሬ</b>\n"
    "   <b>የኢትዮጵያ ንግድ ባንክ አካዉንት ቁጥር፦ 1000174738533</b>\n\n"
    "👇 <i>ክፍያውን ከፈጸሙ በኋላ፣ ከኢትዮጵያ ንግድ ባንክ የደረስዎትን የክፍያ ስክሪንሾት (Screenshot) ወይም የትራንዛክሽን ቁጥር (Transaction ID) እባክዎን እዚህ ይላኩ፦</i>"
)
OWNER_ASK_PAYMENT_PROPERTY = (
    "🙏 <b>ምዝገባው ሊጠናቀቅ ጥቂት ቀርቶታል!</b>\n\n"
    "በቦቱ ላይ ሆኖ ለፈላጊዎች እንዲታይ የምዝገባ ክፍያ <b>50 ብር</b> ብቻ ይከፍሉ።\n\n"
    "💰 <b>የክፍያ መጠን፦ 50 ብር</b>\n"
    "👤 <b>ስም፦ ሳምሶን ማሬ</b>\n"
    "   <b>የኢትዮጵያ ንግድ ባንክ አካዉንት ቁጥር፦ 1000174738533</b>\n\n"
    "👇 <i>ክፍያውን ከፈጸሙ በኋላ፣ ከኢትዮጵያ ንግድ ባንክ የደረስዎትን የክፍያ ስክሪንሾት (Screenshot) ወይም የትራንዛክሽን ቁጥር (Transaction ID) እባክዎን እዚህ ይላኩ፦</i>"
)
OWNER_RENEW_BTN = "🔄 እንደገና ይከፈሉ"
OWNER_RENEW_PROMPT = "ዝርዝሩ ከ30 ቀናት በኋላ እንዲቀጥል እባክዎን በድጋግሚ ክፍያ ይላኩ (50 ብር)። የክፍያ ስክሪንሾት ወይም TXID ይላኩ፦"
PAYMENT_GUIDE = "እባክዎን ከኢትዮጵያ ንግድ ባንክ የደረስዎትን የክፍያ ስክሪንሾት (Screenshot) ወይም የትራንዛክሽን ቁጥር (Transaction ID) በትክክል ያስገቡ።"
OWNER_PAYMENT_PENDING = "ክፍያዎ በተሳካ ሁኔታ ተመዝግቧል! ✅ አስተዳዳሪው ሲያጸድቀው ዝርዝርዎ በቦቱ ላይ ይወጣል። እናመሰግናለን።"
OWNER_PAYMENT_SUCCESS = "እንኳን ደስ አለዎት! 🎉 ዝርዝርዎ በአስተዳዳሪው ጸድቆ ለፈላጊዎች ክፍት ሆኗል።"
OWNER_LISTING_REJECTED = "❌ ዝርዝርዎ አልተፈቀደም። ምክንያቱን ለማወቅ እባክዎን በ 0985605005 ይደውሉ።"
OWNER_SUCCESS = "በተሳካ ሁኔታ ተመዝግቧል! ✅"

# Seeker Flow
SEEKER_MENU_MSG = "ምን ማድረግ ይፈልጋሉ?"
SEEKER_SEARCH = "🔍 በከተማ, ሰፈር ፈልግ"
# SEEKER_LOOKING_FOR = "🔎 እየፈለኩትን ይላኩ (Looking For)"
SEEKER_LOOKING_FOR = "🔎 ፍላጎቶን ይላኩ"
SEEKER_MANAGE = "📝 የኔን ፍላጎቶች አስተዳድር"
SEEKER_CREATE_ALERT = "🔔 ማሳወቂያ ፍጠር"
SEEKER_MANAGE_ALERTS = "🔕 ማሳወቂያዎችን ሰርዝ"
SEEKER_VIEW_ALL = "ሁሉንም ዝርዝሮች እይ"
SEEKER_ASK_CATEGORY = "📂 እባክዎን የሚፈልጉትን ምድብ ይምረጡ:"
SEEKER_ASK_SEARCH = "የሚፈልጉትን ሰፈር ከታች ካለው ዝርዝር ይምረጡ።"
SEEKER_ASK_CITY = "📍 የሚፈልጉትን ከተማ ከታች ካለው ዝርዝር ይምረጡ።"
SEEKER_NO_LISTINGS = "ምንም የተመዘገበ መረጃ አልተገኘም።"
SEEKER_NO_MATCH = "በዚህ አካባቢ የተመዘገበ መረጃ አልተገኘም።"

# Looking For flow
SEEKER_ASK_LOOKING_FOR = (
    "🔎 <b>ፍላጎቶን ይግለጹ:</b>\n\n"
    "• ምን ዓይነት ንብረት/አገልግሎት እንደሚፈልጉ ይጻፉ\n"
    "  (ለምሳሌ፦ «ባለ 2 ክፍል ቤት ቦሌ አካባቢ 5000 ብር ድረስ»)\n\n"
    "ጥያቄዎ ለሻጮች/አከራዮች/አገልግሎት ሰጪዎች  የሚታይ ይሆናል።"
)
SEEKER_LOOKING_FOR_SENT = (
    # "✅ <b>ጥያቄዎ ክፍያ ተቀብሏል!</b>\n\n"
    "✅ <b>ጥያቄዎ ደርሶናል!</b>\n\n"
    "አስተዳዳሪው ሲያጸድቀው ጥያቄዎ ለሻጮች/አከራዮች/አገልግሎት ሰጪዎች ይቀርባል።\n"
    "ሲጸድቅ ማሳወቂያ ይደርስዎታል። እናመሰግናለን!"
)
SEEKER_LOOKING_FOR_APPROVED = (
    "✅ <b>ጥያቄዎ ጸድቋል!</b>\n\n"
    "ጥያቄዎ ለሻጮች/አከራዮች/አገልግሎት ሰጪዎች ቀርቧል።\n"
    "ብዙም ሳይቆይ ሊደወልሎ ይችላል።"
)
SEEKER_LOOKING_FOR_ADMIN = (
    "🔍 <b>አዲስ «ፍላጎት» ጥያቄ — ክፍያ ተፈጽሟል!</b>\n\n"
    "ከ: {seeker}\n"
    "ምድብ: {category}\n"
    "ከተማ (City): {city}\n"
    "ሰፈር (Neighborhood): {neighborhood}\n"
    "ዓላማ (Purpose): {purpose}\n"
    "ዝርዝር: {description}\n"
    "ስልክ: {contact}\n"
    "ክፍያ: 50 ብር (ቋሚ)\n"
    "TxID: {txid}"
)
SEEKER_ASK_CONTACT_FOR_LOOKING = "📞 ስልክ ቁጥርዎን ያስገቡ (ሻጭ/አከራይ/አገልግሎት ሰጪ እንድያናግርዎ):"
SEEKER_ASK_PAYMENT_LOOKING_FOR = (
    "🙏 <b>ጥያቄዎ ሊጠናቀቅ ጥቂት ቀርቶታል!</b>\n\n"
    "ጥያቄዎ ለሻጮች/አከራዮች እንዲደርስ የምዝገባ ክፍያ <b>50 ብር</b> ብቻ ይከፍሉ።\n\n"
    "💰 <b>የክፍያ መጠን፦ 50 ብር</b>\n"
    "👤 <b>ስም፦ ሳምሶን ማሬ</b>\n"
    "   <b>የኢትዮጵያ ንግድ ባንክ አካዉንት ቁጥር፦ 1000174738533</b>\n\n"
    "👇 <i>ክፍያውን ከፈጸሙ በኋላ፣ ከኢትዮጵያ ንግድ ባንክ የደረስዎትን የክፍያ ስክሪንሾት (Screenshot) ወይም የትራንዛክሽን ቁጥር (Transaction ID) እባክዎን እዚህ ይላኩ፦</i>"
)
SEEKER_ASK_PURPOSE = "እባክዎን ከታች ካሉት አማራጮች ይምረጡ:"
PURPOSE_BUY = "🛒 ግዢ"
PURPOSE_RENT = "🏠 ኪራይ"
PURPOSE_SERVICE = "🛠️ አገልግሎት"

SEEKER_ALERT_CREATED = "✅ <b>ማሳወቂያዎ ተፈጥሯል!</b>\n\nከምርጫዎ ጋር የሚስማማ አዲስ ነገር ሲገባ መልእክት እንልክልዎታለን።"
ALERT_NOTIFICATION_MSG = "🔔 <b>አዲስ ማሳወቂያ!</b>\n\nየምትፈልጉት አይነት አዲስ ነገር ተለቋል:\n\n{title}\n\nወደ ዋናው ምናሌ በመሄድ መፈለግ ይችላሉ!"
ALERT_LIST_EMPTY = "ምንም አይነት ማሳወቂያ የለዎትም።"
ALERT_LIST_ITEM = "📌 <b>ዓላማ:</b> {purpose}\n📂 <b>ምድብ:</b> {category}\n📍 <b>ቦታ:</b> {location}\n📅 <b>የተፈጠረበት:</b> {date}"
ALERT_DELETE_BTN = "❌ ሰርዝ"
ALERT_DELETED_MSG = "✅ ማሳወቂያው በተሳካ ሁኔታ ተሰርዟል።"

# Listing Template
LISTING_TEMPLATE = (
    "🌟 <b>{title}</b>\n\n"
    "📌 አይነት፦ <b>{listing_type_am}</b>\n"
    "📍 ቦታ፦ <b>{location}</b>\n"
    "💰 ዋጋ፦ <b>{price} ብር</b>\n\n"
    "📞 ስልክ፦ {contact}\n"
    "📅 የተመዘገበበት፦ {date}"
)

LOOKING_FOR_CHANNEL_POST = (
    "🔎 <b>ፍላጎት — ተፈላጊ</b>\n\n"
    "👤 ፈላጊ። {seeker}\n"
    "📌 ከተማ፦ {city}\n"
    "📍 ሰፈር፦ {neighborhood}\n"
    "🛋️ ዓላማ፦ {purpose}\n"
    "📂 ምድብ፦ {category}\n\n"
    "📝 ዝርዝር፦\n{description}\n\n"
    "📞 ስልክ፦ {contact}"
)

# Admin
ADMIN_DELETE = "🗑️ ዝርዝሩን ሰርዝ (Admin)"
ADMIN_DELETE_CONFIRM = "ዝርዝሩ በተሳካ ሁኔታ ተሰርዟል።"
ADMIN_TITLE = "--- የአስተዳዳሪ ክፍል ---"
ADMIN_APPROVE_REQ = "🆕 አዲስ ክፍያ ተመዝግቧል!\n\nባለቤት፦ {owner}\nርዕስ፦ {title}\nከተማ (City)፦ {city}\nሰፈር (Neighborhood)፦ {neighborhood}\nዓላማ (Purpose)፦ {listing_type_am}\nስልክ፦ {contact}\nዋጋ፦ {price} ብር\nክፍያ፦ 50 ብር (ቋሚ)\nTxID፦ {txid}"
ADMIN_APPROVE = "✅ አጽድቅ"
ADMIN_REJECT = "❌ ውድቅ አድርግ"
ADMIN_APPROVE_CONFIRM = "ዝርዝሩ ጸድቋል! ለፈላጊዎች የቀረበ ነው።"
ADMIN_BROADCAST_PROMPT = "📢 እባክዎን ለሁሉም ተጠቃሚዎች የሚላከውን መልእክት ይጻፉ።"
ADMIN_BROADCAST_DONE = "✅ መልእክቱ ለ {count} ተጠቃሚዎች ተልኳል።"
ADMIN_STATS = (
    "📊 <b>― የአስተዳዳሪ ዳሽቦርድ ―</b>\n\n"
    "👥 ጠቅላላ ተጠቃሚዎች፦ <b>{total}</b>\n\n"
    "🏠 ንቁ ዝርዝሮች (ንብረት/ኪራይ)፦ <b>{active_property}</b>\n"
    "🛠️ ንቁ አገልግሎት ዝርዝሮች፦ <b>{active_service}</b>\n"
    "🔎 ንቁ «ፍላጎት» ጥያቄዎች፦ <b>{active_looking}</b>\n"
    "⏳ ሊጸድቁ እየጠበቁ ያሉ፦ <b>{pending}</b>\n\n"
    "👤 ሻጮች/አከራዮች (ግምት)፦ <b>{owners}</b>\n"
    "👤 ገዢዎች/ተከራዮች (ግምት)፦ <b>{seekers}</b>"
)
ADMIN_ONLY = "❌ ይህ ትዕዛዝ ለአስተዳዳሪዎች ብቻ ነው።"
ADMIN_PENDING_TITLE = "⏳ <b>ከክፍያ ጋር የቀረቡ ዝርዝሮች፦</b>"
ADMIN_NO_PENDING = "✅ ምንም የሚጠበቁ ክፍያዎች የሉም።"
OWNER_ASK_DATE_FILTER = "የማጣሪያ ጊዜ ይምረጡ:"
FILTER_24_HOURS = "ባለፉት 24 ሰዓታት"
FILTER_7_DAYS = "ባለፉት 7 ቀናት"
FILTER_ALL_TIME = "ሁሉም ጊዜ"

# Common
BACK = "ተመለስ ⬅️"
CANCEL = "አቋርጥ ❌"
SKIP = "ዝለል"
CANCEL_MSG = "ክዋኔው ተሰርዟል።"
BTN_NEXT = "ቀጣይ ➡️"
BTN_PREV = "⬅️ ወደኋላ"
HELP_BTN = "መመሪያ/እርዳታ ℹ️"
TIMEOUT_MSG = "⏳ ጊዜው ስላለቀ ክዋኔው ተቋርጧል። እባክዎን እንደገና ይሞክሩ። /start"

# Price Validation
PRICE_INVALID = "❌ ያስገቡት ዋጋ ትክክል አይደለም። እባክዎን ዋጋ በቁጥር ወይም በቃላት ያስገቡ (ለምሳሌ፦ 3500 ወይም «ሶስት ሺ»)"


# Help
HELP_MSG = (
    "📖 <b>የቦቱ አጠቃቀም መመሪያ</b>\n\n"
    "<b>🏠 ለሻጮች፣ አከራዮች፣ እና አገልግሎት ሰጪዎች:</b>\n"
    "• /start → 'አከራይ/ሻጭ/አገልግሎት ሰጪ ነኝ' ይምረጡ\n"
    "• የንብረቱን/የአገልግሎቱን አይነት ወይም አጭር መግለጫ፣ አካባቢ፣ ዋጋ፣ ፎቶ እና ስልክ ያስገቡ\n"
    "• የምዝገባ ክፍያ <b>50 ብር</b> ብቻ (ቋሚ)\n"
    "• ዝርዝርዎ አስተዳዳሪው ክፍያዎን ካረጋገጠ በኋላ ለፈላጊዎች ይቀርባል\n\n"
    "<b>🔍 ለገዢዎች፣ ተከራዮች፣ እና አገልግሎት ፈላጊዎች:</b>\n"
    "• /start → 'ተከራይ/ገዢ/አገልግሎት ፈላጊ ነኝ' ይምረጡ\n"
    "• ሁሉንም ዝርዝሮች ይመልከቱ ወይም በከተማና አካባቢ ይፈልጉ\n"
    "• ከተመቸዎ፣ ባለቤቱን ስልክ ደውለው ያናግሩ\n"
    "• «🔎 ፍላጎቶን ይላኩ» ን ተጠቅመው ምን እንደሚፈልጉ ይጻፉ — ሻጮች/አከራዮች/አገልግሎት ሰጪዎች ያናግሩዎታል\n\n"
    "<b>ለአገልግሎት ሰጪዎች:</b>\n"
    "• ክፍያ በወር 50 ብር ብቻ ነው\n\n"
    "<b>ማስታወቂያ ማስነገር ለምፈልጉ:</b>\n"
    "• በርካታ ተከታዮች ባሉት Sam Technologies የTelegram Channel ማስታወቂያ ማስነገር ከፈለጉ በ 0985605005 ይደዉሉ\n\n"
    "<b>ለበለጠ መረጃ:</b>\n"
    "• 0985605005\n\n"
    "<b>📌 ሌሎች ትዕዛዞች:</b>\n"
    "• /cancel - ወቅታዊ ክዋኔ ለማቋረጥ\n"
    "• /help - ይህን ገጽ ለማሳየት"
)
