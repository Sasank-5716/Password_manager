# Secure Password Manager 🔒

A command-line password manager that securely stores your passwords using encryption.

## Features
- 🔐 Master password protection
- 🔑 Secure password generation
- 🗃️ Encrypted password storage
- 🔍 Easy password retrieval
- 📝 Password history tracking


_______________________________________________________________________________________

python password_manager.py [command] [arguments]

## Commands:
  register <username>    Register a new user
  login <username>      Login to your account
  add <service>         Add a new password (--username, --password optional)
  get <service>         Retrieve a stored password
  update <service>      Update an existing password
  delete <service>      Delete a stored password
  list                  List all saved services
  history <service>     View password change history

## Terminology
Term	Meaning
Master username	Your login for the password manager itself (created during registration)
Service	The name of the website/app you are saving a password for (e.g., google)
Service username	Your login for the specific service (e.g., your Google username)
Security Notes
Passwords are encrypted using a key stored in secret.key (created automatically).

The SQLite database is local (passwords.db).

Do not share your secret.key or database file with others.

## Example Workflow
### Register:
python Password_manager.py register alice

### Add a Google password:
python Password_manager.py add google --username alice123

### Retrieve your Google password:
python Password_manager.py get google

### List all your services:
python Password_manager.py list

Feel free to contribute or open issues!