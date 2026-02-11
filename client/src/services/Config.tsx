export const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false';
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// Export for easy debugging
if (import.meta.env.DEV) {
  console.log('🔧 API Configuration:', {
    USE_MOCK,
    API_BASE_URL,
  });
}
