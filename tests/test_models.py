import pytest

from attribution.models import Journey, compare, first_touch, last_touch, linear, markov, position_based, time_decay
from attribution.sample import generate

JS = [
    Journey(["Social", "Search"], True),
    Journey(["Social", "Email", "Search"], True),
    Journey(["Search"], True),
    Journey(["Social"], False),
    Journey(["Email"], False),
]


def test_rule_based_models():
    assert last_touch(JS) == {"Search": 3}
    assert first_touch(JS) == {"Social": 2, "Search": 1}
    lin = linear(JS)
    assert lin["Social"] == pytest.approx(0.5 + 1 / 3)
    pb = position_based(JS)
    assert pb["Email"] == pytest.approx(0.2)


@pytest.mark.parametrize("fn", [last_touch, first_touch, linear, time_decay, position_based, markov])
def test_every_model_credits_all_conversions(fn):
    assert sum(fn(JS).values()) == pytest.approx(3)


def test_time_decay_favours_recent_touches():
    td = time_decay([Journey(["A", "B", "C"], True)])
    assert td["C"] > td["B"] > td["A"]


def test_markov_gives_credit_to_assisting_channels():
    mk = markov(JS)
    assert mk["Social"] > 0 and mk["Search"] > mk["Email"]


def test_sample_story_last_touch_undercredits_creators():
    js = [Journey(r["path"].split(" > "), bool(r["converted"])) for r in generate(3000)]
    t = compare(js)
    assert t["Markov (data-driven)"]["Instagram creators"] > t["Last touch"].get("Instagram creators", 0) * 1.5
