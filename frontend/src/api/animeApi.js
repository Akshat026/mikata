import axios from "axios";

const BASE_URL = process.env.REACT_APP_API_BASE_URL;

export const searchAnime = async (query) => {
  const response = await axios.get(`${BASE_URL}/search/`, {
    params: { q: query },
  });
  return response.data.results;
};

export const getRecommendations = async (animeName) => {
  const response = await axios.get(`${BASE_URL}/recommend/`, {
    params: { name: animeName },
  });
  return response.data.recommendations;
};