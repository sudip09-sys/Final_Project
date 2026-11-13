# Tutorial 1 Install and start the application

1. Install Python 3.12, CMake and a C++ compiler. Use WSL2 or Docker if native dlib installation is difficult on Windows.
2. Extract the project ZIP and open a terminal in the smart-attendance folder.
3. Run `python -m venv .venv`.
4. Activate with `source .venv/bin/activate` on Linux/macOS/WSL2, or `.venv\Scripts\Activate.ps1` in Windows PowerShell.
5. Run `pip install -r requirements.txt`. Compiling dlib can take several minutes.
6. Run `python scripts/setup.py`. Create and confirm a password with at least 12 characters.
7. Run `python scripts/run.py`.
8. Open http://127.0.0.1:5000 and enter your password.
9. Follow the recorded enrollment and check-in tutorial.

For MySQL, add MYSQL_PASSWORD and MYSQL_ROOT_PASSWORD to the generated .env as described in README.md, then run `docker compose up --build` and open http://127.0.0.1:8000. This path keeps MySQL private and uses a persistent Docker volume.
