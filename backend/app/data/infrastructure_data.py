"""
Infrastructure Quality Database for FloodSenseAI
=================================================
Maps city names and neighborhood names to a drainage_multiplier.

drainage_multiplier:
  1.0 = Excellent drainage (planned cities, well maintained)
  1.1 = Good drainage (maintained infrastructure)
  1.2 = Average drainage (normal urban areas)
  1.3 = Below average (aging infrastructure, some waterlogging)
  1.4 = Poor drainage (frequent waterlogging, low-lying)
  1.5 = Very poor (known flood-prone, inadequate infrastructure)
  1.6 = Severe (regularly floods in moderate rain)
  1.7 = Critical (floods in light rain, no drainage capacity)
  1.8 = Extreme (historically catastrophic flooding)
  2.0 = Worst case (zero effective drainage, lowest elevation)

This multiplier is applied to the base ML flood risk score.
Score is capped at 100 after multiplication.

Sources: NDMA reports, BMC flood data, BSDMA, news archives, IMD records.
"""

# Format: "normalized name (lowercase)" -> multiplier
INFRASTRUCTURE_DB = {

    # ============================================================
    # MUMBAI METROPOLITAN REGION (MMR)
    # ============================================================

    # Suburbs — Western Line (North to South)
    "virar":            2.0,   # Worst drainage in MMR, repeatedly floods 6-8hrs/year
    "nalasopara":       2.0,   # Zero drainage capacity, low elevation, annual flooding
    "vasai":            1.8,   # Poor drainage, large low-lying areas, creek flooding
    "naigaon":          1.8,   # Near Vasai creek, poor drainage
    "mira road":        1.7,   # Rapid unplanned development, drainage never upgraded
    "bhayander":        1.7,   # Low elevation, poor drains
    "dahisar":          1.6,   # Areas below sea level near creek, poor drainage
    "borivali":         1.2,   # Mixed — Sanjay Gandhi NP helps, drains are ok
    "kandivali":        1.3,   # Some low-lying areas near creek
    "malad":            1.5,   # Mahim Creek flooding, low-lying areas in Malwani
    "malwani":          1.7,   # Very low-lying, extremely poor drainage
    "goregaon":         1.3,   # Mixed — Western Express Highway areas ok
    "jogeshwari":       1.5,   # Low-lying, Mithi River proximity
    "andheri":          1.5,   # Mithi River flooding (2005), low areas near subway
    "versova":          1.4,   # Coastal, creek-side
    "lokhandwala":      1.3,   # Some drainage issues
    "bandra":           1.3,   # Coastal but maintained, BKC is fine
    "khar":             1.2,   # Relatively maintained
    "santacruz":        1.3,   # Airport proximity, some waterlogging
    "vile parle":       1.2,   # Better maintained
    "juhu":             1.4,   # Coastal flooding, low-lying
    "ville parle":      1.2,
    "churchgate":       1.0,   # South Mumbai, well maintained colonial drains
    "fort":             1.0,   # Old but maintained drainage
    "colaba":           1.1,   # Coastal but maintained
    "nariman point":    1.0,   # Reclaimed land but good drainage
    "marine lines":     1.1,
    "grant road":       1.1,
    "charni road":      1.1,
    "mumbai central":   1.2,
    "lower parel":      1.5,   # Mill land, flooding issues
    "parel":            1.4,   # Some drainage issues
    "elphinstone":      1.3,
    "dadar":            1.2,   # Maintained
    "matunga":          1.2,
    "mahim":            1.5,   # Mahim Creek flooding
    "sion":             1.6,   # Frequently floods
    "kurla":            1.8,   # Notoriously flood-prone, multiple underpasses flood
    "vidyavihar":       1.4,
    "ghatkopar":        1.5,   # Underpasses, low-lying areas
    "vikhroli":         1.2,   # Mangroves help absorption
    "kanjurmarg":       1.5,   # Low-lying, prone to waterlogging
    "bhandup":          1.3,   # Mixed
    "mulund":           1.2,   # Better drainage, higher elevation
    "dharavi":          1.8,   # Very low-lying, inadequate drainage
    "chembur":          1.3,   # Mixed areas
    "govandi":          1.6,   # Low-lying near creek
    "mankhurd":         1.6,   # Flooding near creek
    "trombay":          1.4,
    "wadala":           1.4,   # Salt pans, low-lying
    "antop hill":       1.4,

    # Harbour Line
    "csmt":             1.0,   # Central, maintained
    "cst":              1.0,
    "sandhurst road":   1.2,
    "dockyard road":    1.2,
    "reay road":        1.3,
    "cotton green":     1.3,
    "sewri":            1.4,
    "king's circle":    1.2,
    "chunabhatti":      1.3,
    "tilaknagar":       1.3,
    "kurla harbour":    1.7,
    "tilak nagar":      1.3,
    "anik":             1.5,

    # Thane District
    "thane":            1.4,   # Ulhas River flooding, low areas
    "kalyan":           1.6,   # Ulhas River, frequent flooding
    "dombivli":         1.4,   # Some low-lying areas
    "ambernath":        1.4,   # Waterlogging areas
    "badlapur":         1.7,   # Severe flooding in 2021-2024
    "titwala":          1.5,
    "ulhasnagar":       1.6,   # Notoriously poor drainage
    "bhiwandi":         1.6,   # Low-lying, industrial area floods
    "shahapur":         1.5,   # Forest runoff issues

    # Navi Mumbai (Planned city — better infrastructure)
    "navi mumbai":      1.0,   # Planned city, excellent drainage grid
    "vashi":            1.0,
    "belapur":          1.0,
    "airoli":           1.0,
    "ghansoli":         1.1,
    "kopar khairane":   1.0,
    "sanpada":          1.0,
    "juinagar":         1.1,
    "nerul":            1.0,
    "seawoods":         1.1,
    "panvel":           1.3,   # Older area, creek flooding
    "khopoli":          1.4,

    # ============================================================
    # PUNE METROPOLITAN REGION
    # ============================================================
    "pune":             1.2,   # Generally ok but areas near rivers flood
    "pimpri":           1.2,
    "chinchwad":        1.1,
    "hadapsar":         1.4,   # Mutha River proximity
    "kothrud":          1.1,
    "shivajinagar":     1.1,
    "yerawada":         1.3,
    "wagholi":          1.5,   # Rapid development, no drainage
    "talegaon":         1.3,
    "sinhagad road":    1.2,
    "kondhwa":          1.3,   # Some waterlogging
    "katraj":           1.3,

    # ============================================================
    # DELHI NCR
    # ============================================================
    "delhi":            1.3,   # Variable across city
    "old delhi":        1.7,   # Ancient narrow drains, severe waterlogging
    "chandni chowk":    1.6,   # Colonial-era drains, flood-prone
    "sadar bazar":      1.6,
    "karol bagh":       1.5,
    "paharganj":        1.5,
    "connaught place":  1.2,   # Maintained
    "south delhi":      1.1,   # Better maintained
    "lodi colony":      1.0,
    "hauz khas":        1.1,
    "dwarka":           1.6,   # Waterlogging — famous for it
    "rohini":           1.4,   # Some low-lying sectors
    "pitampura":        1.3,
    "janakpuri":        1.2,
    "rajouri garden":   1.3,
    "uttam nagar":      1.5,
    "vikaspuri":        1.4,
    "narela":           1.6,   # Low-lying, farmland conversion
    "bawana":           1.7,
    "prashant vihar":   1.3,
    "saket":            1.1,
    "vasant kunj":      1.1,
    "mahipalpur":       1.4,   # Near airport, low-lying
    "gurgaon":          1.8,   # Infamous for flooding despite being new city
    "gurugram":         1.8,   # Same as gurgaon
    "noida":            1.3,   # Planned but some sectors waterlog
    "greater noida":    1.1,   # Newer, better planned
    "faridabad":        1.4,
    "ghaziabad":        1.5,

    # ============================================================
    # KOLKATA
    # ============================================================
    "kolkata":          1.5,   # Low elevation, tidal flooding
    "howrah":           1.6,   # River-side, very low
    "garden reach":     1.6,
    "metiabruz":        1.7,   # Extremely low-lying
    "majerhat":         1.5,
    "tollygunge":       1.4,
    "salt lake":        1.4,   # Built on salt lake, reclaimed land
    "new town":         1.2,   # Newer planned area
    "rajarhat":         1.3,
    "dumdum":           1.5,
    "belgharia":        1.5,
    "baranagar":        1.5,
    "kamarhati":        1.5,
    "barrackpore":      1.4,

    # ============================================================
    # CHENNAI
    # ============================================================
    "chennai":          1.4,   # 2015 floods, poor drainage historically
    "adyar":            1.6,   # Adyar River flooding
    "velachery":        1.7,   # Notorious flooding, low-lying lake area
    "tambaram":         1.4,
    "perambur":         1.5,
    "vyasarpadi":       1.5,
    "egmore":           1.3,
    "nungambakkam":     1.2,
    "anna nagar":       1.2,
    "t nagar":          1.3,
    "mylapore":         1.4,
    "besant nagar":     1.3,   # Coastal
    "marina":           1.3,   # Coastal
    "sholinganallur":   1.4,
    "pallikaranai":     1.7,   # Built on wetland/marshland
    "medavakkam":       1.6,
    "madipakkam":       1.6,
    "nanganallur":      1.5,
    "chromepet":        1.4,

    # ============================================================
    # BANGALORE / BENGALURU
    # ============================================================
    "bangalore":        1.3,   # Lake flooding, IT corridors flood
    "bengaluru":        1.3,
    "koramangala":      1.4,   # Built on lake, floods frequently
    "hsr layout":       1.3,   # Some low areas
    "electronic city":  1.2,
    "whitefield":       1.3,   # Low-lying areas
    "marathahalli":     1.4,
    "hebbal":           1.3,   # Near lake
    "yelahanka":        1.3,
    "raja rajeshwari nagar": 1.5, # Low-lying, flooding issues
    "majestic":         1.3,
    "shivajinagar bengaluru": 1.2,
    "jayanagar":        1.2,
    "btm layout":       1.4,

    # ============================================================
    # HYDERABAD
    # ============================================================
    "hyderabad":        1.2,   # Variable
    "secunderabad":     1.2,
    "banjara hills":    1.1,
    "jubilee hills":    1.1,
    "hitech city":      1.2,
    "gachibowli":       1.2,
    "kukatpally":       1.4,   # Low-lying, flooding
    "lb nagar":         1.4,
    "uppal":            1.4,   # Musi River proximity
    "old city":         1.5,   # Musi River flooding

    # ============================================================
    # ASSAM / NORTHEAST
    # ============================================================
    "guwahati":         1.8,   # Brahmaputra flooding, severe annual
    "jorhat":           1.6,
    "dibrugarh":        1.7,
    "silchar":          1.7,
    "nagaon":           1.6,
    "tezpur":           1.6,

    # ============================================================
    # BIHAR / EAST INDIA
    # ============================================================
    "patna":            1.7,   # Ganga river flooding
    "muzaffarpur":      1.7,
    "darbhanga":        1.8,   # Severely flood prone every year
    "bhagalpur":        1.6,
    "purnea":           1.6,

    # ============================================================
    # OTHER MAJOR INDIAN CITIES
    # ============================================================
    "ahmedabad":        1.2,   # Generally ok
    "surat":            1.4,   # Tapi River flooding 2006
    "vadodara":         1.4,   # Vishwamitri River flooding
    "rajkot":           1.2,
    "bhopal":           1.2,
    "indore":           1.2,
    "jabalpur":         1.3,
    "nagpur":           1.3,   # Some low-lying areas
    "nashik":           1.3,   # Godavari flooding
    "aurangabad":       1.2,
    "solapur":          1.2,
    "jaipur":           1.2,
    "jodhpur":          1.1,   # Desert city, rain rarely
    "udaipur":          1.3,
    "kota":             1.3,
    "lucknow":          1.4,   # Gomti River
    "varanasi":         1.5,   # Ganga flooding
    "kanpur":           1.4,
    "agra":             1.3,   # Yamuna River
    "prayagraj":        1.5,   # Ganga-Yamuna confluence
    "allahabad":        1.5,   # Same as prayagraj
    "meerut":           1.4,
    "bhubaneswar":      1.4,   # Cyclone-prone
    "cuttack":          1.6,   # Mahanadi River
    "puri":             1.5,   # Coastal
    "visakhapatnam":    1.4,   # Coastal, cyclone-prone
    "vijayawada":       1.5,   # Krishna River flooding
    "kochi":            1.4,   # 2018 floods
    "trivandrum":       1.3,
    "thiruvananthapuram": 1.3,
    "kozhikode":        1.4,
    "thrissur":         1.4,
    "mangalore":        1.4,   # Coastal, heavy rain
    "mysore":           1.2,
    "mysuru":           1.2,
    "coimbatore":       1.2,
    "madurai":          1.3,
    "tiruchirappalli":  1.3,
    "salem":            1.2,
    "tirunelveli":      1.3,

    # ============================================================
    # GLOBAL CITIES (for the world scan feature)
    # ============================================================
    "brussels":         1.0,   # Good European drainage
    "london":           1.1,   # Thames Barrier, mostly ok
    "miami":            1.4,   # Low-lying, sea level rise, poor drainage
    "new orleans":      1.9,   # Below sea level, levee-dependent
    "houston":          1.6,   # Famously poor drainage (Harvey 2017)
    "jakarta":          1.9,   # Sinking city, extreme flooding
    "dhaka":            1.8,   # Delta city, severe flooding
    "chittagong":       1.7,   # Port city, flooding
    "manila":           1.7,   # Typhoon flooding, poor drainage
    "bangkok":          1.5,   # 2011 megaflood, improving
    "ho chi minh city": 1.6,   # Low-lying delta
    "hanoi":            1.5,   # Red River Delta
    "yangon":           1.6,   # Low-lying delta
    "colombo":          1.4,   # Coastal, some drainage issues
    "singapore":        1.0,   # World's best drainage infrastructure
    "kuala lumpur":     1.3,   # SMART Tunnel helps, but still floods
    "tokyo":            1.0,   # Excellent underground drainage
    "osaka":            1.1,
    "hong kong":        1.2,   # Good infrastructure
    "taipei":           1.2,
    "lagos":            1.8,   # Very poor drainage, flooding every rain
    "accra":            1.6,   # Poor drainage
    "nairobi":          1.4,
    "kinshasa":         1.7,
    "new york":         1.1,   # Hurricane Sandy improved awareness
    "seattle":          1.1,
    "amsterdam":        1.0,   # Dutch engineering, world class
    "dublin":           1.1,
    "bergen":           1.2,   # Rainy but ok drainage
    "karachi":          1.7,   # Terrible drainage, floods in monsoon
    "islamabad":        1.2,   # Better planned
    "kathmandu":        1.5,   # Valley flooding
    "sao paulo":        1.5,   # Low-lying areas flood
    "bogota":           1.3,
    "lima":             1.1,   # Desert city, rarely rains
    "buenos aires":     1.3,
}


