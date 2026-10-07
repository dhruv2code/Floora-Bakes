import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./components/Dashboard";
import UploadPage from "./components/UploadPage";
import SalesPage from "./components/SalesPage";
import ProductsPage from "./components/ProductsPage";
import TimePage from "./components/TimePage";
import InsightsPage from "./components/InsightsPage";
import { FilterProvider } from "./context/FilterContext.jsx";

export default function App() {
  return (
    <FilterProvider>
      <Routes>
      <Route element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="sales" element={<SalesPage />} />
        <Route path="products" element={<ProductsPage />} />
        <Route path="time" element={<TimePage />} />
        <Route path="insights" element={<InsightsPage />} />
        <Route path="upload" element={<UploadPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
      </Routes>
    </FilterProvider>
  );
}
