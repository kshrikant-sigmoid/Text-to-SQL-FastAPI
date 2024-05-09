import axios from 'axios';

// Create an axios instance
const instance = axios.create({
  baseURL: 'http://localhost:8000/',
});

// Add a request interceptor
instance.interceptors.request.use((config) => {
  const token = document.cookie.replace(/(?:(?:^|.*;\s*)token\s*=\s*([^;]*).*$)|^.*$/, "$1");
  config.headers.Authorization =  token ? `Bearer ${token}` : '';
  return config;
});

export default instance;