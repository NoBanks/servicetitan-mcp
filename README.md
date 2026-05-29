# servicetitan-mcp

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io)

MCP server for [ServiceTitan](https://servicetitan.com), the dominant vertical SaaS for home services and trades (HVAC, plumbing, electrical, garage door, pest control, landscaping, pool). 5 tools for AI receptionists and dispatchers to search customers, check live appointment availability from Scheduling Pro, create booking requests in the dispatcher Calls inbox, query jobs by status, and read job details.

As of May 2026, ServiceTitan does not ship an official business-focused MCP server. The only official `@servicetitan/anvil2-mcp` package is restricted to React design-system component docs. This is the production-quality, install-ready Python rail for AI agents to natively manage ServiceTitan tenants.

## The 5 tools

| Tool | Purpose |
|---|---|
| `search_customers` | Find existing customers by name, phone, or email |
| `get_available_slots` | Check live open booking windows from Scheduling Pro |
| `create_booking_request` | Create a pending booking in the dispatcher Calls inbox (the AI receptionist's primary write action) |
| `list_jobs` | Query, filter, and paginate jobs by status or modified-since timestamp |
| `get_job_details` | Read full job details including customer history notes |

## Install

```bash
pip install servicetitan-mcp
```

## Configure

ServiceTitan uses OAuth 2.0 Client Credentials flow. You need 4 environment variables:

```bash
export SERVICETITAN_CLIENT_ID="your-oauth-client-id"
export SERVICETITAN_CLIENT_SECRET="your-oauth-client-secret"
export SERVICETITAN_APP_KEY="your-app-key"
export SERVICETITAN_TENANT_ID="your-tenant-id"
```

Get all four in your ServiceTitan Developer Portal. The client_secret and app_key are sensitive, keep them server-side. The MCP client handles automatic token renewal (ServiceTitan access tokens expire every 15 minutes with no refresh tokens, so the client re-auths transparently when needed).

## Use with Claude Desktop

```json
{
  "mcpServers": {
    "servicetitan": {
      "command": "servicetitan-mcp",
      "env": {
        "SERVICETITAN_CLIENT_ID": "your-oauth-client-id",
        "SERVICETITAN_CLIENT_SECRET": "your-oauth-client-secret",
        "SERVICETITAN_APP_KEY": "your-app-key",
        "SERVICETITAN_TENANT_ID": "your-tenant-id"
      }
    }
  }
}
```

Restart Claude Desktop. The 5 ServiceTitan tools are now available.

## Use case: AI receptionist for a trades business

Typical agent flow for an inbound service call:

1. Call `search_customers(phone="...")` to check whether the caller is an existing customer
2. Call `get_available_slots(startsOnOrAfter, endsOnOrBefore)` to see what time windows are open for booking
3. Offer the windows to the caller, ask which works
4. Call `create_booking_request(name, summary, phone, address...)` to create a pending request in the dispatcher Calls inbox. A human dispatcher confirms and converts it to a scheduled job.

For customer status queries (e.g. "is my technician on the way?"):

1. Call `search_customers(name="...")` to find the customer
2. Call `list_jobs(modifiedOnOrAfter="<today>")` to find their open job
3. Call `get_job_details(jobId)` to read the latest status and notes

## Architecture

- Public MIT-licensed wrapper around the ServiceTitan V2 REST API
- Async HTTP via `httpx`
- pydantic v2 input validation
- OAuth 2.0 Client Credentials with automatic 15-minute token renewal
- Dual-header auth: `Authorization: Bearer <token>` PLUS `ST-App-Key: <key>` on every business API call
- Tenant-scoped: every endpoint is scoped per tenant_id in the URL path
- Rate-limit aware (429 returns a clean error; ServiceTitan caps regular APIs at 60 req/sec per tenant)

## Safety note

ServiceTitan API terms restrict caching retrieved data for longer than 24 hours. The MCP does not cache responses beyond an in-process request lifetime, which keeps you compliant by default. The `create_booking_request` action creates a PENDING booking (not a confirmed job), so a human dispatcher remains in the loop for the final schedule. This is the intended safe pattern for AI receptionists.

## Development

```bash
git clone https://github.com/NoBanks/servicetitan-mcp.git
cd servicetitan-mcp
pip install -e ".[dev]"
pytest
```

## License

MIT. See [LICENSE](LICENSE).

## Author

Ryan Hammer (NoBanks). Solo founder + engineer. Built this and 11 other MCP servers as part of a sprint to expose AI agent rails for the products and platforms shipping daily.

- GitHub: [@NoBanks](https://github.com/NoBanks)
- X/Twitter: [@livingagentic](https://x.com/livingagentic)
- Site: [livingagentic.me](https://livingagentic.me), [nohumannearby.com](https://nohumannearby.com)

Open to AI engineering roles, contract or full-time, remote-only.
