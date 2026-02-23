# Introduction to Pydantic

https://docs.pydantic.dev/latest/

## What is Pydantic?

Pydantic is a Python library that helps you define **data models** with automatic validation and parsing.  
It uses **Python type hints** to check that the data you receive matches the expected format, and it can convert types when possible.

In short:

1. You define a class with attributes and their types.
2. Pydantic validates and parses incoming data.
3. You get clean, safe, and predictable Python objects.

> [!TIP]
> If you are a Java developer, Pydantic is similar to *Lombok* library.

## Why use Pydantic?

In real-world applications, especially when dealing with **APIs**, **databases**, or **user input**, the data you receive may not always be:

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



