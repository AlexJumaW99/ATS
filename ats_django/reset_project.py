import os
import glob
import subprocess
import sys

def run_command(command):
    """Runs a shell command and checks for errors."""
    print(f"\n--- Running command: {' '.join(command)} ---\n")
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print("--- Stderr ---\n", result.stderr)
        print(f"\n--- Command '{' '.join(command)}' executed successfully. ---")
        return True
    except subprocess.CalledProcessError as e:
        print(f"--- ERROR: Command failed with exit code {e.returncode} ---")
        print("--- Stdout ---")
        print(e.stdout)
        print("--- Stderr ---")
        print(e.stderr)
        return False
    except FileNotFoundError:
        print(f"--- ERROR: Command '{command[0]}' not found. Is Python in your PATH? ---")
        return False


def main():
    """Main function to orchestrate the Django project reset."""
    print("--- Starting Django project reset script ---")

    # 1. Delete all migration files, except __init__.py
    print("\n--- Step 1: Deleting migration files ---")
    deleted_files_count = 0
    # Walk through the current directory and its subdirectories
    for dirpath, dirnames, filenames in os.walk('.'):
        # We are looking for directories named 'migrations'
        if 'migrations' in dirnames:
            migrations_dir = os.path.join(dirpath, 'migrations')
            # Find all .py and .pyc files within this directory
            migration_files = glob.glob(os.path.join(migrations_dir, '*.py*'))
            
            for f in migration_files:
                # Keep the __init__.py file
                if os.path.basename(f) != '__init__.py':
                    print(f"  Deleting {f}")
                    os.remove(f)
                    deleted_files_count += 1
    
    if deleted_files_count == 0:
        print("No migration files found to delete.")
    else:
        print(f"Deleted {deleted_files_count} migration files.")


    # 2. Delete the database file
    print("\n--- Step 2: Deleting database file (db.sqlite3) ---")
    db_file = 'db.sqlite3'
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
            print(f"  Successfully deleted {db_file}.")
        except OSError as e:
            print(f"  Error deleting {db_file}: {e}")
            sys.exit(1) # Exit if we can't delete the db
    else:
        print(f"  {db_file} not found, skipping.")


    # 3. Run makemigrations and migrate
    print("\n--- Step 3: Running makemigrations and migrate ---")
    python_executable = sys.executable # Use the same python that runs the script
    
    if not run_command([python_executable, 'manage.py', 'makemigrations']):
        print("\n--- Makemigrations failed. Aborting script. ---")
        sys.exit(1)
        
    if not run_command([python_executable, 'manage.py', 'migrate']):
        print("\n--- Migrate failed. Aborting script. ---")
        sys.exit(1)


    # 4. Create a superuser automatically
    print("\n--- Step 4: Creating superuser ---")
    
    # This script will be executed within the Django context using `manage.py shell`
    # It safely checks if the user already exists before attempting to create it.
    superuser_script = """
from django.contrib.auth import get_user_model

User = get_user_model()

username = 'alexjuma'
email = 'jumalex99@gmail.com'
password = 'Aj37024013!'

if not User.objects.filter(username=username).exists():
    print(f"Creating superuser '{username}'...")
    User.objects.create_superuser(username, email, password)
    print("Superuser created successfully.")
else:
    print(f"Superuser '{username}' already exists. Skipping creation.")
"""
    
    if not run_command([python_executable, 'manage.py', 'shell', '--command', superuser_script]):
        print("\n--- Failed to create superuser. Please check the logs. ---")
        sys.exit(1)
        
    print("\n\n--- Django project reset completed successfully! ---")


if __name__ == "__main__":
    main()


