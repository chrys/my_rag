# My RAG

My RAG is an enterprise-grade platform for managing retrieval-augmented generation (RAG) workflows. It empowers businesses to create intelligent, context-aware AI assistants that can accurately answer questions based on their own proprietary documents and data.

## Value Proposition
The platform provides a unified interface to securely manage multiple AI projects across different storage and processing environments. Whether prioritizing maximum data privacy with local processing or leveraging the scale of cloud providers like Google, My RAG offers a flexible solution tailored to diverse business needs.

## Key Features
- **Centralized Dashboard**: A user-friendly web interface to manage AI projects, documents, and interactions.
- **Multi-Backend Support**: Seamlessly switch between different document storage and AI processing backends:
  - **Google Cloud**: For powerful, scalable document search and generation.
  - **Local Storage**: For handling highly sensitive data with maximum privacy.
  - **PostgreSQL**: For robust, relational data integration.
- **Document Management**: Easily upload, organize, and index company documents to build specialized knowledge bases.
- **Customizable AI Behavior**: Tailor the AI's responses for different business units or use cases by configuring specific system prompts.
- **Performance Evaluation**: Built-in tools to test and evaluate the accuracy of the AI's responses, ensuring high-quality answers for end-users.

## Business Benefits
- **Enhanced Productivity**: Employees can quickly find accurate information hidden within vast amounts of company documents.
- **Data Security and Control**: Flexible deployment options ensure that sensitive business data is handled according to internal security policies.
- **Scalability**: Designed to grow with the organization, from small internal teams to enterprise-wide deployments.

## Installation & Quick Start

### Prerequisites
- Python 3.10+
- `pip` and `virtualenv`
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/chrys/my_rag.git
cd my_rag
```

### 2. Set Up Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements/requirements.txt
```
*(Optional: For local AI/vector index features, also run `pip install -r requirements/requirements-ai.txt`)*

### 4. Environment Configuration
Create a `.env` file in the root directory and configure required variables:
```env
DEBUG=True
SECRET_KEY=your-secret-key
GEMINI_API_KEY=your-gemini-api-key
```

### 5. Database Setup & Migrations
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Run the Application
Start the Django development server:
```bash
python manage.py runserver
```
Or use the convenience startup script:
```bash
./run.sh
```

Access the application at `http://127.0.0.1:8000/`.

## Project Documentation
For more detailed information on specific aspects of the platform, please refer to the following documents:
- [Platform Functionality Overview](Documentation/Project/FUNCTIONALITY.md): A deep dive into what the platform can do.
- [API Overview](Documentation/API/README.md): Information for integrating the platform with other systems.
- [User Management and Access Control](Documentation/Project/USER_MANAGEMENT.md): How we handle security and data isolation.
- [Google File Search Projects](Documentation/Google_File_Search/README.md): Details on our cloud-based AI capabilities.
- [Local Projects](Documentation/local_projects/README.md): Information on our privacy-focused local processing.