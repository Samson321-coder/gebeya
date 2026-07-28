import database
database.init_db()
listings = database.get_all_listings()
print(f"Total active listings: {len(listings)}")
for i in listings:
    status = i[8] if len(i) > 8 else "?"
    print(f"  [{i[0]}] {i[2]} - {i[3]} - status:{status}")
