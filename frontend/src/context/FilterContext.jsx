import { useState } from "react";
import { FilterContext } from "./FilterContext";

export function FilterProvider({ children }) {
  const [filters, setFilters] = useState({});
  const value = { filters, setFilters };
  return <FilterContext.Provider value={value}>{children}</FilterContext.Provider>;
}
