import database
database.init_db()
listings = database.get_all_listings()
print(f"Total active: {len(listings)}")
for r in listings:
    lt = r[13] if len(r) > 13 else "?"
    pp = r[7]
    print(f"  id={r[0]} title={r[2]} location={r[3]} status={r[9]} listing_type={lt} property_purpose={pp}")

# Test filtered queries
print("\n--- Filter: buyer (property, sell) ---")
results = database.get_listings_by_city("አዲስ አበባ", listing_type="property", property_purpose="sell")
print(f"  Found: {len(results)}")

print("\n--- Filter: renter (property, rent) ---")
results = database.get_listings_by_city("አዲስ አበባ", listing_type="property", property_purpose="rent")
print(f"  Found: {len(results)}")

print("\n--- Filter: service seeker (service) ---")
results = database.get_listings_by_city("አዲስ አበባ", listing_type="service")
print(f"  Found: {len(results)}")
