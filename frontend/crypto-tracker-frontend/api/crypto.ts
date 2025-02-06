import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:5000"; // Flask backend

export const searchCrypto = async (query: string) => {
  const response = await axios.get(`${API_BASE_URL}/search?query=${query}`);
  return response.data;
};

export const getCryptoDetails = async (cryptoId: string) => {
  const response = await axios.get(`${API_BASE_URL}/crypto/${cryptoId}`);
  return response.data;
};

export const getCryptoHistory = async (cryptoId: string, days: number) => {
  const response = await axios.get(`${API_BASE_URL}/crypto/${cryptoId}/history?days=${days}`);
  return response.data;
};
