from typing import Dict, List


def generate_ad_mermaid(ad: Dict, posted: List[Dict]) -> str:
    """Generate a simple Mermaid flowchart string for an ad and its posted marketplaces.

    Implementation is intentionally small and deterministic for tests and UI demo.
    """
    title = ad.get("title") or ad.get("id")
    owner = ad.get("owner_id", "unknown")

    lines = ["flowchart TB"]
    # High-level nodes
    lines.append('    create["Create Ad"]')
    lines.append(f'    ad["Ad: {title}"]')
    lines.append("    create --> ad")

    # If there are posted marketplaces, add nodes
    platforms = []
    for p in posted:
        plat = p.get("platform")
        if plat and plat not in platforms:
            platforms.append(plat)

    for i, plat in enumerate(platforms):
        node_id = f"m{i}"
        lines.append(f'    {node_id}["{plat}"]')
        lines.append(f"    ad --> {node_id}")

    # Footer with owner info
    lines.append("    style ad fill:#f9f,stroke:#333,stroke-width:1px")
    lines.append(f"    subgraph owner[Owner: {owner}]")
    lines.append("    end")

    return "\n".join(lines)
