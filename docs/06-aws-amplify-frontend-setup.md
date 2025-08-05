# AWS Amplify Frontend Setup Guide

## Overview

This guide provides step-by-step instructions for setting up AWS Amplify to host the Crypto Trend Analysis Chatbot frontend. Amplify provides a simple, cost-effective solution with built-in CI/CD, global CDN, and automatic HTTPS.

## Prerequisites

- AWS CLI configured with appropriate credentials
- Git repository for frontend code
- Node.js and npm/yarn installed locally
- Basic React/Vue/Angular application ready

## Why AWS Amplify?

**Benefits for Chat Interface:**
- **Zero Server Management**: No EC2 instances to maintain
- **Global CDN**: Fast loading worldwide via CloudFront
- **Automatic HTTPS**: SSL certificates managed automatically
- **Git-based Deployment**: Push to deploy automatically
- **Cost-Effective**: Pay only for storage and data transfer
- **Built-in CI/CD**: Automatic builds on code changes

**Cost Comparison:**
- **Amplify**: ~$1-5/month for MVP traffic
- **EC2 + nginx**: ~$15-30/month minimum

## Step 1: Prepare Frontend Application

### Environment Configuration

Create environment configuration for API endpoints:

**`.env.production`**:
```env
REACT_APP_API_BASE_URL=https://your-api-id.execute-api.us-east-1.amazonaws.com/prod
REACT_APP_API_VERSION=v1
REACT_APP_ENVIRONMENT=production
```

**`.env.development`**:
```env
REACT_APP_API_BASE_URL=http://localhost:3001
REACT_APP_API_VERSION=v1
REACT_APP_ENVIRONMENT=development
```

### Build Configuration

**For React Applications**:
```json
{
  "scripts": {
    "build": "react-scripts build",
    "start": "react-scripts start",
    "test": "react-scripts test"
  }
}
```

**For Vue Applications**:
```json
{
  "scripts": {
    "build": "vue-cli-service build",
    "serve": "vue-cli-service serve"
  }
}
```

## Step 2: AWS Amplify Setup

### Option A: AWS Console Setup (Recommended for beginners)

