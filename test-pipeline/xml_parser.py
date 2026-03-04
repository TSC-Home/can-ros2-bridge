"""Parse bridge XML config to extract allowed messages, signals and topics."""

from lxml import etree


def parse_allowed(xml_path: str) -> dict[int, set[str]]:
    """Return {can_id: {signal_name, ...}} from bridge XML config."""
    tree = etree.parse(xml_path)
    allowed = {}
    for msg in tree.findall(".//message"):
        can_id = int(msg.get("id"))
        signals = {sig.get("name") for sig in msg.findall("signal")}
        allowed[can_id] = signals
    return allowed


def parse_topics(xml_path: str) -> dict[str, str]:
    """Return {topic: signal_name} from bridge XML config."""
    tree = etree.parse(xml_path)
    topics = {}
    for sig in tree.findall(".//signal"):
        topics[sig.get("topic")] = sig.get("name")
    return topics
