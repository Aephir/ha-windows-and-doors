from __future__ import annotations

OPEN_STATES = {"on", "open", "opening"}
CLOSED_STATES = {"off", "closed"}


def _normalized_state(state: str | None) -> str | None:
    if state is None:
        return None
    return state.strip().lower()


def get_entity_status(entity_id: str | None, state: str | None) -> str:
    normalized = _normalized_state(state)

    if normalized is None:
        return "Unknown"
    if normalized == "unknown":
        return "Unknown"
    if normalized == "unavailable":
        return "Unavailable"

    if entity_id and entity_id.startswith("cover."):
        return "Closed" if normalized == "closed" else "Open"

    if normalized in CLOSED_STATES:
        return "Closed"
    if normalized in OPEN_STATES:
        return "Open"

    return "Open"


def is_entity_open(entity_id: str | None, state: str | None) -> bool:
    return get_entity_status(entity_id, state) == "Open"
