# Grimoire Core

Grimoire Core is the shared library used by all Grimoire bots.

Its main goal is to hide the complexity of interacting with Google Sheets behind a typed, object-oriented API. Instead of working with cells, ranges and JSON blobs, bots work with Python models and controllers.

## Core Concepts

### Rows

A sheet row is represented as a typed Python class.

```python
class CemeteryRow(Row):
    Name: str
    Discord_id: str
    Turn_of_death: int
    Resources: JsonData[Resource, int]
```

Fields are automatically serialized to and from spreadsheet values.

---

### Controllers

Each worksheet is represented by a controller.

```python
class CemeteryController(SheetsControllerBase[CemeteryRow]):
    def __init__(self):
        super().__init__(CEMETERY_SHEET_ID, CemeteryRow)
```

Controllers provide a high-level API for:

- loading sheet data
- caching data in memory
- querying rows
- updating rows
- inserting rows
- deleting rows
- batch operations

without exposing the underlying Google Sheets API.

---

### Business Logic

Application code interacts exclusively with rows and controllers.

```python
pj = PJsController().get_pj_row(user_id)

dead = CemeteryRow(
    Name=pj.Name,
    Discord_id=pj.Discord_id,
    ...
)

CemeteryController().insert_row(dead)
PJsController().delete_row(pj)
```

Notice that no spreadsheet-specific code appears in the command itself. Controllers encapsulate all communication with Google Sheets.

## Features

- Typed row models
- Typed sheet controllers
- Automatic serialization
- JSON column support
- In-memory caching
- Batch updates
- Singleton controllers
- Shared Discord bot utilities

## Philosophy

Google Sheets is treated as the application's database.

Each worksheet becomes a repository, each row becomes a model, and Discord commands focus solely on business logic.