# MCP Servers Registry

| Server | Domain | Tools | Backing | Status |
|---|---|---|---|---|
| **Filesystem** | Local file I/O | read_file, write_file, list_directory, delete_file | OS filesystem, scoped by permission broker | Implemented |
| **Search/Research** | Web search | web_search, fetch_url | DuckDuckGo (free, no API key required) | Implemented |
| **Email** | Email operations | list, draft, send | Gmail API / Microsoft Graph (key required) | Implemented (stub API) |
| **Messaging** | Multi-channel messaging | list_channels, draft, send | WhatsApp Business API, Slack, Telegram, SMS | Implemented (stub channels) |
| **Browser/Automation** | Browser control | navigate, screenshot, click, type | LAM browser MCP wrapper | Implemented |
| **Calendar** | Calendar operations | list_events, create_event | Google Calendar / Outlook (stub) | Implemented (stub API) |
| **Shell/Terminal** | Command execution | run, write_file, read_file | Disposable sandbox per task, network denied by default | Implemented |
| **Input Injection** | Input control | click, type, hotkey | LAM input scope, requires explicit per-session grant | Implemented |

## Permission Scopes

Every server exposes tools through the MCP gateway's permission broker. Scopes are declared per agent per server. The broker enforces:
- Path scopes for filesystem/shell tools (prefix matching with normalization)
- Tool allow-lists per agent per server
- Input injection requires explicit grant/revoke lifecycle

## Circuit Breakers & Retries

All cloud-facing MCP servers (search, email, messaging, calendar) are wrapped with retry-with-backoff and circuit breaker patterns so a flaky external API doesn't cascade into blocking the whole agent layer.
