#!/usr/bin/env python3
"""
Jira MCP Server - Сервер Model Context Protocol для интеграции с Jira
"""
import os
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from jira import JIRA
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация MCP сервера
app = Server("jira-mcp-server")

# Глобальный клиент Jira
jira_client: Optional[JIRA] = None


def get_jira_client() -> JIRA:
    """Инициализация и возврат клиента Jira"""
    global jira_client

    if jira_client is None:
        jira_url = os.getenv("JIRA_URL")
        jira_email = os.getenv("JIRA_EMAIL")
        jira_api_token = os.getenv("JIRA_API_TOKEN")

        if not all([jira_url, jira_email, jira_api_token]):
            raise ValueError("Отсутствуют необходимые учетные данные Jira в переменных окружения")

        jira_client = JIRA(
            server=jira_url,
            token_auth=jira_api_token
        )
        logger.info(f"Подключено к Jira по адресу {jira_url}")

    return jira_client


@app.list_tools()
async def list_tools() -> List[Tool]:
    """Список доступных инструментов Jira"""
    return [
        Tool(
            name="get_issue",
            description="Получить детали задачи Jira по ключу (например, PROJ-123)",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {
                        "type": "string",
                        "description": "Ключ задачи Jira (например, PROJ-123)"
                    }
                },
                "required": ["issue_key"]
            }
        ),
        Tool(
            name="search_issues",
            description="Поиск задач Jira с использованием JQL (Jira Query Language)",
            inputSchema={
                "type": "object",
                "properties": {
                    "jql": {
                        "type": "string",
                        "description": "Строка JQL-запроса"
                    },
                    "max_results": {
                        "type": "number",
                        "description": "Максимальное количество результатов",
                        "default": 50
                    }
                },
                "required": ["jql"]
            }
        ),
        Tool(
            name="create_issue",
            description="Создать новую задачу в Jira",
            inputSchema={
                "type": "object",
                "properties": {
                    "project": {
                        "type": "string",
                        "description": "Ключ проекта"
                    },
                    "summary": {
                        "type": "string",
                        "description": "Краткое описание/заголовок задачи"
                    },
                    "description": {
                        "type": "string",
                        "description": "Подробное описание задачи"
                    },
                    "issue_type": {
                        "type": "string",
                        "description": "Тип задачи (например, Bug, Task, Story)",
                        "default": "Task"
                    }
                },
                "required": ["project", "summary"]
            }
        ),
        Tool(
            name="add_comment",
            description="Добавить комментарий к задаче Jira",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {
                        "type": "string",
                        "description": "Ключ задачи Jira"
                    },
                    "comment": {
                        "type": "string",
                        "description": "Текст комментария"
                    }
                },
                "required": ["issue_key", "comment"]
            }
        ),
        Tool(
            name="update_issue",
            description="Обновить статус или поля задачи Jira",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {
                        "type": "string",
                        "description": "Ключ задачи Jira"
                    },
                    "fields": {
                        "type": "object",
                        "description": "Поля для обновления (например, {\"summary\": \"Новый заголовок\"})"
                    }
                },
                "required": ["issue_key", "fields"]
            }
        ),
        Tool(
            name="get_transitions",
            description="Получить доступные переходы статусов для задачи Jira",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {
                        "type": "string",
                        "description": "Ключ задачи Jira"
                    }
                },
                "required": ["issue_key"]
            }
        ),
        Tool(
            name="transition_issue",
            description="Изменить статус задачи Jira",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {
                        "type": "string",
                        "description": "Ключ задачи Jira"
                    },
                    "transition": {
                        "type": "string",
                        "description": "Название или ID перехода"
                    }
                },
                "required": ["issue_key", "transition"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    """Обработка вызовов инструментов"""
    try:
        jira = get_jira_client()

        if name == "get_issue":
            issue = jira.issue(arguments["issue_key"])
            result = {
                "key": issue.key,
                "summary": issue.fields.summary,
                "description": issue.fields.description or "",
                "status": issue.fields.status.name,
                "assignee": issue.fields.assignee.displayName if issue.fields.assignee else "Не назначен",
                "reporter": issue.fields.reporter.displayName,
                "created": str(issue.fields.created),
                "updated": str(issue.fields.updated),
                "priority": issue.fields.priority.name if issue.fields.priority else "None",
                "issue_type": issue.fields.issuetype.name
            }
            return [TextContent(type="text", text=str(result))]

        elif name == "search_issues":
            max_results = arguments.get("max_results", 50)
            issues = jira.search_issues(arguments["jql"], maxResults=max_results)
            result = []
            for issue in issues:
                result.append({
                    "key": issue.key,
                    "summary": issue.fields.summary,
                    "status": issue.fields.status.name,
                    "assignee": issue.fields.assignee.displayName if issue.fields.assignee else "Не назначен"
                })
            return [TextContent(type="text", text=str(result))]

        elif name == "create_issue":
            issue_dict = {
                "project": {"key": arguments["project"]},
                "summary": arguments["summary"],
                "description": arguments.get("description", ""),
                "issuetype": {"name": arguments.get("issue_type", "Task")}
            }
            new_issue = jira.create_issue(fields=issue_dict)
            return [TextContent(type="text", text=f"Создана задача: {new_issue.key}")]

        elif name == "add_comment":
            jira.add_comment(arguments["issue_key"], arguments["comment"])
            return [TextContent(type="text", text=f"Комментарий добавлен к {arguments['issue_key']}")]

        elif name == "update_issue":
            issue = jira.issue(arguments["issue_key"])
            issue.update(fields=arguments["fields"])
            return [TextContent(type="text", text=f"Обновлена задача: {arguments['issue_key']}")]

        elif name == "get_transitions":
            transitions = jira.transitions(arguments["issue_key"])
            result = [{"id": t["id"], "name": t["name"]} for t in transitions]
            return [TextContent(type="text", text=str(result))]

        elif name == "transition_issue":
            jira.transition_issue(arguments["issue_key"], arguments["transition"])
            return [TextContent(type="text", text=f"Изменен статус задачи: {arguments['issue_key']}")]

        else:
            return [TextContent(type="text", text=f"Неизвестный инструмент: {name}")]

    except Exception as e:
        logger.error(f"Ошибка при выполнении инструмента {name}: {str(e)}")
        return [TextContent(type="text", text=f"Ошибка: {str(e)}")]


async def main():
    """Главная точка входа"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

