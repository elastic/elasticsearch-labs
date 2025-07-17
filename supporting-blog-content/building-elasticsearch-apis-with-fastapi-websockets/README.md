# Quickstart

Follow these steps to set up and run the FastAPI API:

1. **Create a virtual environment:**

```bash
python3 -m venv venv
```

2. **Activate the virtual environment:**

- On macOS/Linux:
  ```bash
  source venv/bin/activate
  ```
- On Windows:
  ```bash
  venv\Scripts\activate
  ```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Run the API with uvicorn:**

```bash
uvicorn main:app --reload
```

The API will be available at [http://localhost:8000](http://localhost:8000)   

## Credentials

When you run the API, you will be prompted to insert your Elasticsearch endpoint and API key using `getpass`. These credentials are required to connect to your Elasticsearch instance.

At the terminal, you will see prompts like this to insert your credentials:

```
Insert the Elasticsearch endpoint here: 
Insert the Elasticsearch API key here: 
``` 