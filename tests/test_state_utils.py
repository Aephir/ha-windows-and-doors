from custom_components.windows_and_doors.state_utils import resolve_entity_state


def test_cover_closed_is_closed():
    assert resolve_entity_state("cover.test_cover", "closed") == "Closed"


def test_cover_percentage_is_open():
    assert resolve_entity_state("cover.test_cover", "58") == "Open"


def test_cover_unknown_is_unknown():
    assert resolve_entity_state("cover.test_cover", "unknown") == "Unknown"


def test_cover_unavailable_is_unavailable():
    assert resolve_entity_state("cover.test_cover", "unavailable") == "Unavailable"


def test_binary_sensor_off_is_closed():
    assert resolve_entity_state("binary_sensor.test_sensor", "off") == "Closed"


def test_binary_sensor_on_is_open():
    assert resolve_entity_state("binary_sensor.test_sensor", "on") == "Open"
