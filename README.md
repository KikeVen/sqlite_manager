# Context-Driven - (MCP) SQLite Server Manager

![Python](https://img.shields.io/badge/python-3.10+-blue?style=flat-square)
![SQLite](https://img.shields.io/badge/SQLite-local--first-003B57?style=flat-square&logo=sqlite)
![MCP](https://img.shields.io/badge/MCP-server-8A2BE2?style=flat-square)
![Platform](https://shields.io/badge/platform-cross--platform-4B0082?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

An enterprise-grade **Model Context Protocol (MCP) Server v2** implementation designed to **manage local SQLite databases dynamically** through LLM chat sessions. This server provides AI agents (such as Claude Desktop, Cursor, and VS Code) with deep schema inspection, secure read/write capabilities, multi-statement ACID transactions, and structural database optimization tools natively via STDIO.

## 🚀 Key Features

* **Zero-Config Stateless Sessions:** Pass the target database file path directly within your chat session text—no hardcoded environment variables required.
* **Multi-Platform Target Compatibility:** Natively parses and handles Windows absolute path strings (`C:\data\db.sqlite`) as well as macOS and Linux paths (`/var/db/app.db`) without configuration changes.
* **Deep Schema Inspection:** Structural tools to dynamically extract schemas, tables, columns, indexes, and active foreign key constraints.
* **Strict Security Boundaries:** Built-in read-only query paths enforcement using system-level database structures to prevent unauthorized modifications.
* **Transactional Pipeline Execution:** Execute sequential modification loops within a secure rollback transaction boundary.
* **Built-in Maintenance Hooks:** Native optimization commands supporting automated database defragmentation (`VACUUM`), data planner analytics (`ANALYZE`), and database validation checks (`integrity_check`).

---

## 🛠️ System Requirements & Prerequisites

* **Operating System:** Windows 10 / 11, macOS, or Linux.
* **Python Environment:** Python 3.10 or higher.
* **Supported Clients:** Any Model Context Protocol host client (Claude Desktop App, Cursor, Zed, etc.).

---

## 📦 Installation & Setup Guide

### 1. Clone & Initialize the Project Workspace

Open your preferred terminal window (such as PowerShell or Command Prompt on Windows) and run:

```bash
# Clone the repository workspace
git clone https://github.com/KikeVen/sqlite-manager.git
cd sqlite-manager

# Build an isolated Python virtual environment
python -m venv venv
```

### 2. Activate Environment & Install Dependencies

Activate the virtual environment according to your operating system platform:

**On Windows (PowerShell):**

```powershell
.\sqlite-manager\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**

```cmd
.\sqlite-manager\Scripts\activate.bat
```

**On macOS / Linux:**

```bash
source sqlite-manager/bin/activate
```

Install the production dependencies utilizing the provided tracking file:

```bash
pip install -r requirements.txt
```

---

## ⚙️ LLM Integration Configuration

To integrate this utility with your preferred AI client application, link the executable environment directly via your system config path.

### Claude Desktop Integration

Navigate to your active system app settings path:

* **Windows Configuration Path:** `%APPDATA%\Claude\claude_desktop_config.json`
* **macOS Configuration Path:** `~/Library/Application Support/Claude/claude_desktop_config.json`

Add or merge the following block inside your configuration schema:

```json
{
  "mcpServers": {
    "sqlite-manager": {
      "command": "C:\\absolute\\path\\to\\mcp-sqlite-env\\Scripts\\python.exe",
      "args": ["C:\\absolute\\path\\to\\server.py"]
    }
  }
}
```

> ⚠️ **Important:** Ensure you replace the absolute file path tokens with the true location pointers on your disk. On Windows systems, escape all folder separators using double backslashes (`\\`).

---

## 💡 Conversational Chat Usage

Once integrated, your LLM agent will dynamically recognize the tools and extract the file paths out of your conversational phrasing. There is no separate setup script required.

### Example Prompts to Try

* *"Using `sqlite-manager` check my SQLite database structure at `C:/Data/app.db` and output a full list of all available tables."*
* *"Using `sqlite-manager` run a structural analysis of the users table inside `/Users/username/Projects/analytics.db` to show its columns and keys."*
* *"Using `sqlite-manager` execute a SELECT query over the items table in `C:\Cache\local.db` to extract records where the total is greater than 500."*
* *"Using `sqlite-manager` optimize the database file page size located at `/var/lib/store.db` using a vacuum operation."*

---

## 🛠️ Core Tool Specification Sheet

This server exposes the following functional tool endpoints to your LLM agent:

| Tool Method Identifier | Parameter Arguments | Core Operational Focus |
| :--- | :--- | :--- |
| `list_tables` | `db_path` | Returns an array string containing all tracking tables and active database views. |
| `describe_table` | `db_path`, `table_name` | Pulls table layout structures including columns, constraints, and indexes. |
| `execute_read_query` | `db_path`, `sql_query` | Securely runs read-only data evaluation lookups using `PRAGMA query_only`. |
| `execute_write_query` | `db_path`, `sql_query`, `params` | Handles mutation cycles like `INSERT`, `UPDATE`, or structural `ALTER TABLE` changes. |
| `execute_transaction` | `db_path`, `sql_queries` | Loops multiple operational updates safely within an atomic ACID rollback block. |
| `optimize_and_maintain` | `db_path`, `operation` | Performs low-level runtime engine processes: `vacuum`, `analyze`, or `integrity_check`. |

---

## 📄 License

Distributed under the MIT License. See `LICENSE` file for more details.
