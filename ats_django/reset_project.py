import os
import glob
import subprocess
import sys
from pathlib import Path

def run_command(command):
    """
    Runs a shell command and checks for errors.
    This is for short-running setup commands.
    """
    print(f"\n--- Running command: {' '.join(command)} ---")
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
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

    # Ensure we are in the script's directory (ats_django)
    script_dir = Path(__file__).resolve().parent
    os.chdir(script_dir)
    print(f"Running in directory: {script_dir}")

    # 1. Delete all migration files, except __init__.py
    print("\n--- Step 1: Deleting migration files ---")
    deleted_files_count = 0
    for dirpath, dirnames, filenames in os.walk('.'):
        if 'migrations' in dirnames:
            migrations_dir = os.path.join(dirpath, 'migrations')
            migration_files = glob.glob(os.path.join(migrations_dir, '*.py*'))
            
            for f in migration_files:
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
    python_executable = sys.executable
    
    if not run_command([python_executable, 'manage.py', 'makemigrations']):
        print("\n--- Makemigrations failed. Aborting script. ---")
        sys.exit(1)
        
    if not run_command([python_executable, 'manage.py', 'migrate']):
        print("\n--- Migrate failed. Aborting script. ---")
        sys.exit(1)


    # 4. Create a superuser automatically with profile picture
    print("\n--- Step 4: Creating superuser 'ajuma' ---")
    
    # This script will be executed within the Django context using `manage.py shell`
    superuser_script = """
import os
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files import File
from parser.models import Profile

User = get_user_model()

username = 'ajuma'
email = 'jumalex99@gmail.com'
password = 'Aj37024013!'
pic_name = 'user1.jpg'
pic_folder = 'dummy_user_profile_pics'
relative_pic_path = os.path.join(pic_folder, pic_name)
full_pic_path = os.path.join(settings.BASE_DIR, relative_pic_path)

if not User.objects.filter(username=username).exists():
    print(f"Creating superuser '{username}'...")
    try:
        user = User.objects.create_superuser(username, email, password)
        print("Superuser created successfully.")
        
        # Now, find the auto-created profile and set the picture
        print("Attempting to set profile picture...")
        if os.path.exists(full_pic_path):
            try:
                with open(full_pic_path, 'rb') as f:
                    # The 'user1.jpg' part is the name saved to the media folder
                    user.profile.profile_picture.save('user1.jpg', File(f), save=True)
                print(f"Successfully set profile picture from: {relative_pic_path}")
            except Exception as e:
                print(f"!!! Error setting profile picture: {e}")
                print("Superuser was created, but without a profile picture.")
        else:
            print(f"!!! Warning: Profile picture path not found: {full_pic_path}")
            print("Superuser was created, but without a profile picture.")
            
    except Exception as e:
        print(f"!!! An error occurred during superuser creation: {e}")
else:
    print(f"Superuser '{username}' already exists. Skipping creation.")
"""
    
    if not run_command([python_executable, 'manage.py', 'shell', '--command', superuser_script]):
        print("\n--- Failed to execute superuser creation script. Please check logs. ---")
        sys.exit(1)
        

    # 5. Run the server on port 7777
    print("\n\n--- Step 5: Starting development server on port 7777 ---")
    print("All steps completed. The server is now running.")
    print("Press CTRL+C to stop the server.")
    
    server_command = [python_executable, 'manage.py', 'runserver', '7777']
    
    try:
        # We run this command differently, letting it take over the terminal
        subprocess.run(
            server_command,
            check=True,
            text=True,
            encoding='utf-8'
        )
    except KeyboardInterrupt:
        print("\n--- Server stopped. Reset script finished. ---")
    except subprocess.CalledProcessError as e:
        print(f"\n--- ERROR: Server process failed. ---")
        if e.stderr:
            print(e.stderr)
        if e.stdout:
            print(e.stdout)
    except FileNotFoundError:
        print(f"--- ERROR: Command '{server_command[0]}' not found. ---")

    print("\n--- Django project reset script has finished. ---")


if __name__ == "__main__":
    main()