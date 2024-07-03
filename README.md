# fastapi-template-with-auth
 Fastapi template with basic auth and Mysql connection
- **main** branch has a basic and simple initial structure with User AUTH
- **async-struc** has a more advanced async architecture with user AUTH 


A template for a FastAPI project. This template includes a basic FastAPI application with a simple example of a RESTful API.
Uses FastAPI, Uvicorn, and Pydantic with SqlAlchemy and Alembic for database management. Currently, the database is a MySql database.
All the db connection and session management is done using async behaviour with the help of SqlAlchemy.

## Installation

    bash    git clone <http-url>
    bash    pip install -r requirements.txt

## Usage

    bash    uvicorn main:app --reload

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D
6. Remember to update the README.md with the new feature.
7. If you find a bug or have a question, please open an issue.
8. If you have a feature request, please open an issue.
9. If you want to contribute, please submit a pull request.
