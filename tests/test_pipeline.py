from app.services.pipeline import contains_banned, compute_metadata

def test_contains_banned_true():
    assert contains_banned("Esto es spam total", ["spam"]) is True

def test_contains_banned_false():
    assert contains_banned("Mensaje limpio", ["spam"]) is False

def test_compute_metadata_counts_and_iso():
    wc, cc, processed = compute_metadata("hola mundo")
    assert wc == 2
    assert cc == len("hola mundo")
    assert processed.endswith("Z")
