# AI Usage Notes

## 1. Which parts of the code were AI-generated vs. written by me

I used ChatGPT to help generate the initial FastAPI project structure, API endpoints, Pydantic models, test cases, README, and documentation. I reviewed the generated code, understood how each component worked, and integrated it into the final solution.

## 2. What I validated, tested, or changed, and why

I manually reviewed the generated code and verified that it met all assignment requirements. I ran the complete test suite using pytest, tested the API through the FastAPI Swagger UI, improved input validation, added additional edge-case tests, improved error handling for JSON file operations, and updated the documentation to make the setup and usage instructions clearer.

## 3. AI suggestions I decided not to use, and why

I chose not to add features such as a database, authentication, Docker support, or additional API endpoints because the assignment requested a lightweight solution using local JSON storage. I kept the implementation focused on the required functionality and one optional bonus feature.