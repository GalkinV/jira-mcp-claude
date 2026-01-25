# Jira MCP Server

MCP (Model Context Protocol) сервер для интеграции с Jira.

## Возможности

- **get_issue** - Получить детали задачи по ключу
- **search_issues** - Поиск задач через JQL
- **create_issue** - Создать новую задачу
- **add_comment** - Добавить комментарий к задаче
- **update_issue** - Обновить поля задачи
- **get_transitions** - Получить доступные переходы статусов
- **transition_issue** - Изменить статус задачи

## Установка

### 1. Настройте .env файл

Отредактируйте `.env` и укажите ваши данные Jira:

```bash
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token
```

Получить API токен через UI jira

### 2. Запуск через Docker

```bash
docker-compose up -d
```


## Использование с Claude Desktop

Добавьте в конфигурацию Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "jira": {
      "command": "docker",
      "args": [
        "exec",
        "-i",
        "jira-mcp-server",
        "python",
        "jira_mcp_server.py"
      ]
    }
  }
}
```

## Использование с Claude CLI

```shell
claude mcp add jira --scope user -- docker exec -i jira-mcp-server python jira_mcp_server.py
```

## Примеры использования

После подключения к Claude вы можете:

- "Покажи задачу PROJ-123"
- "Найди все открытые баги в проекте PROJ"
- "Создай новую задачу в проекте PROJ с названием 'Fix login bug'"
- "Добавь комментарий к PROJ-123: 'Работа завершена'"
- "Измени статус PROJ-123 на In Progress"

## Разработка

Структура проекта:
```
├── jira_mcp_server.py     # Основной код сервера
├── requirements.txt        # Python зависимости
├── Dockerfile             # Docker образ
├── docker-compose.yml     # Docker Compose конфигурация
├── .env                   # Переменные окружения
└── README.md              # Документация
```
