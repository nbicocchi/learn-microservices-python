# Persistence in FastAPI with SQLModel

## Product Model Example

```py
from sqlmodel import SQLModel, Field

class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    uuid: str
    name: str
    weight: float
```

**Explanation:**

* `SQLModel` inherits from **Pydantic**, so it automatically validates fields in API requests.
* `table=True` tells SQLModel to create a database table for this class.
* `id` is the primary key, auto-incremented.
* Other fields like `uuid`, `name`, `weight` define your domain data.

> [!TIP] This model can be used **both for API requests and database persistence**, reducing duplication.

---

## Database Setup

```py
from sqlmodel import SQLModel, create_engine, Session
from core.config import settings

engine = create_engine(settings.database_url, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
```

**Explanation:**

* `engine` connects to your database (Postgres, SQLite, etc.)
* `init_db()` creates all tables defined by SQLModel classes
* `get_session()` is a **FastAPI dependency** that gives each request a database session
* Using `yield` ensures the session **closes automatically** after the request

> [!TIP] Dependency injection with `get_session()` keeps your database code **clean and safe**.

---

## Repository Pattern

```py
from sqlmodel import Session, select
from typing import List, Optional
from models.product_model import Product
from schemas.product import ProductCreate, ProductUpdate

class ProductRepository:
    def __init__(self, session: Session):
        self.session = session
```

**Explanation:**

* Encapsulates all database operations for `Product`.
* Keeps **API routes thin**, only responsible for HTTP and validation.
* Makes testing easier: you can **mock the repository** without touching the database.

---

### Create Product

```py
def create(self, data: ProductCreate) -> Product:
    product = Product(uuid=data.uuid, name=data.name, weight=data.weight)
    self.session.add(product)
    self.session.commit()
    self.session.refresh(product)
    return product
```

**Explanation:**

* `add()` + `commit()` inserts the product into the database.
* `refresh()` updates the object with **auto-generated fields** (like `id`).
* Returns the **complete product object**, ready for API response.

---

### Read Products

```py
def get_all(self) -> List[Product]:
    return self.session.exec(select(Product)).all()

def get_by_id(self, product_id: int) -> Optional[Product]:
    return self.session.get(Product, product_id)
```

**Explanation:**

* `get_all()` fetches all products from the database.
* `get_by_id()` retrieves a single product by its primary key.
* Using SQLModel’s `select` and `get` methods makes queries **type-safe and easy to read**.

---

### Update Product

```py
def update(self, product_id: int, data: ProductUpdate) -> Optional[Product]:
    product = self.get_by_id(product_id)
    if not product:
        return None
    if data.uuid is not None:
        product.uuid = data.uuid
    if data.name is not None:
        product.name = data.name
    if data.weight is not None:
        product.weight = data.weight
    self.session.add(product)
    self.session.commit()
    self.session.refresh(product)
    return product
```

**Explanation:**

* Retrieves the product first; returns `None` if not found.
* Updates only fields that are **not `None`**, supporting **partial updates**.
* Commits and refreshes the object for the latest state.

---

### Delete Product

```py
def delete(self, product_id: int) -> bool:
    product = self.get_by_id(product_id)
    if not product:
        return False
    self.session.delete(product)
    self.session.commit()
    return True
```

**Explanation:**

* Checks if the product exists.
* Deletes it and commits the transaction.
* Returns `True` if deletion succeeded, otherwise `False`.

> [!TIP] Always handle `None` or missing objects gracefully in your repository.

---

## Best Practices

* Use **dependency injection** (`get_session`) to manage database sessions.
* Keep **API routes thin**; move logic to **services** or **repositories**.
* Call **`init_db()`** on startup to ensure tables exist.
* Use **SQLModel models** for both **validation** and **persistence**.
* Consider **async SQLModel** for high-throughput or concurrent APIs.

