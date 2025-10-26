# Communication-Breakdown Backend

FastAPI backend for the mock encryption simulation.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

4. Access API documentation:
http://localhost:8000/docs

## API Endpoints

- `GET /nodes` - Get all node locations
- `POST /publish_message` - Publish encrypted message
- `GET /node/{node_id}/messages` - Get node message history
- `GET /node/{node_id}/inventory` - Get node inventory
- `DELETE /messages/clear` - Clear all messages