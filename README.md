# OpenFunnel Magic Service

API service for OpenFunnel, built with FastAPI.

## Setup

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Data Files:** Ensure you have the necessary data files (`people.json`, `accounts-with-magic-column.json`) in the `data/` directory. These files are read by the API endpoints.

## Running the Application

Run the FastAPI application using Uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 4000 --reload
```

The `--reload` flag enables auto-reloading when code changes are detected, which is useful for development.

The API will be available at `http://localhost:4000`.

## API Endpoints

The service exposes the following endpoints:

- **`GET /`**:

  - Description: Health check endpoint.
  - Response: `{"Ping": "Pong"}`

- **`GET /api/accounts/all`**:

  - Description: Retrieves all accounts from the `data/accounts-with-magic-column.json` file.
  - Response: A list of `Account` objects.

- **`GET /api/accounts/{company_name}`**:

  - Description: Retrieves accounts filtered by the provided `company_name`.
  - Path Parameter: `company_name` (string) - The name of the company to filter by.
  - Response: A list of matching `Account` objects or a 404 error if not found.

- **`GET /api/prospects/{company_name}`**:

  - Description: Retrieves prospects (people) filtered by the provided `company_name` from the `data/people.json` file.
  - Path Parameter: `company_name` (string) - The name of the company to filter prospects by.
  - Response: A list of matching `Person` objects or a 404 error if no prospects are found for that company.

- **`POST /api/magic/generate`**:
  - Description: Adds a new "magic question" to the `magicColumns` list for every account in `data/accounts-with-magic-column.json`. Initializes `magicColumns` if it doesn't exist. The generated answer is initially set to "Unsure".
  - Request Body: A JSON object containing the question, e.g., `{"question": "What is their biggest pain point?"}`.
  - Response: `{"success": true, "message": "Magic question added successfully"}` on success, or an error response.
