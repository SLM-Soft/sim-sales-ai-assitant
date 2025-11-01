/**
 * Application configuration
 *
 * Environment variables:
 * - VITE_API_URL: Backend API URL for production (e.g., https://your-backend.execute-api.region.amazonaws.com)
 */

// Get API base URL from environment variable or use /api for local development
// In production, set VITE_API_URL in Amplify environment variables
export const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

console.log('>>>> API_BASE_URL:', API_BASE_URL)
// Other config values can be added here as needed
export const config = {
  apiBaseUrl: API_BASE_URL,
} as const;
