import dotenv from "dotenv";

dotenv.config();

// API'nin varsayılan URL'si
export const API_URL = process.env.API_URL || "http://localhost:8000/api/v1";
