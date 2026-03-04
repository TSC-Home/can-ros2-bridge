"""Interactive signal mapping selection."""

import click


def select_signals(messages: list[dict]) -> list[dict]:
    """Interactively select which signals to map to ROS2 topics."""
    selected = []

    for msg in messages:
        click.echo(f"\n--- {msg['name']} (0x{msg['id']:X}) ---")
        for sig in msg["signals"]:
            if click.confirm(f"  Map signal '{sig['name']}'?", default=True):
                default_topic = f"/{msg['name'].lower()}/{sig['name'].lower()}"
                topic = click.prompt("    ROS2 topic", default=default_topic)
                selected.append({
                    "message": msg,
                    "signal": sig,
                    "topic": topic,
                })

    return selected
