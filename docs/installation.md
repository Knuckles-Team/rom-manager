# Installation

## PyPI

```bash
pip install rom-manager            # core CLI + Api facade
pip install "rom-manager[mcp]"     # + MCP server (rom-manager-mcp)
pip install "rom-manager[agent]"   # + A2A agent server (rom-manager-agent)
pip install "rom-manager[native]"  # + patool (archive extraction)
pip install "rom-manager[all]"     # everything
```

## From source

```bash
git clone https://github.com/Knuckles-Team/rom-manager
pip install -e ".[all]"
```

## External binaries (required for conversion)

`rom-manager` shells out to native tools for the actual conversion. Install the
ones you need:

- **`chdman`** (CHD output) — Ubuntu: `apt install mame-tools`; Windows: install
  MAME tools from <https://github.com/mamedev/mame/releases> and add to `PATH`.
- **`dolphin-tool`** (RVZ output) — see
  <https://github.com/dolphin-emu/dolphin#dolphintool-usage>.
- **`7z` / archive backends** (extraction) — Ubuntu: `apt install p7zip-full`;
  required by the `patool` native extra.

The Python package installs cleanly without these binaries; only the conversion
*actions* require them at runtime.
