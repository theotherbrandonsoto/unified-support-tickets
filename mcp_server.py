#!/usr/bin/env python3
"""
MCP Server for Unified Support Tickets Metrics
Allows Claude Desktop to query support metrics in plain English
"""

import os
from typing import Any
import duckdb
from mcp.server import Server
from mcp.types import Tool, TextContent

# Initialize the MCP server
server = Server("unified-support-tickets-metrics")

# Get the database path
DB_PATH = os.path.join(os.path.dirname(__file__), "unified_support_tickets.duckdb")


def get_connection():
    """Get database connection"""
    return duckdb.connect(DB_PATH, read_only=True)


# Define tools
TOOLS = [
    {
        "name": "sla_compliance_overview",
        "description": "Get SLA compliance metrics for all brands",
        "input_schema": {
            "type": "object",
            "properties": {
                "brand": {
                    "type": "string",
                    "description": "Optional: Filter by brand",
                }
            },
        },
    },
    {
        "name": "ticket_volume_by_status",
        "description": "Get ticket volume by status",
        "input_schema": {
            "type": "object",
            "properties": {
                "brand": {
                    "type": "string",
                    "description": "Optional: Filter by brand",
                }
            },
        },
    },
    {
        "name": "escalation_and_compensation",
        "description": "Get escalation rates and compensation metrics",
        "input_schema": {
            "type": "object",
            "properties": {
                "brand": {
                    "type": "string",
                    "description": "Optional: Filter by brand",
                }
            },
        },
    },
    {
        "name": "resolution_patterns",
        "description": "Analyze resolution patterns",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "sla_missed_tickets",
        "description": "Find SLA-missed tickets",
        "input_schema": {
            "type": "object",
            "properties": {
                "brand": {
                    "type": "string",
                    "description": "Optional: Filter by brand",
                },
                "limit": {
                    "type": "integer",
                    "description": "Optional: Number of results",
                },
            },
        },
    },
]


@server.list_tools()
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


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> str:
    """Execute tool calls"""

    try:
        conn = get_connection()

        if name == "sla_compliance_overview":
            brand = arguments.get("brand", "")
            where_clause = f"WHERE brand = '{brand}'" if brand else ""
            query = f"""
            SELECT
                brand,
                COUNT(*) as total_tickets,
                SUM(CASE WHEN resolved_within_sla THEN 1 ELSE 0 END) as sla_compliant,
                ROUND(SUM(CASE WHEN resolved_within_sla THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as sla_compliance_pct
            FROM main_mart.fct_unified_support_tickets
            {where_clause}
            GROUP BY brand
            ORDER BY sla_compliance_pct DESC
            """

            result = conn.execute(query).fetchall()
            conn.close()

            text = "**SLA Compliance Overview**\n\n"
            text += "| Brand | Total | Compliant | Compliance % |\n"
            text += "|-------|-------|-----------|---------------|\n"
            for row in result:
                text += f"| {row[0]} | {row[1]} | {row[2]} | {row[3]}% |\n"

            return text

        elif name == "ticket_volume_by_status":
            brand = arguments.get("brand", "")
            where_clause = f"WHERE brand = '{brand}'" if brand else ""
            query = f"""
            SELECT
                brand,
                ticket_status,
                COUNT(*) as count
            FROM main_mart.fct_unified_support_tickets
            {where_clause}
            GROUP BY brand, ticket_status
            ORDER BY brand, count DESC
            """

            result = conn.execute(query).fetchall()
            conn.close()

            text = "**Ticket Volume by Status**\n\n"
            text += "| Brand | Status | Count |\n"
            text += "|-------|--------|-------|\n"
            for row in result:
                text += f"| {row[0]} | {row[1]} | {row[2]} |\n"

            return text

        elif name == "escalation_and_compensation":
            brand = arguments.get("brand", "")
            where_clause = f"WHERE brand = '{brand}'" if brand else "WHERE 1=1"
            query = f"""
            SELECT
                brand,
                ROUND(SUM(CASE WHEN escalated_to_management THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as escalation_rate_pct,
                ROUND(SUM(financial_compensation), 2) as total_compensation,
                ROUND(AVG(financial_compensation), 2) as avg_compensation
            FROM main_mart.fct_unified_support_tickets
            {where_clause}
            GROUP BY brand
            ORDER BY escalation_rate_pct DESC
            """

            result = conn.execute(query).fetchall()
            conn.close()

            text = "**Escalation & Compensation**\n\n"
            text += "| Brand | Escalation % | Total $ | Avg $ |\n"
            text += "|-------|--------------|---------|-------|\n"
            for row in result:
                text += f"| {row[0]} | {row[1]}% | ${row[2]:,.0f} | ${row[3]:.2f} |\n"

            return text

        elif name == "resolution_patterns":
            query = """
            SELECT
                primary_issue,
                resolution_label,
                COUNT(*) as frequency
            FROM main_mart.fct_unified_support_tickets
            GROUP BY primary_issue, resolution_label
            HAVING COUNT(*) > 20
            ORDER BY frequency DESC
            LIMIT 15
            """

            result = conn.execute(query).fetchall()
            conn.close()

            text = "**Top Resolution Patterns**\n\n"
            text += "| Issue | Resolution | Count |\n"
            text += "|-------|-----------|-------|\n"
            for row in result:
                text += f"| {row[0]} | {row[1]} | {row[2]} |\n"

            return text

        elif name == "sla_missed_tickets":
            brand = arguments.get("brand", "")
            limit = arguments.get("limit", 20)
            where_clause = f"AND brand = '{brand}'" if brand else ""
            query = f"""
            SELECT
                brand,
                ticket_id,
                primary_issue
            FROM main_mart.fct_unified_support_tickets
            WHERE NOT resolved_within_sla
            {where_clause}
            LIMIT {limit}
            """

            result = conn.execute(query).fetchall()
            conn.close()

            if not result:
                return "No SLA-missed tickets found"

            text = f"**SLA-Missed Tickets** ({len(result)} results)\n\n"
            text += "| Brand | Ticket ID | Issue |\n"
            text += "|-------|-----------|-------|\n"
            for row in result:
                text += f"| {row[0]} | {row[1]} | {row[2]} |\n"

            return text

        else:
            conn.close()
            return f"Unknown tool: {name}"

    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting MCP Server for Unified Support Tickets")
    print("📊 Database: unified_support_tickets.duckdb")
    print("🔗 Server: http://localhost:3000")
    print("\n✅ Server is running.\n")
    
    uvicorn.run(server, host="localhost", port=3000)
