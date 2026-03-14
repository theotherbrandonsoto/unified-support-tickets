# Claude Desktop MCP Server Setup

This guide explains how to connect the Unified Support Tickets MCP server to Claude Desktop.

## What is the MCP Server?

The MCP (Model Context Protocol) server allows Claude Desktop to query your support metrics in plain English, like:

- "What's our SLA compliance by brand?"
- "Show me tickets from BrandB that missed SLA"
- "What are the top resolution patterns?"
- "Compare escalation rates across all brands"

## Installation Steps

### 1. Install Claude Desktop

Download Claude Desktop from [claude.ai](https://claude.ai) if you haven't already.

### 2. Start the MCP Server

First, navigate to your project directory and start the MCP server:

```bash
cd unified-support-tickets
python mcp_server.py
```

You should see output like:
```
INFO:     Uvicorn running on http://localhost:3000
```

### 3. Configure Claude Desktop

Open Claude Desktop and go to **Settings** → **Connected Apps** or **MCP Servers**.

Add a new MCP server with these details:

```json
{
  "name": "unified-support-tickets",
  "type": "stdio",
  "command": "python",
  "args": ["/path/to/mcp_server.py"]
}
```

Or, if you're running it as an HTTP server:

```json
{
  "name": "unified-support-tickets",
  "type": "http",
  "url": "http://localhost:3000"
}
```

Replace `/path/to` with the actual path to your `mcp_server.py` file.

### 4. Restart Claude Desktop

Close and reopen Claude Desktop to load the new MCP server configuration.

### 5. Start Querying

Now you can ask Claude Desktop questions about your support metrics:

**Examples:**

```
"What's the SLA compliance by brand?"
```
→ Returns a table with SLA compliance percentages for each brand

```
"Show me BrandB tickets that missed SLA"
```
→ Lists specific tickets from BrandB that didn't meet SLA

```
"What are the most common resolution patterns?"
```
→ Shows the top issue-to-resolution mappings with escalation rates

```
"Compare escalation rates across brands"
```
→ Displays escalation metrics for all 7 brands

## Available Queries

The MCP server provides these tools:

### `sla_compliance_overview`
Get SLA compliance metrics for all brands or a specific brand.

**Parameters:**
- `brand` (optional): Filter by brand name

**Example:**
```
"Tell me the SLA compliance for BrandA1"
```

### `ticket_volume_by_status`
Get ticket volume broken down by status (open, closed, in_progress, pending).

**Parameters:**
- `brand` (optional): Filter by brand name

**Example:**
```
"How many tickets are open vs closed across all brands?"
```

### `escalation_and_compensation`
Get escalation rates and financial compensation metrics.

**Parameters:**
- `brand` (optional): Filter by brand name

**Example:**
```
"What's our total compensation exposure by brand?"
```

### `resolution_patterns`
Analyze how different issues are resolved, with escalation and compensation data.

**Parameters:**
- `issue_type` (optional): Filter by issue type

**Example:**
```
"What are the most common ways we resolve login_issue?"
```

### `sla_missed_tickets`
Find specific tickets that missed SLA.

**Parameters:**
- `brand` (optional): Filter by brand name
- `limit` (optional): Number of results (default: 20)

**Example:**
```
"Show me the last 10 tickets from BrandC that missed SLA"
```

## Troubleshooting

### MCP Server Won't Start

**Error:** `ModuleNotFoundError: No module named 'duckdb'`

**Solution:**
```bash
pip install duckdb mcp
```

### Claude Desktop Can't Connect

1. Make sure the MCP server is running (you should see "Uvicorn running on...")
2. Check that the path to `mcp_server.py` is correct
3. Verify that the database file `unified_support_tickets.duckdb` exists in the same directory

### No Data Returned

1. Make sure you ran `dbt run` to create the metrics tables
2. Verify the database connection: `python -c "import duckdb; conn = duckdb.connect('unified_support_tickets.duckdb'); print(conn.execute('SELECT COUNT(*) FROM main.metrics_sla_resolution').df())"`

## Advanced Usage

### Natural Language Examples

The MCP server is designed to understand natural language queries. Here are examples Claude can handle:

```
"Which brand has the worst SLA compliance?"
→ Automatically calls sla_compliance_overview and identifies the lowest percentage

"Show me all escalated tickets from BrandA2"
→ Can drill down into specific ticket subsets

"What's the compensation rate across all brands?"
→ Queries escalation_and_compensation metrics

"How do we usually resolve billing problems?"
→ Calls resolution_patterns filtered to billing_problem
```

### Chaining Queries

Claude can now chain queries together:

```
"Compare SLA compliance between BrandA1 and BrandB, then show me 
the SLA-missed tickets from the worse-performing brand"
```

This will:
1. Call `sla_compliance_overview` for both brands
2. Identify which has lower compliance
3. Call `sla_missed_tickets` for that brand

## Next Steps

Once you have the MCP server running:

1. Ask Claude Desktop: **"What's our business health across all brands?"**
2. Request: **"Identify our top 3 improvement opportunities"**
3. Explore: **"Deep dive: why is BrandB's SLA compliance so low?"**

---

**Questions?** Check the main README.md for more context on the data model and metrics definitions.
