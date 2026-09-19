import pytest

from evidencebench.evaluation.span_runner import reserve_variant


def test_three_variants_each_have_one_atomic_attempt(tmp_path):
    for variant in ("plain", "constrained", "focused"):
        reserve_variant(tmp_path, variant)
        with pytest.raises(ValueError, match="already used"):
            reserve_variant(tmp_path, variant)
    with pytest.raises(ValueError, match="unknown"):
        reserve_variant(tmp_path, "fourth")
    assert len(list((tmp_path / "attempts").glob("*.json"))) == 3
