# PAYROLL-PRCESSING-SYSTEM

- Open your terminal(in any window of your choice).

- Run the following commands to generate the secure random key:

- python -c "import os; import secrets; print(f'Secure Random Key: {secrets.token_hex(16)}')"

- This one-liner will print the generated key to the terminal.

- Copy the generated key.

- Open your .env file, and set the FLASK_SECRET_KEY to the copied key:
