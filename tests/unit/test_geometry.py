import pytest
from test_retrieval import make_units


@pytest.mark.parametrize("value", [float("inf"), float("nan")])
def test_nonfinite_geometry_rejected(value):
    from evidencebench.schemas import ContentUnit

    values = make_units()[0].model_dump()
    values["bbox"] = (1, 2, value, value)
    with pytest.raises(ValueError):
        ContentUnit.model_validate(values)
