import asyncio
import os
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock

os.environ.setdefault("BOT_TOKEN", "dummy-token")

import database
import main
import strings

class EnhancementTests(unittest.TestCase):
    def setUp(self):
        os.environ["DB_ENGINE"] = "sqlite"
        database.SQLITE_PATH = "test_rental_bot.db"
        if os.path.exists("test_rental_bot.db"):
            os.remove("test_rental_bot.db")
        database.init_db()

    def tearDown(self):
        if os.path.exists("test_rental_bot.db"):
            os.remove("test_rental_bot.db")

    def test_strings_categories(self):
        self.assertEqual(strings.CATEGORY_OTHER, "📦 ሌሎች")
        self.assertEqual(strings.SERVICE_CATEGORY_OTHER, "📦 ሌሎች አገልግሎቶች")

    def test_alerts_with_description(self):
        database.add_alert(
            telegram_id=12345,
            category="🏠 ቤት/መሬት",
            city="አዲስ አበባ/ዙሪያ",
            neighborhood="ቦሌ",
            property_purpose="buy",
            description="ባለ 2 ክፍል ኮንዶሚኒየም"
        )
        alerts = database.get_alerts_by_user(12345)
        self.assertEqual(len(alerts), 1)
        alert = alerts[0]
        # alert structure: id, telegram_id, category, city, neighborhood, property_purpose, created_at, description
        self.assertEqual(alert[1], 12345)
        self.assertEqual(alert[2], "🏠 ቤት/መሬት")
        self.assertEqual(alert[3], "አዲስ አበባ/ዙሪያ")
        self.assertEqual(alert[4], "ቦሌ")
        self.assertEqual(alert[5], "buy")
        self.assertEqual(alert[7], "ባለ 2 ክፍል ኮንዶሚኒየም")

    def test_get_listings_by_owner_filtering(self):
        database.add_listing(100, "Listing 1", "አዲስ አበባ - ቦሌ", "1000", None, "0911000000", listing_type="property", property_purpose="sell")
        database.add_listing(100, "Listing 2", "አዲስ አበባ - ቦሌ", "2000", None, "0911000000", listing_type="property", property_purpose="rent")
        database.add_listing(100, "Listing 3", "አዲስ አበባ - ቦሌ", "3000", None, "0911000000", listing_type="service", property_purpose=None)

        all_listings = database.get_listings_by_owner(100)
        self.assertEqual(len(all_listings), 3)

        sell_listings = database.get_listings_by_owner(100, listing_type="property", property_purpose="sell")
        self.assertEqual(len(sell_listings), 1)
        self.assertEqual(sell_listings[0][2], "Listing 1")

        rent_listings = database.get_listings_by_owner(100, listing_type="property", property_purpose="rent")
        self.assertEqual(len(rent_listings), 1)
        self.assertEqual(rent_listings[0][2], "Listing 2")

        service_listings = database.get_listings_by_owner(100, listing_type="service")
        self.assertEqual(len(service_listings), 1)
        self.assertEqual(service_listings[0][2], "Listing 3")

    def test_seeker_menu_keyboard_has_no_alert_buttons(self):
        keyboard = main.get_seeker_menu_keyboard()
        labels = [label for row in keyboard.keyboard for label in row]

        self.assertNotIn("ማሳወቂያ ፍጠር", labels)
        self.assertNotIn("ማሳወቂያዎችን ሰርዝ", labels)
        self.assertNotIn("የኔን ፍላጎቶች አስተዳድር", labels)

    def test_send_listing_page_renders_listing_without_error(self):
        async def run_test():
            listing = (
                1,
                100,
                "Luxury Home",
                "አዲስ አበባ - ቦሌ",
                "5000",
                None,
                "0911000000",
                "sell",
                "2026-01-01 12:00:00",
                "paid",
                0,
                None,
                None,
                "property",
            )
            update = SimpleNamespace(
                effective_user=SimpleNamespace(id=100),
                effective_chat=SimpleNamespace(id=200),
            )
            bot = SimpleNamespace(
                send_photo=AsyncMock(),
                send_message=AsyncMock(),
                send_media_group=AsyncMock(),
            )
            context = SimpleNamespace(
                user_data={"current_listings": [listing], "is_for_owner": False},
                bot=bot,
            )

            await main.send_listing_page(update, context, 0)

            bot.send_message.assert_called_once()

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()
