# SQLROOT

SQLROOT is a lightweight, interactive command-line interface (CLI) tool for executing SQL queries against your databases directly from your terminal. Built with Python and SQLAlchemy, it offers a colorful and intuitive experience for database management and querying.

## Features

- **Interactive SQL Shell**: Execute SQL queries seamlessly.
- **Dynamic Configuration**: Manages database connection strings using an `.env` file.
- **Runtime Switching**: Switch between different databases easily at runtime using the `/env` command.
- **User-Friendly**: Clear, colorful output with helpful status messages.
- **Utility Commands**: Includes `/clear` to tidy up your terminal and `/env` to update your connection string.

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd SQLRoot
   ```

2. **Install dependencies:**
   Make sure you have [Python 3](https://python.org) installed.
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Run the application:**
   ```bash
   python main.py
   ```

2. **Configure Database Connection:**
   On the first run, the tool will prompt you to enter your database connection string, which will be saved in a `.env` file.

3. **Shell Commands:**
   - Type any valid SQL query to execute it.
   - `/clear` - Clears the terminal screen.
   - `/env` - Prompt to update the current database connection string.
   - `exit` or `quit` - Exit the application.

## Built With

- [SQLAlchemy](https://www.sqlalchemy.org/) - SQL toolkit and ORM.
- [colorama](https://pypi.org/project/colorama/) - For colorful terminal output.
- [python-dotenv](https://pypi.org/project/python-dotenv/) - For managing environment variables.

## License

This project is licensed under the MIT License.
