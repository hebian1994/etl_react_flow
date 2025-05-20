/// <reference types="vite/client" />
// src/utils/api.ts
import axios from 'axios';
const API_BASE = import.meta.env.VITE_API_BASE_URL;
const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
