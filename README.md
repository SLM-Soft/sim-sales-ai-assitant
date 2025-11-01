# Sales AI Assistant Chat Application

A modern chat application powered by AWS Bedrock AI models, built with React, TypeScript, and Vite.

## Tech Stack

**Frontend:**
- React 19 + TypeScript
- Vite for fast development and building
- Chakra UI + TailwindCSS for styling
- Zustand for state management
- Axios for API communication

**Backend:**
- Python Netlify Functions (production)
- FastAPI (local development alternative)
- AWS Bedrock for AI model inference
- boto3 for AWS SDK integration

## Quick Start

### Option 1: FastAPI Backend (Traditional)

**Terminal 1 - Backend:**
```bash
cd backend-py
pip install -r requirements.txt
python app.py
```

**Terminal 2 - Frontend:**
```bash
npm install
npm run dev
```

Access the app at `http://localhost:5173`

### Option 2: Netlify Functions (Recommended)

```bash
npm install
npm run dev:netlify
```

Access the app at `http://localhost:8888`

This runs both the frontend and Netlify Functions locally.

## Configuration

### AWS Credentials

The backend requires AWS credentials to access Bedrock:

1. Set environment variables:
   ```bash
   export AWS_REGION=eu-central-1
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export BEDROCK_MODEL_ID=amazon.titan-text-express-v1
   ```

2. Or configure AWS CLI:
   ```bash
   aws configure
   ```

3. For local FastAPI development, copy `.env.example` to `.env`:
   ```bash
   cd backend-py
   cp .env.example .env
   # Edit .env with your credentials
   ```

### Mock Mode (Development without AWS)

Set `USE_MOCK_BEDROCK=true` to test without AWS credentials:

```bash
# For Netlify Functions
export USE_MOCK_BEDROCK=true

# For FastAPI
# Add to backend-py/.env
USE_MOCK_BEDROCK=true
```

## Project Structure

```
├── src/                      # Frontend React application
│   ├── components/          # UI components
│   ├── pages/              # Page components
│   ├── store/              # Zustand state management
│   └── api/                # API client functions
├── backend-py/              # FastAPI backend (local dev)
│   ├── app.py              # FastAPI server
│   └── requirements.txt    # Python dependencies
├── netlify/
│   └── functions/          # Netlify Functions (production)
│       ├── checkHealth.py  # Health check endpoint
│       ├── bedrock.py      # AWS Bedrock integration
│       └── requirements.txt # Python dependencies
├── netlify.toml            # Netlify configuration
└── vite.config.ts          # Vite configuration
```

## Available Scripts

- `npm run dev` - Start Vite dev server (use with FastAPI backend)
- `npm run dev:netlify` - Start Netlify Dev (frontend + functions)
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Deployment

### Deploy to Netlify (Recommended)

1. Push your code to GitHub/GitLab/Bitbucket
2. Go to [Netlify Dashboard](https://app.netlify.com)
3. Click "Add new site" → "Import an existing project"
4. Connect your repository
5. Configure environment variables:
   - `AWS_REGION`
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `BEDROCK_MODEL_ID`
6. Deploy!

Netlify will automatically:
- Build the frontend
- Deploy Netlify Functions
- Handle routing with redirects (`/api/*` → functions)

### Deploy to AWS Amplify (Frontend Only)

See `CLAUDE.md` for detailed instructions on deploying to AWS Amplify with separate backend hosting options.

## API Endpoints

- `GET /api/health` - Health check and configuration status
- `POST /api/bedrock` - Send messages to AI model

## Environment Variables

**For Netlify Functions:**
- `AWS_REGION` - AWS region (default: eu-central-1)
- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key
- `BEDROCK_MODEL_ID` - Model ID (default: amazon.titan-text-express-v1)
- `USE_MOCK_BEDROCK` - Enable mock mode (optional)

**For Frontend:**
- `VITE_API_URL` - API base URL (optional, for custom backend URL)

## Documentation

See `CLAUDE.md` for comprehensive development and deployment documentation.

## License

MIT