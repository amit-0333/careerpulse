from pipeline.dedup import dedup_key, normalize_company


def same(a, b):
    return dedup_key(*a) == dedup_key(*b) and dedup_key(*a) is not None


def test_linkedin_suffix_removed():
    assert normalize_company("Artefactlinkedin") == normalize_company("Artefact")
    assert normalize_company("SingleStore-LinkedIn") == normalize_company("SingleStore")


def test_legal_suffix_ignored():
    assert normalize_company("Acme GmbH") == normalize_company("ACME Inc.")


def test_same_job_with_different_formatting():
    assert same(("Artefact", "Data Scientist (m/f/d)", "Paris"),
                ("Artefactlinkedin", "Data Scientist", "Paris, France"))


def test_accents_ignored():
    assert same(("Zalando SE", "Entwickler", "Munchen"), ("Zalando", "Entwickler", "München"))


def test_different_city_is_different_job():
    assert not same(("Acme", "Data Scientist", "Berlin"), ("Acme", "Data Scientist", "London"))


def test_different_title_is_different_job():
    assert not same(("Acme", "Data Scientist", "Berlin"), ("Acme", "Data Engineer", "Berlin"))


def test_different_company_is_different_job():
    assert not same(("Acme", "Data Scientist", "Berlin"), ("Globex", "Data Scientist", "Berlin"))


def test_empty_company_gives_no_key():
    assert dedup_key("", "Data Scientist", "Berlin") is None


def test_cpp_title_is_kept():
    assert dedup_key("Acme", "C++ Developer", "")[1] == "c++ developer"