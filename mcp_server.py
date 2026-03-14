#!/usr/bin/env python3
"""
MCP Server for Unified Support Tickets Metrics
Allows Claude Desktop to query support metrics in plain English
"""

import json
import os
from typing import Any

import duckdb
from mcp.server.models import InitializationOptions
from mcp.server import Server
from mcp.types import Tool, TextContent, ToolResult

# Initialize the MCP server
app = Server("unified-support-tickets-metrics")

# Get the database path
DB_PATH = os.path.join(os.path.dirname(__file__), "unified_support_tickets.duckdb")


def get_connection():
    """Get database connection"""
    return duckdb.connect(DB_PATH, read_only=True)


# Define tools
TOOLS = [
    {
        "name": "sla_compliance_overview",
        "description": "Get SLA compliance metrics for all brands. Shows compliance percentage, total tickets, and SLA-compliant vs missed tickets.",
        "input_schema": {
            "type": "object",
            "properties": {
                "brand": {
                    "type": "string",
                    "description": "Optional: Filter by specific brand (e.g., 'BrandA1', 'BrandB'). Leave empty to see all brands.",
                }
            },
            "required": [],
        },
    },
    {
        "name": "ticket_volume_by_status",
        "description": "Get ticket volume broken down by status and optionally by brand. Shows count and percentage distribution.",
        "input_schema": {
            "type": "object",
            "properties": {
                "brand": {
                    "type": "string",
                    "description": "Optional: Filter by specific brand. Leave empty to see all brands.",
                }
            },
            "required": [],
        },
    },
    {
        "name": "escalation_and_compensation",
        "description": "Get escalation rates and financial compensation metrics by brand. Shows escalation percentage, total compensation, and tickets with compensation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "brand": {
                    "type": "string",
                    "description": "Optional: Filter by specific brand. Leave empty to see all brands.",
                }
            },
            "required": [],
        },
    },
    {
        "name": "resolution_patterns",
        "description": "Analyze how different issues are resolved. Shows frequency, escalation rates, and SLA compliance by issue type and resolution method.",
        "input_schema": {
            "type": "object",
            "properties": {
                "issue_type": {
                    "type": "string",
                    "description": "Optional: Filter by specific issue type (e.g., 'login_issue', 'billing_problem'). Leave empty to see top patterns.",
                }
            },
            "required": [],
        },
    },
    {
        "name": "sla_missed_tickets",
        "description": "Find specific tickets that missed SLA. Useful for root cause analysis and improvement opportunities.",
        "input_schema": {
            "type": "object",
            "properties": {
                "brand": {
                    "type": "string",
                    "description": "Optional: Filter by specific brand.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Optional: Number of results to return (default: 20).",
                },
            },
            "required": [],
        },
    },
]


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools"""
    return [
        Tool(
            name=tool["name"],
            description=tool["description"],
            inputSchema=tool["input_schema"],
        )
        for tool in TOOLS
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[ToolResult]:
    """Execute tool calls"""

    try:
        conn = get_connection()

        if name == "sla_compliance_overview":
            brand = arguments.get("brand", "")
            where_clause = f"WHERE brand = '{brand}'" if brand else ""
            query = f"""
            SELECT
                brand,
                total_tickets,
                sla_compliant_tickets,
                sla_missed_tickets,
                sla_compliance_pct
            FROM main.metrics_sla_resolution
            {where_clause}
            ORDER BY sla_compliance_pct DESC
            """

            result = conn.execute(query).fetchall()
            conn.close()

            if not result:
                return [ToolResult(content=[TextContent(text=f"No data found")])]

            text = "**SLA Compliance Overview**\n\n"
            text += "| Brand | Total | Compliant | Missed | Compliance % |\n"
            text += "|-------|-------|-----------|--------|---------------|\n"
            for row in result:
                text += f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]}% |\n"

            return [ToolResult(content=[TextContent(text=text)])]

        elif name == "ticket_volume_by_status":
            brand = arguments.get("brand", "")
            where_clause = f"AND brand = '{brand}'" if brand else ""
            query = f"""
            SELECT
                brand,
                ticket_status,
                ticket_count,
                pct_of_brand
            FROM main.metrics_volume_distribution
            WHERE metric_type = 'by_brand_status'
            {where_clause}
            ORDER BY brand, ticket_count DESC
            """

            result = conn.execute(query).fetchall()
            conn.close()

            text = "**Ticket Volume by Status**\n\n"
            text += "| Brand | Status | Count | % |\n"
            text += "|-------|--------|-------|----|\n"
            for row in result:
                text += f"| {row[0]} | {row[1]} | {row[2]} | {row[3]}% |\n"

            return [ToolResult(content=[TextContent(text=text)])]

        elif name == "escalation_and_compensation":
            brand = arguments.get("brand", "")
            where_clause = f"WHERE brand = '{brand}'" if brand else "WHERE brand IS NOT NULL"
            query = f"""
            SELECT
                brand,
                escalation_rate_pct,
                total_compensation,
                avg_compensation_per_ticket,
                compensation_rate_pct
            FROM main.metrics_quality_escalation
            {where_clause}
            ORDER BY escalation_rate_pct DESC
            """

            result = conn.execute(query).fetchall()
            conn.close()

            text = "**Escalation & Compensation**\n\n"
            text += "| Brand | Escalation % | Total $ | Avg $ | Comp Rate % |\n"
            text += "|-------|--------------|---------|-------|-------------|\n"
            for row in result:
                text += f"| {row[0]} | {row[1]}% | ${row[2]:,.0f} | ${row[3]:.2f} | {row[4]}% |\n"

            return [ToolResult(content=[TextContent(text=text)])]

        elif name == "resolution_patterns":
            query = """
            SELECT
                primary_issue,
                resolution_label,
                COUNT(*) as frequency,
                ROUND(SUM(CASE WHEN escalated_to_management THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as escalation_pct,
                ROUND(AVG(financial_compensation), 2) as avg_comp
            FROM main_mart.fct_unified_support_tickets
            GROUP BY primary_issue, resolution_label
            HAVING COUNT(*) > 20
            ORDER BY frequency DESC
            LIMIT 15
            """

            result = conn.execute(query).fetchall()
            conn.close()

            text = "**Top Resolution Patterns**\n\n"
            text += "| Issue | Resolution | Count | Escalation % | Avg $ |\n"
            text += "|-------|-----------|-------|--------------|-------|\n"
            for row in result:
                text += f"| {row[0]} | {row[1]} | {row[2]} | {row[3]}% | ${row[4]} |\n"

            return [ToolResult(content=[TextContent(text=text)])]

        elif name == "sla_missed_tickets":
            brand = arguments.get("brand", "")
            limit = arguments.get("limit", 20)
            where_clause = f"AND brand = '{brand}'" if brand else ""
            query = f"""
            SELECT
                brand,
                ticket_id,
                received_date,
                primary_issue,
                ticket_status
            FROM main_mart.fct_unified_support_tickets
            WHERE NOT resolved_within_sla
            {where_clause}
            ORDER BY received_date DESC
            LIMIT {limit}
            """

            result = conn.execute(query).fetchall()
            conn.close()

            if not result:
                return [ToolResult(content=[TextContent(text="No SLA-missed tickets found")])]

            text = f"**SLA-Missed Tickets**\n\n"
            text += "| Brand | Ticket ID | Received | Issue |\n"
            text += "|-------|-----------|----------|-------|\n"
            for row in result:
                text += f"| {row[0]} | {row[1]} | {row[2]:.10} | {row[3]} |\n"

            return [ToolResult(content=[TextContent(text=text)])]

        else:
            conn.close()
            return [ToolResult(content=[TextContent(text=f"Unknown tool: {name}")])]

    except Exception as e:
        return [ToolResult(content=[TextContent(text=f"Error: {str(e)}")])]


if __name__ == "__main__":
    import uvicorn

    # Run the server
    uvicorn.run(app, host="localhost", port=3000)
