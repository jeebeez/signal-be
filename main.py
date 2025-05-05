from fastapi import FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel

import json
import urllib.parse
from pathlib import Path

# Define source data directory (where the files are originally)
DATA_DIR = Path(__file__).parent / "data"

PEOPLE_JSON = DATA_DIR / "people.json"
MAGIC_JSON = DATA_DIR / "accounts-with-magic-column.json"


app = FastAPI(
    title="OpenFunnel Magic Service",
    description="API service for OpenFunnel",
)

origins = [
    "http://localhost:3000",
    "https://openfunnel.jeebee.dev",
    "https://jeebee-funnel.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


class Person(BaseModel):
    name: str
    role: str
    company: str
    location: str
    linkedinUrl: str
    email: str


class GeneratedAnswer(BaseModel):
    answer: str
    reasoning: str


class MagicColumn(BaseModel):
    question: str
    generated: GeneratedAnswer


class Account(BaseModel):
    name: str
    domain: str
    linkedinUrl: str
    signalDescription: Optional[str] = None
    signalLink: Optional[str] = None
    employees: Optional[int] = None
    fundingStage: Optional[str] = None
    magicColumns: Optional[List[MagicColumn]] = None


class MagicQuestion(BaseModel):
    question: str


class MagicResponse(BaseModel):
    success: bool
    message: Optional[str] = None


def load_json_file(file_path):
    """Load data from a JSON file"""
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"File not found: {file_path}"
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Invalid JSON in file: {file_path}",
        )


@app.get("/", status_code=status.HTTP_200_OK)
async def read_root():
    return {"Ping": "Pong"}


@app.get(
    "/api/accounts/all", response_model=List[Account], status_code=status.HTTP_200_OK
)
async def get_accounts():
    return load_json_file(MAGIC_JSON)


@app.get(
    "/api/accounts/{company_name}",
    response_model=List[Account],
    status_code=status.HTTP_200_OK,
)
async def get_account(company_name: str):
    # URL decode the company name
    decoded_name = urllib.parse.unquote(company_name)

    accounts_data = load_json_file(MAGIC_JSON)
    filtered = [
        account for account in accounts_data if account.get("name") == decoded_name
    ]
    if not filtered:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with name '{decoded_name}' not found",
        )
    return filtered


@app.get(
    "/api/prospects/{company_name}",
    response_model=List[Person],
    status_code=status.HTTP_200_OK,
)
async def get_prospects(company_name: str):
    # URL decode the company name
    decoded_name = urllib.parse.unquote(company_name)

    people_data = load_json_file(PEOPLE_JSON)
    filtered = [
        person for person in people_data if person.get("company") == decoded_name
    ]

    return filtered


@app.post(
    "/api/magic/generate",
    response_model=MagicResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_magic(question_data: MagicQuestion, response: Response):
    # Load the JSON data
    try:
        accounts_data = load_json_file(MAGIC_JSON)

        # If accounts_data is empty, return appropriate response
        if not accounts_data:
            response.status_code = status.HTTP_200_OK
            return MagicResponse(success=False, message="No accounts data available")

        # Add the new question to each account's magic columns
        for account in accounts_data:
            # Check if magic columns exists, if not create it
            if "magicColumns" not in account:
                account["magicColumns"] = []

            account["magicColumns"].append(
                {
                    "question": question_data.question,
                    "generated": {
                        "answer": "Unsure",
                        "reasoning": "No reasoning provided.",
                    },
                }
            )

        # Save the updated JSON data
        with open(MAGIC_JSON, "w") as file:
            json.dump(accounts_data, file, indent=4)

        return MagicResponse(success=True, message="Magic question added successfully")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=4000, reload=True)
