import re
import unicodedata

# Words that only mark legal form or the posting channel, not the company itself
_LEGAL = {
    "gmbh", "ag", "se", "inc", "llc", "ltd", "limited", "corp", "corporation",
    "co", "plc", "bv", "ab", "oy", "srl", "sarl", "sa", "pvt", "kg", "ug",
}
_CHANNEL_SUFFIXES = ("linkedin",)

# "(m/f/d)", "(w/m/x)", "m/w/d" ... gender tags used in German job titles
_GENDER_TAG = re.compile(r"\(?\b[mwfd]\s*/\s*[mwfdx](?:\s*/\s*[mwfdx])?\b\)?", re.IGNORECASE)


def _ascii(text):
    text = unicodedata.normalize("NFKD", str(text or ""))
    return text.encode("ascii", "ignore").decode("ascii").lower()


def normalize_company(name):
    tokens = re.findall(r"[a-z0-9]+", _ascii(name))
    tokens = [t for t in tokens if t not in _LEGAL]
    squashed = "".join(tokens)
    for suffix in _CHANNEL_SUFFIXES:
        if squashed.endswith(suffix) and len(squashed) - len(suffix) >= 3:
            squashed = squashed[: -len(suffix)]
    return squashed


def normalize_title(title):
    text = _GENDER_TAG.sub(" ", _ascii(title))
    return " ".join(re.findall(r"[a-z0-9+#]+", text))


def normalize_location(location):
    first_part = _ascii(location).split(",")[0]
    return " ".join(re.findall(r"[a-z0-9]+", first_part))


def dedup_key(company, title, location=""):
    """Same company + same title + same city => same job. None if unusable."""
    c, t = normalize_company(company), normalize_title(title)
    if not c or not t:
        return None
    return (c, t, normalize_location(location))