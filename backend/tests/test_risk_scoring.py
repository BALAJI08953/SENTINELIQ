import pytest

from app.services.risk.scoring import priority_for, score_risk


@pytest.mark.parametrize("score,expected", [
    (0, "low"), (34.99, "low"), (35, "medium"), (59.99, "medium"),
    (60, "high"), (79.99, "high"), (80, "critical"), (100, "critical"),
])
def test_priority_boundaries(score, expected):
    assert priority_for(score) == expected


def test_formula_and_components():
    r = score_risk(10, 10, 10, 10)
    assert r.overall_score == 100 and r.priority == "critical"
    r = score_risk(8, 6, 4, 2)
    assert r.overall_score == pytest.approx(10 * (0.35 * 8 + 0.25 * 6 + 0.25 * 4 + 0.15 * 2))
    assert "Heuristic" in r.explanation


@pytest.mark.parametrize("bad", [-0.1, 10.1])
def test_out_of_range_rejected(bad):
    with pytest.raises(ValueError):
        score_risk(bad, 5, 5, 5)
