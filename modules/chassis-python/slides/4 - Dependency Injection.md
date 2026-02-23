# Dependency Injection

## Depends

When building APIs, it’s common to need reusable logic across multiple endpoints: authentication, database sessions, pagination parameters, etc. FastAPI provides a powerful system called ***dependency injection***, and the key tool is `Depends`.

When we specify `Depends`, we tell FastAPI that a parameter’s value should **come from another function**, not directly from the request.

For example:

```py
from typing import Annotated
from fastapi import FastAPI, Depends

app = FastAPI()

def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

@app.get("/items/")
def read_items(commons: Annotated[dict, Depends(common_parameters)]):
    return commons
```

The endpoint `read_items` receives `commons` as the dictionary returned by `common_parameters` function.

A common use case for `Depends` is **Database Session Management**

```py
# Database Session Management

def get_db():
    db = create_session()
    try:
        yield db
    finally:
        db.close()

@app.get("/products/")
def get_products(db: Annotated[Session, Depends(get_db)]):
    return db.query(Product).all()
```


## References

https://fastapi.tiangolo.com/tutorial/query-params-str-validations/

https://fastapi.tiangolo.com/tutorial/path-params-numeric-validations/

https://fastapi.tiangolo.com/reference/dependencies/?h=depen#fastapi.Depends
