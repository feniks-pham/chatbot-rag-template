
# ChatBot RAG App

This is an app that powered by LangChain, OpenAI LLM and Streamlit to create a chatbot experience with your own data and data from websites. It also supports Text-to-Speech (TTS) and Speech-to-Text (STT), allowing users to interact via text or voice.

## General prerequisites
- Python 3.13 installed
- Git installed

## Download the Project

Download the project from Github

```bash
git clone https://github.com/feniks-pham/trung-nguyen-chatbot
```

## Prepare your data and templates

This chatbot uses files and web as data source

First, you need to copy all the files that you want the chatbot use as data to data folder or if you use production deployment, you can put all the files to your s3 service

```bash
# Create data directory
mkdir -p data

# Copy files to data folder
cp your_file data/your_file
```

Then, you need to setup your templates folder to load all your data and prompt for each type of data

- Create templates directory

```bash
mkdir -p templates
```

- Create intents.yaml file in templates folder

```bash
touch templates/intents.yaml
```

- Separate your data used for chatbot into intents then put all data of each intent to intents.yaml file

```intents.yaml
# For local files data
your_intent:
    name: your_intent_name
    data_source:
        type: vector_db
        file: your_file
    prompt_file: your_intent_prompt_file.txt

# For web data
your_intent:
    name: your_intent_name
    data_source: 
        type: crawl
        web_url: your_web_url
    prompt_file: your_intent_prompt_file.txt

# For fixed answer data
your_intent:
    name: your_intent_name
    data_source: 
        type: fixed
        context: ""
    prompt_file: your_intent_prompt_file.txt
```

Note: You need to set "default" value to one intent to make sure that the application will return the default intent in case it cannot define the intent of user query

- Create your intent prompt file and two files intent_prompt.txt and rewrite_prompt.txt

## Running the App

This application supports two ways to deploy: via Docker or via Kubernetes (k8s). 
- Docker is recommended for local development and quick testing. 
- Kubernetes is intended for production or staging environments, providing scalability, load balancing, and fault tolerance.

### Running with Docker

Make sure you have your Docker and Docker compose installed

1. **Setup your environment file**

Copy env.dev.example to .env and fill in all required values according to the instructions

```bash
cp env.dev.example .env
```

Note: Those following .env values cannot be left blank 

```env
LLM_API_URL=your_llm_api_url 
LLM_API_KEY=your_llm_api_key

TTS_API_URL=your_tts_api_url 
TTS_API_KEY=your_tts_api_key 

GEMINI_TTS_API_URL=your_gemini_tts_api_url
GEMINI_TTS_API_KEY=your_gemini_api_key

EMBEDDING_API_URL=your_embedding_api_url
EMBEDDING_API_KEY=your_embedding_api_key
EMBEDDING_MODEL_NAME=your_embedding_model_name
EMBEDDING_MAX_TOKENS=your_embedding_model_max_tokens 

HF_TOKEN=your_huggingface_token 
```

We support two types of vector databases, which are PostgreSQL and OpenSearch, but only one is used at runtime, and selected by the DATABASE value in your .env file. This is key settings for each database

- PostgreSQL:

```env
DATABASE=postgres
DATABASE_URL=postgresql://postgres_user:postgres_password@postgres_host/postgres_db
```

Note: If the database in the URL has not been created beforehand, the application will automatically create the corresponding database for you when running, but we recommend that you create the database manually before running to avoid unexpected errors.

- OpenSearch:

```env
DATABASE=opensearch
OPENSEARCH_URL=https://opensearch_user:opensearch_password@opensearch_host:opensearch_port
```

Note: You only need to pass the url for the database that you use, do not have to fill both

2. **Create virtual environment**

```bash
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Start Database**

For development/testing, you should use Docker to host your database

```bash
# For Postgres Database
docker compose -f docker-compose.dev.yml up -d postgres
   
# For OpenSearch Database
docker-compose -f docker-compose.dev.yml up -d opensearch-node1
docker-compose -f docker-compose.dev.yml up -d opensearch-node2
docker-compose -f docker-compose.dev.yml up -d opensearch-dashboards

# Stop Database
docker compose -f docker-compose.dev.yml down

# View Database Logs
# For Postgres Database
docker compose -f docker-compose.dev.yml logs -f postgres

# For OpenSearch Database
docker compose -f docker-compose.dev.yml logs -f opensearch-note1
```

4. **Index knowledge base**

Embedding your data and store into your vector database

```bash
python scripts/import_qa_data.py
```

5. **Start the application**

```bash
# Backend
docker compose -f docker-compose.dev.yml up -d Backend

# Frontend
docker compose -f docker-compose.dev.yml up -d frontend

# Cleaned up when finished
docker compose -f docker-compose.dev.yml down
```

### Running with Kubernetes

1. **Setup environment file**

Copy env.prod.example to .env and fill in all required values according to the instructions

```bash
cp env.prod.example .env
```

Note: Look at the 'Running with Docker' section to see which .env values are mandatory and must be filled in.

Then you need to setup the .env settings for your s3 service

```env
S3_PATH=your_s3_bucket_name
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
S3_ENDPOINT_URL=your_s3_endpoint_url
```

Finally, you can setup the .env settings for your databases as same as running with docker

2. **Kubernetes deployment**

First, you need to pass all corresponding data from .env to configmap and secret section in file k8s/chatbot-deployment.yaml.

Then, you can deploy the application

```bash
# Deploy the application
kubectl apply -f k8s/chatbot-deployment.yaml

# Clean up when finished
kubectl delete -f k8s/chatbot-deployment.yaml
```

## Troubleshooting

1. **Database connection failed**
   - Check if PostgreSQL is running
   - Verify DATABASE_URL format
   - Ensure database exists and has pgvector extension

2. **S3 connection failed (Production)**
   - Verify S3 credentials and endpoint
   - Check if bucket exists and is accessible
   - Ensure your s3 contains all files in your templates

3. **Local file not found (Development)**
   - Ensure all files in your templates exists
   - Check files permissions

4. **Import script fails**
   - Check if all API keys are configured
   - Verify database schema is initialized
   - Check logs for specific error messages







 







