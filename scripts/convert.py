#!/usr/bin/env python3
"""
Convert systemprompt-web skills and agents to Claude Code plugin marketplace format.

Replicates the logic from:
- export_resolvers.rs:63 build_skill_md()
- export_resolvers.rs:97 strip_frontmatter()
- export_resolvers.rs:110 collect_skill_auxiliary_files()
- export_resolvers.rs:229 build_agent_md()
"""

import argparse
import json
import os
import shutil
import sys

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


def strip_frontmatter(content: str) -> str:
    """Remove YAML frontmatter from markdown content.
    Mirrors export_resolvers.rs:97 strip_frontmatter()"""
    trimmed = content.lstrip()
    if not trimmed.startswith("---"):
        return content
    parts = trimmed.split("---", 2)
    if len(parts) >= 3:
        return parts[2].strip()
    return content


def to_kebab(name: str) -> str:
    """Convert snake_case to kebab-case."""
    return name.replace("_", "-")


def convert_skill(skill_id: str, source_dir: str, dest_dir: str) -> bool:
    """Convert config.yaml + index.md to SKILL.md.
    Mirrors export_resolvers.rs:63 build_skill_md()"""
    skill_source = os.path.join(source_dir, "services", "skills", skill_id)
    if not os.path.isdir(skill_source):
        print(f"  WARNING: Skill directory not found: {skill_source}", file=sys.stderr)
        return False

    # Read description from config.yaml
    config_path = os.path.join(skill_source, "config.yaml")
    description = ""
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        if config and "description" in config:
            description = config["description"]

    # Read body from index.md or SKILL.md
    index_path = os.path.join(skill_source, "index.md")
    skill_md_path = os.path.join(skill_source, "SKILL.md")
    body = ""
    if os.path.exists(index_path):
        with open(index_path, "r") as f:
            body = strip_frontmatter(f.read())
    elif os.path.exists(skill_md_path):
        with open(skill_md_path, "r") as f:
            body = strip_frontmatter(f.read())
    else:
        body = f'$(systemprompt core skills show {skill_id} --raw 2>/dev/null || echo "Skill not available")'

    # Write SKILL.md
    kebab_name = to_kebab(skill_id)
    skill_dir = os.path.join(dest_dir, "skills", kebab_name)
    os.makedirs(skill_dir, exist_ok=True)

    escaped_desc = description.replace('"', '\\"')
    skill_md = f'---\nname: {kebab_name}\ndescription: "{escaped_desc}"\n---\n\n{body.strip()}\n'

    with open(os.path.join(skill_dir, "SKILL.md"), "w") as f:
        f.write(skill_md)

    # Copy auxiliary files (scripts/, references/, templates/, diagnostics/, data/, assets/)
    aux_dirs = ["scripts", "references", "templates", "diagnostics", "data", "assets"]
    for aux in aux_dirs:
        aux_source = os.path.join(skill_source, aux)
        if os.path.isdir(aux_source):
            aux_dest = os.path.join(skill_dir, aux)
            if os.path.exists(aux_dest):
                shutil.rmtree(aux_dest)
            shutil.copytree(aux_source, aux_dest)

    return True


def convert_agent(agent_id: str, source_dir: str, dest_dir: str) -> bool:
    """Convert agent YAML to agent .md.
    Mirrors export_resolvers.rs:229 build_agent_md()"""
    agents_dir = os.path.join(source_dir, "services", "agents")

    # Find the agent in YAML files
    for filename in os.listdir(agents_dir):
        if not filename.endswith(".yaml"):
            continue
        filepath = os.path.join(agents_dir, filename)
        with open(filepath, "r") as f:
            data = yaml.safe_load(f)

        if not data or "agents" not in data:
            continue

        if agent_id in data["agents"]:
            agent_data = data["agents"][agent_id]
            description = ""
            system_prompt = ""

            # Extract description from card
            card = agent_data.get("card", {})
            if card:
                description = card.get("description", "")

            # Extract system prompt from metadata
            metadata = agent_data.get("metadata", {})
            if metadata:
                system_prompt = metadata.get("systemPrompt", "")

            if not system_prompt:
                print(f"  WARNING: No systemPrompt found for agent {agent_id}", file=sys.stderr)
                return False

            # Write agent .md
            agents_dest = os.path.join(dest_dir, "agents")
            os.makedirs(agents_dest, exist_ok=True)

            escaped_desc = description.replace('"', '\\"')
            agent_md = f'---\nname: {agent_id}\ndescription: "{escaped_desc}"\n---\n\n{system_prompt.strip()}\n'

            with open(os.path.join(agents_dest, f"{agent_id}.md"), "w") as f:
                f.write(agent_md)

            return True

    print(f"  WARNING: Agent {agent_id} not found in any YAML file", file=sys.stderr)
    return False


