"""Export signal mappings to bridge config XML."""

from lxml import etree


def export_config(mappings: list[dict], output_path: str) -> None:
    """Write bridge config XML from selected mappings."""
    root = etree.Element("bridge")
    messages_added: dict[int, etree._Element] = {}

    for m in mappings:
        msg = m["message"]
        sig = m["signal"]
        msg_id = msg["id"]

        if msg_id not in messages_added:
            msg_el = etree.SubElement(root, "message")
            msg_el.set("id", str(msg_id))
            msg_el.set("name", msg["name"])
            messages_added[msg_id] = msg_el

        sig_el = etree.SubElement(messages_added[msg_id], "signal")
        sig_el.set("name", sig["name"])
        sig_el.set("start_bit", str(sig["start_bit"]))
        sig_el.set("length", str(sig["length"]))
        sig_el.set("byte_order", sig["byte_order"])
        sig_el.set("signed", str(sig.get("signed", False)).lower())
        sig_el.set("scale", str(sig["scale"]))
        sig_el.set("offset", str(sig["offset"]))
        sig_el.set("topic", m["topic"])

    tree = etree.ElementTree(root)
    etree.indent(tree, space="    ")
    tree.write(output_path, pretty_print=True, xml_declaration=True, encoding="UTF-8")