1. **Navigate to AWS Amplify Console**:
   - Go to [AWS Amplify Console](https://console.aws.amazon.com/amplify/)
   - Click "New app" → "Host web app"

2. **Connect Git Repository**:
   - Choose your Git provider (GitHub, GitLab, Bitbucket, CodeCommit)
   - Authorize AWS Amplify to access your repository
   - Select the frontend repository and branch (main/master)

3. **Configure Build Settings**:
   ```yaml
   version: 1
   frontend:
     phases:
       preBuild:
         commands:
           - npm ci
       build:
         commands:
           - npm run build
     artifacts:
       baseDirectory: build
       files:
         - '**/*'
     cache:
       paths:
         - node_modules/**/*
   ```

4. **Environment Variables**:
   - Add environment variables from your `.env.production` file
   - Set `REACT_APP_API_BASE_URL` to your API Gateway URL

5. **Deploy**:
   - Review settings and click "Save and Deploy"
   - First deployment takes 5-10 minutes

### Option B: AWS CLI Setup

1. **Install Amplify CLI**:
```bash
npm install -g @aws-amplify/cli
amplify configure
```

2. **Initialize Amplify Project**:
```bash
cd your-frontend-project
amplify init

# Follow prompts:
# - Project name: crypto-analysis-frontend
# - Environment: prod
# - Default editor: VS Code
# - App type: javascript
# - Framework: react (or your framework)
# - Source directory: src
# - Build command: npm run build
# - Start command: npm start
```

3. **Add Hosting**:
```bash
amplify add hosting

# Choose:
# - Hosting with Amplify Console
# - Manual deployment (or CI/CD setup)
```

4. **Deploy**:
```bash
amplify push
```

## Step 3: Configure Custom Domain (Optional)

### Using AWS Route 53

1. **Purchase/Import Domain**:
   - Go to Route 53 in AWS Console
   - Register new domain or import existing domain

2. **Add Custom Domain in Amplify**:
   - In Amplify Console, go to "Domain management"
   - Click "Add domain"
   - Enter your domain name (e.g., `crypto-analysis.com`)
   - Add subdomain if needed (e.g., `app.crypto-analysis.com`)

3. **DNS Configuration**:
   - Amplify automatically creates SSL certificate
   - Update nameservers if domain is external
   - DNS propagation takes 24-48 hours

### Example Configuration:
```
Domain: crypto-analysis.com
Subdomain: app.crypto-analysis.com → points to Amplify app
API: api.crypto-analysis.com → points to API Gateway (configure separately)
```

## Step 4: Environment Variables Configuration

### Required Environment Variables:

```env
# API Configuration
REACT_APP_API_BASE_URL=https://abc123.execute-api.us-east-1.amazonaws.com/prod
REACT_APP_API_TIMEOUT=10000

# Feature Flags
REACT_APP_ENABLE_ANALYTICS=true
REACT_APP_ENABLE_ERROR_REPORTING=true

# Application Settings
REACT_APP_APP_NAME=Crypto Trend Analysis
REACT_APP_VERSION=1.0.0
```

### Setting in Amplify Console:
1. Go to "App settings" → "Environment variables"
2. Add each variable with appropriate values
3. Redeploy application for changes to take effect

## Step 5: CORS Configuration

Ensure your API Gateway has proper CORS settings for Amplify domain:

```json
{
  "Access-Control-Allow-Origin": "https://main.d1234567890.amplifyapp.com",
  "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
  "Access-Control-Allow-Methods": "GET,POST,OPTIONS"
}
```

**For custom domain**:
```json
{
  "Access-Control-Allow-Origin": "https://app.crypto-analysis.com",
  "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
  "Access-Control-Allow-Methods": "GET,POST,OPTIONS"
}
```

## Step 6: Build Optimizations

### Optimize Bundle Size

**webpack-bundle-analyzer** (for React):
```bash
npm install --save-dev webpack-bundle-analyzer
npm run build
npx webpack-bundle-analyzer build/static/js/*.js
```

### Code Splitting Example:
```javascript
// Lazy load components
const QueryInterface = React.lazy(() => import('./components/QueryInterface'));
const ResultDisplay = React.lazy(() => import('./components/ResultDisplay'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <QueryInterface />
      <ResultDisplay />
    </Suspense>
  );
}
```

### Performance Optimizations:
```javascript
// Service worker for caching
// Add to public/sw.js
self.addEventListener('fetch', event => {
  if (event.request.destination === 'script' || 
      event.request.destination === 'style') {
    event.respondWith(
      caches.open('static-cache').then(cache => {
        return cache.match(event.request) || fetch(event.request);
      })
    );
  }
});
```

## Step 7: Monitoring and Analytics

### CloudWatch Integration

Amplify automatically provides:
- **Build Logs**: Available in Amplify Console
- **Access Logs**: Via CloudWatch
- **Error Monitoring**: JavaScript errors tracked

### Custom Analytics (Optional):
```javascript
import { Analytics } from 'aws-amplify';

// Track user queries
Analytics.record({
  name: 'userQuery',
  attributes: {
    query: userInput,
    intent: detectedIntent,
    resultCount: results.length
  }
});

// Track performance
Analytics.record({
  name: 'apiResponseTime',
  metrics: {
    duration: responseTime
  }
});
```

## Step 8: Automated Deployments

### Branch-based Deployments

Configure multiple environments:

1. **Production Branch** (`main`):
   - Auto-deploy to production
   - Custom domain attached
   - Production environment variables

2. **Development Branch** (`develop`):
   - Auto-deploy to staging
   - Different API endpoints
   - Development environment variables

### GitHub Actions Integration (Optional):

```yaml
# .github/workflows/amplify-deploy.yml
name: Deploy to Amplify

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '16'
          
      - name: Install dependencies
        run: npm ci
        
      - name: Run tests
        run: npm test -- --coverage --watchAll=false
        
      - name: Build application
        run: npm run build
        
      - name: Deploy to Amplify
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
```

## Troubleshooting

### Common Issues:

1. **Build Failures**:
   - Check Node.js version compatibility
   - Verify all dependencies are in package.json
   - Check environment variables are set correctly

2. **CORS Errors**:
   - Verify API Gateway CORS configuration
   - Check Amplify domain in allowed origins
   - Test with browser developer tools

3. **Environment Variables Not Working**:
   - Ensure variables start with `REACT_APP_` (for React)
   - Redeploy after adding variables
   - Check case sensitivity

4. **Slow Loading**:
   - Enable compression in build settings
   - Implement code splitting
   - Optimize images and assets

### Build Commands Troubleshooting:

```yaml
# If build fails, try these commands:
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - npm ci --force
        - npm install -g @angular/cli  # if Angular
    build:
      commands:
        - npm run build -- --prod     # if Angular
        - npm run build              # if React/Vue
  artifacts:
    baseDirectory: dist             # for Angular
    # baseDirectory: build          # for React
    files:
      - '**/*'
```

## Security Considerations

1. **Environment Variables**: Never commit sensitive data to Git
2. **API Keys**: Use environment variables for all API endpoints
3. **HTTPS**: Amplify provides HTTPS automatically
4. **Content Security Policy**: Consider adding CSP headers
5. **Access Control**: Use CloudFront for additional security layers

## Cost Management

### Amplify Pricing:
- **Build minutes**: $0.01 per minute
- **Hosting**: $0.15 per GB per month
- **Data transfer**: $0.15 per GB (first 15 GB free)

### Cost Optimization:
- Use build cache to reduce build times
- Optimize bundle size to reduce hosting costs
- Consider CloudFront caching policies
- Monitor usage in AWS billing dashboard

## Next Steps

After successful deployment:

1. **Test all functionality** with production API endpoints
2. **Set up monitoring** and error tracking
3. **Configure custom domain** if desired
4. **Set up branch-based deployments** for development workflow
5. **Implement analytics** to track user behavior
6. **Add error boundaries** for better user experience

## Support Resources

- [AWS Amplify Documentation](https://docs.amplify.aws/)
- [Amplify CLI Documentation](https://docs.amplify.aws/cli/)
- [Amplify Console User Guide](https://docs.aws.amazon.com/amplify/latest/userguide/)
- [AWS Amplify Discord Community](https://discord.gg/amplify) 