import axios from "axios";

const api = axios.create({
  baseURL: "",
  timeout: 12000,
  withCredentials: true,
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && !window.location.hash.includes("/login")) {
      window.location.hash = "#/login";
    }
    return Promise.reject(error);
  },
);

export function errorMessage(error, fallback = "操作失败，请稍后重试") {
  return error.response?.data?.message || fallback;
}

export default api;
