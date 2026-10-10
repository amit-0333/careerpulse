import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.dedup import dedup_key, normalize_company

fails = 0


def check(name, got, expected):
    global fails
    ok = got == expected
    fails += not ok
    print("PASS" if ok else "FAIL", "|", name, "" if ok else f"| got={got} expected={expected}")


def same(a, b):
    return dedup_key(*a) == dedup_key(*b) and dedup_key(*a) is not None


check("Artefact vs Artefactlinkedin", normalize_company("Artefactlinkedin"), normalize_company("Artefact"))
check("SingleStore-LinkedIn", normalize_company("SingleStore-LinkedIn"), normalize_company("SingleStore"))
check("legal suffix GmbH/Inc", normalize_company("Acme GmbH"), normalize_company("ACME Inc."))
check("same job, tag and city format differ",
      same(("Artefact", "Data Scientist (m/f/d)", "Paris"),
           ("Artefactlinkedin", "Data Scientist", "Paris, France")), True)
check("accents ignored", same(("Zalando SE", "Entwickler", "Munchen"), ("Zalando", "Entwickler", "München")), True)
check("different city = different job",
      same(("Acme", "Data Scientist", "Berlin"), ("Acme", "Data Scientist", "London")), False)
check("different title = different job",
      same(("Acme", "Data Scientist", "Berlin"), ("Acme", "Data Engineer", "Berlin")), False)
check("different company = different job",
      same(("Acme", "Data Scientist", "Berlin"), ("Globex", "Data Scientist", "Berlin")), False)
check("empty company -> no key", dedup_key("", "Data Scientist", "Berlin"), None)
check("C++ title kept", dedup_key("Acme", "C++ Developer", "")[1], "c++ developer")

print("\nALL PASSED" if not fails else f"\n{fails} FAILED")