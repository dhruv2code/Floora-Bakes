import axios from "axios";

const defaultApiUrl = "https://floora-bakes-1.onrender.com/api";
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || defaultApiUrl,
  timeout: 30000,
});

export const getDashboard = (params = {}) => api.get("/dashboard", { params });
export const getAnalytics = (params = {}) => api.get("/analytics/overview", { params });
export const getItems = (params = {}) => api.get("/analytics/items", { params });
export const getDays = (params = {}) => api.get("/analytics/days", { params });
export const getTime = (params = {}) => api.get("/analytics/time", { params });
export const getShare = (params = {}) => api.get("/analytics/share", { params });
export const getWaste = (params = {}) => api.get("/analytics/waste", { params });
export const getInsights = (params = {}) => api.get("/insights", { params });
export const getRecommendations = (params = {}) => api.get("/recommendations", { params });
export const getSales = (params = {}) => api.get("/sales", { params });
export const getUploads = () => api.get("/upload/history");
export const previewUpload = (file) => {
  const form = new FormData();
  form.append("file", file);
  return api.post("/upload/preview", form, { headers: { "Content-Type": "multipart/form-data" } });
};
export const importUpload = (file, mapping) => {
  const form = new FormData();
  form.append("file", file);
  form.append("mapping", JSON.stringify(mapping));
  return api.post("/upload", form, { headers: { "Content-Type": "multipart/form-data" } });
};
export const exportReport = (format, params = {}) => api.get("/reports/export", { params: { format, ...params }, responseType: "blob" });
export const deleteUpload = (id) => api.delete(`/upload/batches/${id}`);
