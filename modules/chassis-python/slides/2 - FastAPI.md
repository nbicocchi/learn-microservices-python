# Introduction to FastAPI

**FastAPI** is a modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints. One of its key advantages is its speed: it is one of the fastest Python frameworks available, thanks to its use of *Starlette* (for web parts) and *Pydantic* (for data validation).

- **High performance** comparable to Node.js and Go.
- **Automatic interactive API documentation** with Swagger UI and ReDoc.
- **Validation and serialization** powered by Python type hints and Pydantic.
- **Easy to learn** and use, with concise, readable code.

## Hello world step-by-step

### 1. Import FastAPI

```py
from fastapi import FastAPI
```

The `FastAPI()` class is the core of every FastAPI application, it provides all the functionality for your API.

### 2. Create a FastAPI "instance"


```py
from fastapi import FastAPI

# Create the application instance
app = FastAPI()
```

This object has several responsibilities:

- **Routing**: It maps HTTP methods and paths (like `GET /` or `POST /`users) to the corresponding Python functions you define with decorators (`@app.get`, `@app.post`, etc.).
- **Dependency Injection**: It provides a way to declare and automatically resolve dependencies such as authentication, database connections, or reusable services.
- **Validation and Serialization**: It uses Pydantic to validate incoming request data and to format outgoing responses.
- **Documentation Generation**: It automatically generates interactive API documentation that you can access at `/docs` (Swagger UI) or `/redoc`.


### 3. Define a basic route

Following code achieves "Hello world" goal returning a JSON message if you will perform a GET request on `/` (root of web service).

```py
from fastapi import FastAPI  

# Create the application instance
app = FastAPI()  

# Define a basic route
@app.get("/")  
def read_root():  
    return {"message": "Hello, World!"}
```

### 4. Run application

To run the application, save the code in a file named `main.py` and use the command:

```
fastapi dev main.py
```

Go to `http://127.0.0.1:8000/` to see the hello world JSON response:

```js
{"message": "Hello, World!"}
```


### 5. Documentation

As already mentioned, FastAPI generates documentation automatically thanks to Swagger.
You can see it and interact go to `http://127.0.0.1:8000/docs`

![Swagger](images/overview/swagger.png)
