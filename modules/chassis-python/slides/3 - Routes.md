# Routes

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

## Routes
In FastAPI, **routes** are the core mechanism that connects HTTP requests to the code that should handle them. Each route corresponds to a specific path (URL) and an HTTP method (GET, POST, etc.).

A **route** is simply a function *decorated* with an HTTP method on your `app` object. For example:

```py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")   # <-- GET route 
def read_root():
    return {"message": "Welcome to FastAPI"}
```

**Supported HTTP Methods**

- `@app.get(path)`: Retrieve data (read operations)
- `@app.post(path)`: Create new data
- `@app.put(path)`: Replace existing data
- `@app.patch(path)`: Update part of existing data
- `@app.delete(path)`: Remove data
- `@app.options(path)`: Discover supported operations
- `@app.head(path)`: Retrieve metadata (like headers) without a body


## Path Parameters

* **Part of the URL** (`{}` in route)
* **Required** by default
* Used to **identify a specific resource**

```python
from fastapi import FastAPI, Path
from typing import Annotated

app = FastAPI()

@app.get("/products/{product_id}")
async def read_product(
    product_id: Annotated[int, Path(gt=0, description="ID must be > 0")]
):
    return {"product_id": product_id}
```

* URL: `/products/42` → `product_id = 42`
* Validation: `gt=0` → only positive integers allowed
* Appears in OpenAPI docs automatically

---

## Query Parameters

* **Sent after `?` in URL** (`/items/?q=apple`)
* Optional by default (unless you enforce it)
* Used for **filtering, sorting, or modifying results**

```python
from fastapi import Query
from typing import Annotated

@app.get("/products/")
async def list_products(
    q: Annotated[str | None, Query(max_length=50)] = None
):
    return {"query": q}
```

* URL: `/products/?q=mouse` → `q = "mouse"`
* URL: `/products/` → `q = None`
* Validation: `max_length=50`
* Optional parameters are easy to handle with default values

---

## Body Parameters

* **Sent in the request body** (usually JSON for POST/PUT)
* Automatically parsed into **Pydantic models**
* Required unless default values are provided

```python
from pydantic import BaseModel

class Product(BaseModel):
    name: str
    price: float
    tags: list[str]

@app.post("/products/")
async def create_product(product: Product):
    return {"message": "Product created", "product": product}
```

* URL: `/products/` (no query/path needed)
* Request body:

```json
{
  "name": "Keyboard",
  "price": 42.0,
  "tags": ["PC", "Hardware"]
}
```


## DTOs

There are some cases where you need or want to return some data that is not exactly what the type declares.

This is very useful when we use DTOs. In fact, we can "change" DTO from input to output automatically. For example, suppose to have input and output of users in which we want to remove (obviously) password:

```py
from typing import Any
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr

app = FastAPI()

class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: str | None = None


class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


@app.post("/user/", response_model=UserOut)
async def create_user(user: UserIn) -> Any:
    return user
```

## Status code

**Default status code**

The same way you can specify a response model, you can also declare the ***default* HTTP status code** used for the response with the parameter `status_code` in any of the path operations.

```py
from fastapi import FastAPI, status

app = FastAPI()


@app.post("/items/", status_code=status.HTTP_201_CREATED)
async def create_item(name: str):
    return {"name": name}
```

**Custom status code**

In order to provide a ***custom* HTTP status code**, based on route logic, we must use `Response` parameter, which will be automatically injected if present in method signature.

```py
from fastapi import FastAPI, Response, status

app = FastAPI()

tasks = {"foo": "Listen to the Bar Fighters"}


@app.put("/get-or-create-task/{task_id}", status_code=200)  # <-- default status code
def get_or_create_task(task_id: str, response: Response):
    if task_id not in tasks:
        tasks[task_id] = "This didn't exist before"
        response.status_code = status.HTTP_201_CREATED  # <-- custom status code
        
    return tasks[task_id]
```

## Errors

When building web applications, it is crucial to handle errors in a way that provides useful feedback to the client without exposing unnecessary internal details. 

The most common tool is the `HTTPException` class, which allows us to return HTTP error responses with custom status codes and messages.

```python
@app.get("/products/{product_id}", status_code=200)
async def read_product(product_id: int) -> Product:
    
    products = [
        Product(
            name="Keyboard",
            price=42.0,
            tags=["PC", "Hardware"]
        ),
        Product(
            name="Mouse",
            price=32.0,
            tags=["PC", "Hardware"],
            description="It is not the animal!"
        ),
    ]
    
    if product_id >= len(products):     # check and return 404 Not Found
        raise HTTPException(status_code=404, detail="Product not found")

    return products[product_id]
```

When a client requests `/products/3`, FastAPI automatically generates a response like this:

```
{
  "detail": "Product not found"
}
```

## References
