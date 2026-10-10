import re
import unicodedata

# country code -> names/aliases a user might type (written in normalized form)
COUNTRIES = {
    "us": ["usa", "us", "u s", "united states", "united states of america", "america"],
    "uk": ["uk", "united kingdom", "great britain", "britain", "england", "scotland", "wales", "gb"],
    "de": ["germany", "deutschland"],
    "fr": ["france"],
    "ch": ["switzerland", "schweiz", "suisse"],
    "nl": ["netherlands", "the netherlands", "holland"],
    "in": ["india"],
    "ca": ["canada"],
    "ie": ["ireland"],
    "es": ["spain"],
    "it": ["italy"],
    "at": ["austria"],
    "se": ["sweden"],
    "pl": ["poland"],
    "pt": ["portugal"],
    "be": ["belgium"],
    "dk": ["denmark"],
    "sg": ["singapore"],
    "au": ["australia"],
    "ae": ["uae", "united arab emirates"],
    "jp": ["japan"],
}

# well-known tech cities -> country code (extend this when the report shows gaps)
CITIES = {
    "de": ["berlin", "munich", "hamburg", "frankfurt", "cologne", "stuttgart", "dusseldorf", "leipzig", "dresden"],
    "uk": ["london", "manchester", "edinburgh", "bristol", "birmingham", "leeds", "glasgow"],
    "fr": ["paris", "lyon", "toulouse", "marseille"],
    "ch": ["zurich", "geneva", "lausanne", "bern", "basel", "zug"],
    "nl": ["amsterdam", "rotterdam", "utrecht", "eindhoven", "the hague"],
    "in": ["bangalore", "bengaluru", "mumbai", "delhi", "new delhi", "hyderabad", "pune", "chennai",
           "gurgaon", "gurugram", "noida", "kolkata", "ahmedabad"],
    "us": ["new york", "san francisco", "seattle", "austin", "boston", "chicago", "los angeles",
           "san jose", "mountain view", "palo alto", "denver", "atlanta", "washington dc", "san diego"],
    "ca": ["toronto", "vancouver", "montreal", "ottawa", "calgary"],
    "ie": ["dublin"], "es": ["madrid", "barcelona"], "at": ["vienna", "wien"],
    "se": ["stockholm"], "pl": ["warsaw", "krakow", "wroclaw"], "pt": ["lisbon", "porto"],
    "sg": ["singapore"], "au": ["sydney", "melbourne"], "dk": ["copenhagen"],
    "be": ["brussels"], "it": ["milan", "rome"], "jp": ["tokyo"], "ae": ["dubai"],
}

# extra places seen in real data: local spellings, regions, smaller cities
_EXTRA_PLACES = {
    "de": ["munchen", "koln", "nuremberg", "nurnberg", "bonn", "essen", "bochum", "heidelberg",
           "karlsruhe", "wiesbaden", "dortmund", "hannover", "bremen", "mannheim", "freiburg",
           "aachen", "bavaria", "bayern", "parsdorf", "ger"],
    "uk": ["belfast", "cardiff", "sheffield", "liverpool", "nottingham", "oxford", "northern ireland"],
    "fr": ["saint denis", "lille", "amiens", "nantes", "bordeaux", "nice", "strasbourg", "rennes",
           "montpellier", "fr"],
    "ch": ["steinhausen", "mendrisio", "jona", "st gallen", "lucerne", "wettingen", "aargau", "vaud",
           "ticino", "winterthur", "lugano"],
    "in": ["vadodara", "gujarat", "karnataka", "maharashtra", "tamil nadu", "telangana", "jaipur",
           "kochi", "coimbatore", "indore", "chandigarh"],
}
for _code, _names in _EXTRA_PLACES.items():
    CITIES.setdefault(_code, []).extend(_names)

US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA",
    "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT",
    "VA", "WA", "WV", "WI", "WY", "DC",
}

_REMOTE_WORDS = ("remote", "anywhere", "worldwide", "work from home")


def _norm(text):
    text = unicodedata.normalize("NFKD", str(text or "")).encode("ascii", "ignore").decode("ascii")
    return " ".join(re.findall(r"[a-z0-9]+", text.lower()))


_COUNTRY_LOOKUP = {_norm(a): code for code, names in COUNTRIES.items() for a in names}
_PHRASES = dict(_COUNTRY_LOOKUP)
for _code, _names in CITIES.items():
    for _c in _names:
        _PHRASES[_norm(_c)] = _code


def countries_in(location):
    """Country codes we can recognise in a job's location text."""
    padded = f" {_norm(location)} "
    found = {code for phrase, code in _PHRASES.items() if f" {phrase} " in padded}
    if not found:  # "Springfield, IL" style -> US state code after a comma
        for m in re.finditer(r",\s*([A-Z]{2})\b", str(location or "")):
            if m.group(1) in US_STATES:
                found.add("us")
    return found


def is_remote(location, job_type=""):
    if str(job_type or "").lower().strip() == "remote":
        return True
    padded = f" {_norm(location)} "
    return any(f" {w} " in padded for w in _REMOTE_WORDS)


def location_matches(job_location, query, job_type="", include_remote=True):
    """Does a job's location match what the user typed?"""
    q = _norm(query)
    if not q:
        return True
    remote = is_remote(job_location, job_type)
    if q in _REMOTE_WORDS:
        return remote
    code = _COUNTRY_LOOKUP.get(q)
    if code:
        countries = countries_in(job_location)
        if code in countries:
            return True
        # worldwide-remote job with no country at all
        return include_remote and remote and not countries
    # city / free text: whole-word prefix match ("ber" finds Berlin, "usa" never finds Lausanne)
    return bool(re.search(r"\b" + re.escape(q), _norm(job_location)))