import os
import time
from colorama import Back, Fore, Style, init
from dotenv import load_dotenv, set_key
import sqlalchemy
from sqlalchemy import text

init(autoreset=True)

github_url = "https://github.com/fatehahmad0509"
github_link_name = "-Follow On Github"

insta_url = "https://instagram.com/fatih10273"
insta_link_name = "-Follow On Instagram"


def colored_start():
    os.system("cls" if os.name == "nt" else "clear")

    banner = f"""
{Fore.CYAN}{Style.BRIGHT}    ╔════════════════════════════════════════════════╗
    ║       {Fore.GREEN}SQLROOT{Fore.CYAN}      ║  MADE BY @fatehahmad0509 ║
    ╚════════════════════════════════════════════════╝{Style.RESET_ALL}
    """
    print(banner)

    print(f"{Fore.LIGHTBLUE_EX} ---WELCOME TO SQLROOT--- ")
    print(" ")
    print(f"{Fore.YELLOW}MADE BY Fateh Ahmad")
    print(f"{Fore.GREEN}\033]8;;{github_url}\033\\{github_link_name}\033]8;;\033\\")
    print(f"{Fore.GREEN}\033]8;;{insta_url}\033\\{insta_link_name}\033]8;;\033\\")

    print(
        f"{Fore.YELLOW}[{Fore.GREEN}✓{Fore.YELLOW}] {Fore.WHITE}Main Goal:"
        f" {Fore.BLUE}Executing SQL Commands Remotely{Style.RESET_ALL}\n"
    )
    print(
        f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}\n"
    )


if __name__ == "__main__":
    colored_start()

time.sleep(1.5)

load_dotenv()

db_str = os.getenv("DB_STR")

# Ask if DB_STR is missing on first run
if not db_str:
    print(f"{Fore.YELLOW}[!] The database string (DB_STR) was not found in the .env file.")
    choice = input(f"{Fore.CYAN}Would you like to add 'DB_STR' to the .env file right now? (y/n): {Fore.WHITE}").strip().lower()
    
    if choice == 'y':
        while True:
            db_str = input(f"{Fore.GREEN}Enter Database Connection String: {Fore.WHITE}").strip()
            if db_str:
                set_key(".env", "DB_STR", db_str)
                print(f"{Fore.GREEN}[✓] DB_STR successfully saved to .env file!\n")
                break
            print(f"{Fore.RED}[!] Connection string cannot be empty.")
    else:
        input(f"\n{Fore.RED}ERROR! DB_STR is required to run SQLROOT. PRESS ENTER TO EXIT")
        exit()

# Connection and loop function
def start_sql_shell(current_db_str):
    print(f"{Fore.YELLOW}[{Fore.GREEN}*SF{Fore.YELLOW}] {Fore.WHITE}Connecting to database...")

    try:
        engine = sqlalchemy.create_engine(current_db_str)
        connection = engine.connect()
        print(f"{Fore.YELLOW}[{Fore.GREEN}✓{Fore.YELLOW}] {Fore.GREEN}Connected successfully!\n")
    except Exception as e:
        print(f"{Fore.RED}[X] Connection failed: {e}\n")
        return "retry", current_db_str

    print(f"{Fore.LIGHTBLACK_EX}----------------------------------------{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Type your SQL commands below.")
    print(f"{Fore.CYAN}Commands: {Fore.YELLOW}'exit' / 'quit' {Fore.CYAN}| {Fore.YELLOW}'/env' {Fore.CYAN}| {Fore.YELLOW}'/clear'\n")

    while True:
        try:
            query = input(f"{Fore.GREEN}SQLROOT> {Fore.WHITE}")
            
            if not query.strip():
                continue
                
            query_lower = query.strip().lower()
            
            if query_lower in ["exit", "quit"]:
                print(f"{Fore.YELLOW}[*] Exiting SQLROOT. Goodbye!")
                connection.close()
                exit()
                
            # Clear the terminal with /clear command
            if query_lower == "/clear":
                os.system("cls" if os.name == "nt" else "clear")
                print(f"{Fore.GREEN}[✓] Terminal cleared.\n")
                continue
                
            # Change connection string at runtime with /env command
            if query_lower == "/env":
                new_db_str = input(f"{Fore.GREEN}Enter new Database Connection String (or type 'cancel' to abort): {Fore.WHITE}").strip()
                
                if not new_db_str or new_db_str.lower() == 'cancel':
                    print(f"{Fore.YELLOW}[i] Environment change cancelled.\n")
                    continue
                    
                print(f"{Fore.YELLOW}[*] Testing new connection...")
                try:
                    test_engine = sqlalchemy.create_engine(new_db_str)
                    test_conn = test_engine.connect()
                    test_conn.close()
                    
                    set_key(".env", "DB_STR", new_db_str)
                    print(f"{Fore.GREEN}[✓] .env updated successfully! Switching to new database...\n")
                    connection.close()
                    return "reconnect", new_db_str
                except Exception as test_err:
                    print(f"{Fore.RED}[!] Invalid connection string! Keeping current connection.")
                    print(f"{Fore.RED}[!] Error details: {test_err}\n")
                    continue

            # Execute command
            result = connection.execute(text(query))
            
            # Print results for queries containing SELECT or RETURNING
            if query_lower.startswith("select") or "RETURNING" in query.upper():
                rows = result.fetchall()
                if rows:
                    print(f"\n{Fore.GREEN}[+] Result ({len(rows)} rows):")
                    for row in rows:
                        print(f"{Fore.WHITE}{row}")
                else:
                    print(f"\n{Fore.YELLOW}[i] Query executed successfully, but returned 0 rows.")
            else:
                connection.commit()
                print(f"\n{Fore.GREEN}[+] Query executed successfully.")
                
            print()

        except Exception as e:
            try:
                connection.rollback()
            except:
                pass
            print(f"\n{Fore.RED}[!] Error executing query: {e}\n")

# Main program flow
current_str = db_str
while True:
    status, result_str = start_sql_shell(current_str)
    
    if status == "reconnect":
        current_str = result_str
    elif status == "retry":
        print(f"{Fore.YELLOW}1. Try entering a new connection string")
        print(f"{Fore.YELLOW}2. Exit SQLROOT")
        choice = input(f"{Fore.CYAN}Choose an option (1/2): {Fore.WHITE}").strip()
        
        if choice == '1':
            current_str = input(f"{Fore.GREEN}Enter Database Connection String: {Fore.WHITE}").strip()
            if current_str:
                set_key(".env", "DB_STR", current_str)
        else:
            print(f"{Fore.YELLOW}[*] Exiting SQLROOT. Goodbye!")
            break