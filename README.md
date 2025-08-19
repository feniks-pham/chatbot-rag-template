
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

First, you need to copy all the files that you want the chatbot use as data to data folder or if you use production deployment, you can put all the files to your s3.

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

# For web data
your_intent:
    name: your_intent_name
    data_source: 
        type: crawl
        web_url: your_web_url
```

Note: You need to set "default" value to one intent to make sure that the application will return the default intent in case it cannot define the intent of user query

- In folder templates, create system_prompt.txt file to put your system prompt for the whole chatbot and create two other files intent_prompt.txt, rewrite_prompt.txt to put prompts that define user query intents and rewrite their query to fit the context

## Running the App

This application supports two ways to deploy: via Docker or via Kubernetes (k8s). 
- Docker is recommended for local development and quick testing. 
- Kubernetes is intended for production or staging environments, providing scalability, load balancing, and fault tolerance.

### Running with Kubernetes

1. **Setup ConfigMap and Secret**

You need to setup and update env data in ConfigMap and Secret section in k8s/chatbot-deployment.yaml.You have to fill in all values that noted "Required" in that file

```env
# S3
S3_PATH: "your_s3_path"
S3_ENDPOINT_URL: "your_s3_endpoint_url"
AWS_ACCESS_KEY_ID: "your_aws_access_key_id" 
AWS_SECRET_ACCESS_KEY: "your_aws_secret_access_key"
```

Note: This is where you store your data, you can check your s3 to get those values

```env
# LLM model
LLM_API_URL: "your_llm_api_url"
LLM_API_KEY: "your_llm_api_key"
LLM_API_MODEL: "your_llm_api_model"
```

Note: You have to use LLM model that support OpenAI. If you do not have any LLM api key, you can go to [OpenAI Platform](https://platform.openai.com/docs/overview) to create your api key and choose your approriate model.

```env 
# Embedding model
EMBEDDING_API_URL: "your_embedding_api_url"
EMBEDDING_API_KEY: "your_embedding_api_key"
EMBEDDING_MODEL_NAME: "your_embedding_model_name"
EMBEDDING_MAX_TOKENS: "your_embedding_max_tokens
```

Note: You should choose enbedding model that fits your data and supports your data languages. If you do not have any embedding api key, you can go to [HuggingFace](https://huggingface.co) to create your api key and choose your approriate model.

```env
HF_TOKEN: "your_huggingface_token"
```

Note: You can create this token here [HuggingFace](https://huggingface.co)

```env
# Zalo TTS 
TTS_API_URL: "your_tts_api_url"
TTS_API_KEY: "your_tts_api_key"
```

Note: If you would like to use Zalo text to speech for chatbot, you can contact us to get api url and api key. If not, you just leave default values there and do not choose Zalo when run text to speech for chatbot or it will get errors

```env
# Gemini TTS
GEMINI_TTS_API_URL: "your_gemini_tts_api_url"
GEMINI_TTS_API_KEY: "your_gemini_tts_api_key"
```

Note: If you would like to use Gemini text to speech for chatbot, you can fill in your Google api key there, or you can go to [Google API Key](https://cloud.google.com/docs/authentication/api-keys) to create your api key. If not, you just leave default values there and do not choose GEMINI when run text to speech for chatbot or it will get errors

We support two types of vector databases, which are PostgreSQL and OpenSearch, but only one is used at runtime, and selected by the DATABASE value in your .env file. This is key settings for each database

- PostgreSQL:

```env
DATABASE: "postgres"
DATABASE_URL: "postgresql://postgres_user:postgres_password@postgres_host/postgres_db"
```

Note: If the database in the URL has not been created beforehand, the application will automatically create the corresponding database for you when running, but we recommend that you create the database manually before running to avoid unexpected errors.

- OpenSearch:

```env
DATABASE: "opensearch"
OPENSEARCH_URL: "https://opensearch_user:opensearch_password@opensearch_host:opensearch_port"
```

Note: You only need to pass the url for the database that you use, do not have to fill both

2. **Kubernetes deployment**

First, you have to create the configmap for your templates folder to mount it into your application deployed on k8s

```bash
# Create configmap for templates
kubectl create configmap templates-config --from-file=templates/

# Clean up when finish
kubectl delete configmap templates-config
```

Note: You need to run this command in the same location where you keep your templates folder

Then, you can deploy your application

```bash
# Deploy the application
kubectl apply -f k8s/chatbot-deployment.yaml

# View Logs
kubectl get pods
kubectl logs -f <Pod Name>

# Clean up when finish
kubectl delete -f k8s/chatbot-deployment.yaml
```

### Running with Docker

Make sure you have your Docker and Docker compose installed

1. **Setup your environment file**

Copy env.dev.example to .env and fill in all required values according to the instructions

```bash
cp env.dev.example .env
```

You can check the instructions for the following env data in Running with Kubernetes section before

```env
# LLM model
LLM_API_URL=your_llm_api_url 
LLM_API_KEY=your_llm_api_key

# Embedding model
EMBEDDING_API_URL=your_embedding_api_url
EMBEDDING_API_KEY=your_embedding_api_key
EMBEDDING_MODEL_NAME=your_embedding_model_name
EMBEDDING_MAX_TOKENS=your_embedding_model_max_tokens 

HF_TOKEN=your_huggingface_token 

# Zalo TTS
TTS_API_URL=your_tts_api_url 
TTS_API_KEY=your_tts_api_key 

# Gemini TTS
GEMINI_TTS_API_URL=your_gemini_tts_api_url
GEMINI_TTS_API_KEY=your_gemini_api_key
```

For development/testing, you should use Docker to host your database.

- PostgreSQL:

```env
DATABASE=postgres
DATABASE_URL=postgresql://postgres_user:postgres_password@postgres_host/postgres_db
```

Note: You can check docker-compose.postgres.yml to get host, port, user, password and db for your Postgres database or you can set your own Postgres database information in that file

- OpenSearch:

```env
DATABASE=opensearch
OPENSEARCH_INITIAL_ADMIN_PASSWORD=your_opensearch_password
OPENSEARCH_URL=https://opensearch_user:opensearch_password@opensearch_host:opensearch_port
```

Note: If you use our default OpenSearch docker compose, remember to fill in OPENSEARCH_INITIAL_ADMIN_PASSWORD variable in .env file or it will get error. You can check docker-compose.opensearch.yml to get host, port, user and password for your OpenSearch database or you can set your own OpenSearch database information in that file. 

2. **Create virtual environment**

```bash
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Start Database**

- Postgres

```bash
# Start Database
docker compose -f docker-compose.postgres.yml up

# View Logs
docker compose -f docker-compose.postgres.yml logs

# Stop Database
docker compose -f docker-compose.postgres.yml down
```

- OpenSearch
   
```bash
# Start Database
docker compose -f docker-compose.opensearch.yml up

# View Logs
docker compose -f docker-compose.opensearch.yml logs

# Stop Database
docker compose -f docker-compose.opensearch.yml down
```

4. **Start the application**

```bash
# Start application
docker compose -f docker-compose.dev.yml up

# View logs
docker ps
docker logs -f <Container ID>

# Cleaned up when finished
docker compose -f docker-compose.dev.yml down
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







 







