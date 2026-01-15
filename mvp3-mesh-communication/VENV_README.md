# MVP2-Crypto Virtual Environment

## Setup Instructions

This project uses a Python virtual environment named `crypto-env`.

### Activation

**PowerShell:**
```powershell
.\crypto-env\Scripts\Activate.ps1
```

**Command Prompt:**
```cmd
.\crypto-env\Scripts\activate.bat
```

### Deactivation

```
deactivate
```

### Dependencies

All dependencies are listed in `backend/requirements.txt` and include:
- **fastapi** & **uvicorn**: Web framework and ASGI server
- **cryptography**: ECDSA, ECDH, AES-GCM crypto primitives
- **pybloom-live**: Bloom filters for gossip protocol
- **numpy**: Economic calculations (Gini coefficient, etc.)

### Installing Dependencies

```bash
pip install -r backend/requirements.txt
```

### Running the Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Running the Frontend

```bash
cd frontend
npm install
npm start
```