def get_infrastructure_multiplier(location_name: str) -> float:
    """
    Look up the infrastructure/drainage multiplier for a location using fuzzy matching.
    Uses rapidfuzz so that spelling variants from OWM (e.g. "Nallasopara" vs "Nalasopara")
    still match correctly.

    Returns 1.2 (average urban) if location is unknown or similarity is too low.
    """
    if not location_name:
        return 1.2

    name = location_name.lower().strip()

    # 1. Exact match — fastest path
    if name in INFRASTRUCTURE_DB:
        return INFRASTRUCTURE_DB[name]

    # 2. Fuzzy match using rapidfuzz
    try:
        from rapidfuzz import process, fuzz
        # Extract best matching key from our DB
        result = process.extractOne(
            name,
            INFRASTRUCTURE_DB.keys(),
            scorer=fuzz.token_set_ratio,  # handles word reordering and partial matches
            score_cutoff=80              # minimum 80% similarity required
        )
        if result:
            matched_key, score, _ = result
            return INFRASTRUCTURE_DB[matched_key]
    except ImportError:
        # rapidfuzz not installed — fall back to substring matching
        best_match = None
        best_len = 0
        for key, multiplier in INFRASTRUCTURE_DB.items():
            if key in name or name in key:
                if len(key) > best_len:
                    best_match = multiplier
                    best_len = len(key)
        if best_match is not None:
            return best_match

    # 3. Default — unknown location, assume average urban drainage
    return 1.2


def get_infrastructure_description(multiplier: float) -> str:
    """Return a human-readable description of the infrastructure quality."""
    if multiplier >= 1.8:
        return "extremely poor drainage infrastructure"
    elif multiplier >= 1.6:
        return "severely inadequate drainage"
    elif multiplier >= 1.4:
        return "below-average drainage capacity"
    elif multiplier >= 1.2:
        return "average urban drainage"
    elif multiplier >= 1.1:
        return "above-average drainage"
    else:
        return "excellent drainage infrastructure"
