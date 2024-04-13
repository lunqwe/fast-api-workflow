# Test task

This project is a test task for Starnavi.
[FastAPI](https://fastapi.tiangolo.com/) application.

## Installation

Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Running

1. Start the application:

   ```bash
   uvicorn main:app --reload
   ```

   Where `main` is the name of your application file and `app` is the instance of your FastAPI application.

2. After starting, the application will be available at `http://127.0.0.1:8000`.

## Testing

1. To run `workflow` services tests:

   ```bash
   pytest tests/workflow.py
   ```

2. To run `node` services tests:
  ```bash
   pytest tests/node.py
   ```

## Documentation

1. API documentation is available at `http://127.0.0.1:8000/docs`.

   Here you'll find interactive documentation and the ability to test endpoints directly from your browser.

2. Alternatively, you can use `http://127.0.0.1:8000/redoc` to view the documentation in ReDoc format.
