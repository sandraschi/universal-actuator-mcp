# universal-actuator-mcp (MCPB Bundle)

Fleet-wide Federation Gateway (Robotics, Media, Infrastructure, Knowledge)

## Usage

Add to \claude_desktop_config.json\:
\\\json
{
  "mcpServers": {
    "universal-actuator-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "\D:\Dev\repos", "python", "-m", "universal_actuator_mcp"],
      "env": { "PYTHONPATH": "\D:\Dev\repos/src" }
    }
  }
}
\\\

## Tools

- **universal_actuator**: universal_actuator
- **search_library**: search_library

## Requirements

- Python 3.12+
- uv
