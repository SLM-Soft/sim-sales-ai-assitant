# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a sales AI assistant chat application with a React + TypeScript frontend (Vite) and Python FastAPI backend that integrates with AWS Bedrock for AI model inference.

**Architecture:**
- **Frontend**: React 19 + TypeScript + Vite + Chakra UI + TailwindCSS
- **Backend**: Python FastAPI server that proxies requests to AWS Bedrock
- **State Management**: Zustand for client-side state
- **API Communication**: Axios with Vite dev server proxy

## Development Setup

### Frontend Development

```bash
# Install dependencies
npm install

# Run development server (port 5173)
npm run dev

# Build for production
npm run build

# Run linter
npm run lint

# Preview production build
npm run preview
```

### Backend Development

```bash
cd backend-py

# Install Python dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env
# Edit .env with your AWS credentials

# Run backend server (port 3000)
python app.py
```

### AWS Configuration

The backend requires AWS credentials to access Bedrock. Configure one of:
1. Environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
2. AWS CLI configuration (`~/.aws/credentials`)
3. IAM role (when deployed)

**Environment Variables** (backend-py/.env):
- `AWS_REGION` - AWS region (default: eu-central-1)
- `AWS_ACCESS_KEY_ID` - Your AWS access key
- `AWS_SECRET_ACCESS_KEY` - Your AWS secret key
- `BEDROCK_MODEL_ID` - Model to use (default: anthropic.claude-3-5-sonnet-20240620-v1:0)
- `PORT` - Backend port (default: 3000)
- `USE_MOCK_BEDROCK` - Set to "true" for mock responses during development

## Architecture Details

### Frontend Structure

- **src/pages/HomePage.tsx** - Main application page
- **src/components/** - React components for chat interface
  - `ChatBoxNew.tsx` - Main chat container
  - `MessagesList.tsx` - Displays chat messages
  - `InputRow.tsx` - User input field
  - `Message.tsx` - Individual message component
  - `ChatHeader.tsx` - Chat header
  - `FirstOptionsGrid.tsx`, `SecondOptionsGrid.tsx`, `OptionsGrid.tsx` - Option selection grids
  - `SelectedOptionDisplay.tsx` - Shows selected options
- **src/store/chatStore.ts** - Zustand store managing chat messages
- **src/api/bedrock.ts** - API client for backend communication
- **src/mock/** - Mock data for development

### Backend Structure

- **backend-py/app.py** - FastAPI application with two main endpoints:
  - `GET /api/health` - Health check endpoint
  - `POST /api/bedrock` - Proxies chat requests to AWS Bedrock

### Request Flow

1. User sends message → Frontend (React)
2. `useChatStore` adds user message to state
3. `sendMessage()` from `src/api/bedrock.ts` sends request to `/api/bedrock`
4. Vite dev server proxies `/api/*` to `http://127.0.0.1:3000` (backend)
5. FastAPI backend (`app.py`) formats prompt and calls AWS Bedrock
6. Backend returns response with `{success: boolean, output: string}`
7. Frontend parses `output` (JSON string) to extract `outputText` and `tokenCount`
8. Assistant message added to chat store and displayed

### Key Data Models

**Chat Message** (shared between frontend and backend):
```typescript
interface ChatMessage {
  role: 'User' | 'Assistant';
  content: string;
}
```

**Backend Request**:
```python
class BedrockRequest(BaseModel):
    messages: Optional[List[ChatMessage]] = []
    maxTokens: Optional[int] = 1024
    temperature: Optional[float] = 0 # 0.7
```

**Backend Response**:
```python
class BedrockResponse(BaseModel):
    success: bool
    output: str  # JSON string containing results
```

## Development Workflow

### Running Full Stack

You need two terminal windows:

**Terminal 1 - Backend:**
```bash
cd backend-py
python app.py
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

Access the app at `http://localhost:5173`

### Mock Mode for Development

To develop without AWS credentials, set in `backend-py/.env`:
```
USE_MOCK_BEDROCK=true
```

This returns mock responses without calling AWS Bedrock.

## Deployment

### Frontend Deployment to AWS Amplify

The frontend can be deployed to AWS Amplify Hosting using the `amplify.yml` configuration file.

**Steps:**

1. **Connect Repository to Amplify**
   - Go to AWS Amplify Console
   - Click "New app" → "Host web app"
   - Connect your Git repository (GitHub, GitLab, etc.)
   - Select the branch to deploy (e.g., `main`)

2. **Configure Build Settings**
   - Amplify will auto-detect the `amplify.yml` file
   - Build command: `npm run build`
   - Output directory: `dist`

3. **Set Environment Variables**
   - In Amplify Console, go to "Environment variables"
   - Add: `VITE_API_URL` = your backend API URL
     - Example: `https://your-backend.execute-api.us-east-1.amazonaws.com/api`
     - Or: `https://your-apprunner-url.region.awsapprunner.com/api`
   - **Important**: Without this variable, the app will try to call `/api` which won't work in production

4. **Deploy**
   - Click "Save and deploy"
   - Amplify will build and deploy your frontend

**Configuration Files:**
- `amplify.yml` - Build specification for Amplify
- `src/config.ts` - Environment configuration that reads `VITE_API_URL`

### Backend Deployment Options

The Python FastAPI backend **cannot** be deployed to Amplify. Choose one of these options:

**Option 1: AWS App Runner (Recommended - Easiest)**
- Deploys containerized applications
- Automatic scaling and load balancing
- Configure with `apprunner.yaml` or use console
- Set environment variables for AWS credentials and Bedrock configuration

**Option 2: AWS Lambda + API Gateway**
- Serverless deployment
- Requires adapting FastAPI with Mangum adapter
- Cost-effective for low traffic
- Add to `requirements.txt`: `mangum`

**Option 3: AWS Elastic Beanstalk**
- Platform-as-a-Service for Python
- Create `Procfile`: `web: uvicorn app:app --host 0.0.0.0 --port $PORT`
- Configure environment variables in EB console

**Option 4: ECS/Fargate**
- Container-based deployment
- More control, more complex setup
- Create `Dockerfile` for the backend

**IAM Permissions Required:**
- Backend service needs IAM role/policy with `bedrock:InvokeModel` permission
- Best practice: Use IAM roles instead of hardcoded credentials in production

### Environment Variables for Production

**Frontend (Amplify):**
- `VITE_API_URL` - Full URL to backend API (e.g., `https://api.example.com/api`)

**Backend (wherever deployed):**
- `AWS_REGION` - AWS region for Bedrock
- `BEDROCK_MODEL_ID` - Model identifier
- `PORT` - Server port (use platform default if available)
- AWS credentials via IAM role (preferred) or `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`

## Tech Stack Details

**Frontend Dependencies:**
- `@chakra-ui/react` - UI component library
- `zustand` - Lightweight state management
- `@tanstack/react-query` - Data fetching (installed but check usage)
- `axios` - HTTP client
- `framer-motion` - Animations
- `react-icons` - Icon library
- TailwindCSS v4 - Utility-first CSS

**Backend Dependencies:**
- `fastapi` - Web framework
- `boto3` - AWS SDK for Python
- `pydantic` - Data validation
- `uvicorn` - ASGI server
- `python-dotenv` - Environment variable management

## Important Notes

- The Vite dev server proxy configuration (vite.config.ts) routes `/api/*` requests to the backend
- Frontend expects `resp.data.output` to be a JSON string with `results[0].outputText` structure
- Backend uses `bedrock.invoke_model()` which requires proper AWS IAM permissions for Bedrock
- The application uses port 5173 (frontend) and 3000 (backend) by default
