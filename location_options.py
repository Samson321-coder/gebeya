CITY_OPTIONS = ["አዲስ አበባ/አካባቢዋ", "ዲላ/አካባቢዋ"]

# Neighborhoods per city
NEIGHBORHOODS_BY_CITY = {
    "አዲስ አበባ/አካባቢዋ": [
        "ሁሉም",
        "አዲስ ከተማ",
        "አቃቂ ቃሊቲ",
        "አራዳ",
        "ቦሌ",
        "ጉለሌ",
        "ቂርቆስ",
        "ኮልፌ ቀራኒዮ",
        "ልደታ",
        "ንፋስ ስልክ ላፍቶ",
        "የካ",
        "ለሚ ኩራ",
        "ሸገር ሲቲ",
    ],
    "ዲላ/አካባቢዋ": [
        "ሁሉም",
        "ሳማራ",
        "አበነኤዘር",
        "ሞላ ጎልጃ",
        "ገትስማርት",
        "ሰንሻይን",
        "ዲላይት",
        "ማዞሪያ",
        "መነሃሪያ",
        "ቆፌ",
        "ጪጩ",
        "ዋላሜ",
        "ዳራ/ማጪሾ",
        "ጓንጓ",
        "ኦዶ ሚቄ",
    ],
}

# Flat list for backward-compat validation
NEIGHBORHOOD_OPTIONS = sorted(
    set(n for neighborhoods in NEIGHBORHOODS_BY_CITY.values() for n in neighborhoods)
)


def get_city_keyboard():
    return [[city] for city in CITY_OPTIONS]


def get_neighborhood_keyboard(city=None):
    """Return the neighborhood keyboard for the given city, or all neighborhoods if city is None."""
    if city and city in NEIGHBORHOODS_BY_CITY:
        neighborhoods = NEIGHBORHOODS_BY_CITY[city]
    else:
        # Fallback: flat list of all neighborhoods
        neighborhoods = NEIGHBORHOOD_OPTIONS
    return [[neighborhood] for neighborhood in neighborhoods]


def get_neighborhoods_for_city(city):
    """Return the list of neighborhoods for a city."""
    return NEIGHBORHOODS_BY_CITY.get(city, NEIGHBORHOOD_OPTIONS)


def build_location_string(city, neighborhood):
    city = (city or "").strip()
    neighborhood = (neighborhood or "").strip()
    if not city:
        return neighborhood or ""
    if not neighborhood or neighborhood == "ሁሉም":
        return city
    return f"{city} - {neighborhood}"
