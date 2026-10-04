# Einrichtung der Werkzeuge (Linux Mint)

Stand: 2026-10-04, Linux Mint 22.3 (Basis Ubuntu 24.04 „noble“), x86_64.

Vorher schon vorhanden: git, VS Code mit Claude-Code-Erweiterung, Python 3.12, `uv`.

## Übersicht

| Werkzeug | Version | Quelle | Ort |
|---|---|---|---|
| KiCad (inkl. Symbole, Footprints, 3D) | 10.0.6 | PPA `kicad/kicad-10.0-releases` | System |
| ngspice | 42 | Ubuntu-Paket | System |
| atopile (`ato`) | 0.15.9 | `uv tool` mit Python 3.14 | `~/.local/bin/ato` |
| atopile-Erweiterung für VS Code | 0.15.9 | VS Code Marketplace | VS Code |
| Java 25 (für Freerouting) | 25.0.4 | Ubuntu-Paket `openjdk-25-jre` | System |
| Freerouting | 2.4.1 | GitHub-Release (`.jar`) | `~/tools/freerouting/` |
| KiCad-MCP-Server (Seeed-Studio) | git `main` | GitHub | `~/tools/kicad-mcp-server/` |

## 1. Systempakete (mit sudo)

```bash
sudo add-apt-repository -y ppa:kicad/kicad-10.0-releases
sudo apt update
sudo apt install -y kicad ngspice openjdk-25-jre python3.12-venv
```

- `kicad` holt automatisch Symbole, Footprints und 3D-Modelle (mehrere GB) sowie `kicad-cli` und das Python-Modul `pcbnew`.
- `openjdk-25-jre`: Freerouting 2.4 braucht mindestens Java 25.
- `python3.12-venv`: wird für die Python-Umgebung des MCP-Servers gebraucht.

Prüfen:

```bash
kicad-cli version            # 10.0.6
ngspice --version            # ngspice-42
python3 -c "import pcbnew; print(pcbnew.Version())"
```

## 2. atopile

```bash
uv tool install --python 3.14 atopile
code --install-extension atopile.atopile
ato --version                # 0.15.9
```

**Wichtig:** atopile ab 0.15 verlangt Python 3.14. Ohne `--python 3.14` nimmt `uv` das System-Python 3.12 und installiert die veraltete Version 0.2.x, ohne zu warnen. Das Python 3.14 lädt `uv` selbst herunter. Ubuntu 24.04 hat kein Python 3.14 in seinen Paketquellen.

Aktualisieren: `uv tool upgrade atopile`

## 3. Freerouting

```bash
mkdir -p ~/tools/freerouting && cd ~/tools/freerouting
curl -LO https://github.com/freerouting/freerouting/releases/download/v2.4.1/freerouting-2.4.1.jar
```

Starter `~/.local/bin/freerouting` (ausführbar):

```sh
#!/bin/sh
# Freerouting 2.4 braucht Java 25 (Paket openjdk-25-jre)
exec /usr/lib/jvm/java-25-openjdk-amd64/bin/java -jar "$HOME/tools/freerouting/freerouting-2.4.1.jar" "$@"
```

Aufruf ohne Oberfläche (so nutzt ihn der Workflow):

```bash
freerouting --gui.enabled=false -de board.dsn -do board.ses
```

Ohne `--gui.enabled=false` öffnet sich die grafische Oberfläche, auch bei `--version`.

## 4. KiCad-MCP-Server

Über den MCP-Server prüft Claude Code Netze, ERC/DRC und die Stückliste (BOM) direkt in den KiCad-Dateien.

```bash
cd ~/tools
git clone https://github.com/Seeed-Studio/kicad-mcp-server.git
cd kicad-mcp-server
/usr/bin/python3 -m venv --system-site-packages .venv
.venv/bin/pip install -e . fastmcp
claude mcp add kicad -s user -- ~/tools/kicad-mcp-server/.venv/bin/python -m kicad_mcp_server
claude mcp get kicad         # Status: ✔ Connected
```

- `--system-site-packages` gibt der Umgebung Zugriff auf KiCads `pcbnew`. Das ist nötig für die volle Platinenanalyse.
- Hinweise von `pip` zu `yubikey-manager`/`cryptography` betreffen nur diese Umgebung, nicht das System.
- `-s user`: Der Server gilt für alle Projekte dieses Benutzers.
- Neu geladen wird er erst in einer **neuen** Claude-Code-Sitzung.

Aktualisieren: `git pull` und danach `.venv/bin/pip install -e .` im Ordner `~/tools/kicad-mcp-server`.

## Noch nicht installiert

- **Firmware-Werkzeuge** (PlatformIO bzw. Compiler und Programmer). Sie kommen nach der Wahl des Mikrocontrollers in Phase 2.