def generate_plugin_json(plugin_name: str, plugin_config: dict, dest_dir: str):
    """Generate .claude-plugin/plugin.json for a plugin."""
    manifest = {
        "name": plugin_name,
        "description": plugin_config["description"],
        "version": plugin_config["version"],
        "author": {
            "name": "systemprompt.io",
            "email": "hello@systemprompt.io"
        }
    }

    plugin_dir = os.path.join(dest_dir, ".claude-plugin")
    os.makedirs(plugin_dir, exist_ok=True)

    with open(os.path.join(plugin_dir, "plugin.json"), "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")


def generate_settings_json(dest_dir: str):
    """Generate minimal settings.json for a plugin."""
    settings = {
        "permissions": {
            "allow": []
        }
    }
    with open(os.path.join(dest_dir, "settings.json"), "w") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")


def generate_mcp_json(dest_dir: str, mcp_servers: list):
    """Generate .mcp.json for plugins with MCP server references."""
    if not mcp_servers:
        return

    mcp_config = {
        "mcpServers": {}
    }
    for server in mcp_servers:
        mcp_config["mcpServers"][server] = {
            "type": "http",
            "url": f"https://systemprompt.io/api/v1/mcp/{server}/mcp"
        }

    with open(os.path.join(dest_dir, ".mcp.json"), "w") as f:
        json.dump(mcp_config, f, indent=2)
        f.write("\n")


def generate_marketplace_json(mapping: dict, marketplace_dir: str):
    """Generate top-level .claude-plugin/marketplace.json."""
    plugins = []
    for plugin_name, config in mapping.items():
        plugins.append({
            "name": plugin_name,
            "source": f"./plugins/{plugin_name}",
            "description": config["description"],
            "version": config["version"],
            "category": config["category"],
            "author": {
                "name": "systemprompt.io",
                "email": "hello@systemprompt.io"
            }
        })

    marketplace = {
        "name": "systemprompt-marketplace",
        "owner": {
            "name": "systemprompt.io",
            "email": "hello@systemprompt.io"
        },
        "metadata": {
            "description": "Development plugins for systemprompt.io codebases",
            "version": "1.0.0",
            "pluginRoot": "./plugins"
        },
        "plugins": plugins
    }

    mp_dir = os.path.join(marketplace_dir, ".claude-plugin")
    os.makedirs(mp_dir, exist_ok=True)

    with open(os.path.join(mp_dir, "marketplace.json"), "w") as f:
        json.dump(marketplace, f, indent=2)
        f.write("\n")


def main():
    parser = argparse.ArgumentParser(description="Convert systemprompt-web to marketplace plugin format")
    parser.add_argument("--source", required=True, help="Path to systemprompt-web repository")
    parser.add_argument("--dest", default=None, help="Path to marketplace output (default: parent of this script's repo)")
    args = parser.parse_args()

    source_dir = os.path.abspath(args.source)
    if args.dest:
        marketplace_dir = os.path.abspath(args.dest)
    else:
        marketplace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Load mapping
    map_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plugin-skills-map.json")
    with open(map_path, "r") as f:
        mapping = json.load(f)

    print(f"Source: {source_dir}")
    print(f"Destination: {marketplace_dir}")
    print()

    total_skills = 0
    total_agents = 0
    total_plugins = 0

    for plugin_name, config in mapping.items():
        plugin_dir = os.path.join(marketplace_dir, "plugins", plugin_name)
        os.makedirs(plugin_dir, exist_ok=True)

        print(f"Plugin: {plugin_name}")

        # Convert skills
        skill_count = 0
        for skill_id in config.get("skills", []):
            if convert_skill(skill_id, source_dir, plugin_dir):
                skill_count += 1
                print(f"  Skill: {skill_id} -> {to_kebab(skill_id)}/SKILL.md")

        # Convert agents
        agent_count = 0
        for agent_id in config.get("agents", []):
            if convert_agent(agent_id, source_dir, plugin_dir):
                agent_count += 1
                print(f"  Agent: {agent_id} -> agents/{agent_id}.md")

        # Generate plugin.json
        generate_plugin_json(plugin_name, config, plugin_dir)

        # Generate settings.json
        generate_settings_json(plugin_dir)

        # Generate .mcp.json if needed
        generate_mcp_json(plugin_dir, config.get("mcp_servers", []))

        print(f"  -> {skill_count} skills, {agent_count} agents")
        print()

        total_skills += skill_count
        total_agents += agent_count
        total_plugins += 1

    # Generate top-level marketplace.json
    generate_marketplace_json(mapping, marketplace_dir)
    print(f"Generated marketplace.json")

    print()
    print(f"Summary: {total_plugins} plugins, {total_skills} skills, {total_agents} agents")


if __name__ == "__main__":
    main()
