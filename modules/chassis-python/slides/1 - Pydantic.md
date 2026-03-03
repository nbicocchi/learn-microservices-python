# Introduction to Pydantic

https://docs.pydantic.dev/latest/

## What is Pydantic?

**Pydantic is a Python library that helps you define data models with automatic validation and parsing.**  

In real-world applications, especially when dealing with **databases**, or **user input**, the data you receive may not always be:

- Complete
- Correctly typed
- Safe to use

Pydantic helps you:

1. **Validate** input data (e.g., an email must be valid).
2. **Parse** strings into proper types (e.g., `"2025-08-15"` into a `datetime` object).
3. **Avoid boilerplate code** for checking and cleaning data manually.
4. **Integrate easily** with frameworks like **FastAPI** and **Django**.

## Pydantic BaseModel

`BaseModel` is the main super-class provided by Pydantic to turn into managed classes your regular classes.

```python
from pydantic import BaseModel, EmailStr, ValidationError

class User(BaseModel):
    email: EmailStr
    password: str
    

User("mail@mail.com", "secret") # OK
User(42, 3.14)  # raise ValidationError
```

## Annotations
In Python, **`Annotated`** is a special type hint from the `typing` module (or `typing_extensions` in older versions) that lets you **attach metadata to a type**. This metadata can be used by tools, frameworks, or libraries, without affecting the runtime type itself. Essentially, it’s a way to **add extra information to a type hint**.

### Basic Syntax

```python
from typing import Annotated

# Annotated[type, metadata1, metadata2, ...]
x: Annotated[int, "This is a positive integer"] = 42
```

* `int` → the actual type of `x`.
* `"This is a positive integer"` → metadata (a description, constraint, or anything a tool might use).

---

### With Multiple Metadata

```python
from typing import Annotated

x: Annotated[int, "positive", "less than 100"] = 10
```

* Here, both `"positive"` and `"less than 100"` are attached as metadata.
* Python itself **ignores these at runtime**, but tools can use them.

---

### Practical Example with `pydantic` or `FastAPI`

`Annotated` is especially useful in frameworks that perform **runtime validation**:

```python
from typing import Annotated
from pydantic import BaseModel, Field

class User(BaseModel):
    age: Annotated[int, Field(gt=0, lt=120)]  # age must be >0 and <120

user = User(age=25)  # ✅ OK
# user = User(age=-5)  # ❌ Validation error
```

## Configuration

In modern software development, it's crucial to separate configuration from code.
**Environment variables** are key to achieving this. They're dynamic, named values that are external to your application's source code, allowing you to change the behavior of your application without modifying the code itself.

Why are they so important?

- **Security**: They let you manage sensitive information like API keys, database credentials, and secret keys securely. Instead of hard-coding them directly into your application, you store them as environment variables. This prevents them from being accidentally committed to version control systems like Git, where they could be exposed.
- **Flexibility**: Environment variables make your application portable across different environments. You can use one codebase for development, testing, and production, and simply change the environment variables to point to the correct database, API endpoint, or other service for each environment. For example, your DATABASE_URL can point to a local database for development and to a production database when deployed.
- **Decoupling**: They promote a clean separation between your application's logic and its configuration. This makes your code cleaner, more maintainable, and easier to test.


```python
import os
import yaml
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = False
    database_url: str = ""

    class Config:
        env_prefix = ""  # optional, can prefix variables like APP_

def load_settings(path="settings.yaml") -> Settings:
    with open(path, "r") as f:
        cfg = yaml.safe_load(f)

    settings = Settings(
        host=cfg.get("app", {}).get("host"),
        port=cfg.get("app", {}).get("port"),
        debug=cfg.get("app", {}).get("debug"),
        database_url=cfg.get("database", {}).get("url"),
    )

    settings.host = os.getenv("HOST", settings.host)
    settings.port = int(os.getenv("PORT", settings.port))
    settings.debug = os.getenv("DEBUG", str(settings.debug)).lower() == "true"
    settings.database_url = os.getenv("DATABASE_URL", settings.database_url)

    return settings

settings = load_settings()
```


