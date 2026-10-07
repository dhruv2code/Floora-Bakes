import { useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { BarChart3, Boxes, CalendarClock, ChartNoAxesCombined, FileSpreadsheet, Filter, Lightbulb, Menu, Upload, X } from "lucide-react";
import { useFilters } from "../context/useFilters";

const navigation = [
  { label: "Dashboard", path: "/", icon: BarChart3 },
  { label: "Sales", path: "/sales", icon: FileSpreadsheet },
  { label: "Products", path: "/products", icon: Boxes },
  { label: "Time Analysis", path: "/time", icon: CalendarClock },
  { label: "Insights", path: "/insights", icon: Lightbulb },
  { label: "Upload Data", path: "/upload", icon: Upload },
];

export default function Layout() {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const { filters, setFilters } = useFilters();

  const navigateTo = (path) => {
    navigate(path);
    setOpen(false);
  };

  const updateFilter = (field, value) => setFilters((current) => ({ ...current, [field]: value || undefined }));

  return (
    <div className="min-h-screen bg-cream text-ink">
      <aside className={`fixed inset-y-0 left-0 z-50 flex w-[250px] flex-col bg-[#2d211a] px-4 py-6 text-white transition-transform lg:translate-x-0 ${open ? "translate-x-0" : "-translate-x-full"}`}>
        <div className="mb-9 flex items-center gap-3 px-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-cinnamon shadow-lg shadow-cinnamon/25"><ChartNoAxesCombined size={21} /></div>
          <div><p className="font-display text-lg font-bold">Floora Bakes</p><p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-[#c8afa0]">Sales Intelligence</p></div>
        </div>
        <nav className="space-y-1">
          {navigation.map(({ label, path, icon: Icon }) => (
            <NavLink key={path} to={path} onClick={() => navigateTo(path)} className={({ isActive }) => `flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition ${isActive ? "bg-white text-ink shadow-lg" : "text-[#d9c9bd] hover:bg-white/10 hover:text-white"}`}>
              <Icon size={18} />{label}
            </NavLink>
          ))}
        </nav>
        <div className="mt-auto rounded-2xl border border-white/10 bg-white/5 p-4">
          <p className="text-xs font-bold uppercase tracking-wider text-[#e2b99c]">Local workspace</p>
          <p className="mt-2 text-sm text-[#d8c9bd]">Your data stays in this application database.</p>
        </div>
      </aside>
      {open && <button aria-label="Close menu" onClick={() => setOpen(false)} className="fixed inset-0 z-40 bg-[#241711]/50 lg:hidden" />}
      <main className="min-h-screen lg:pl-[250px]">
        <header className="sticky top-0 z-30 flex h-[76px] items-center justify-between border-b border-[#eadfd3] bg-cream/90 px-5 backdrop-blur-xl sm:px-8">
          <button onClick={() => setOpen(true)} className="rounded-xl p-2 text-ink lg:hidden" aria-label="Open menu"><Menu /></button>
          <div className="hidden sm:block"><p className="text-xs font-semibold uppercase tracking-[0.16em] text-cinnamon">Bakery performance</p><p className="font-display text-lg font-bold">Sales overview</p></div>
          <div className="flex items-center gap-3"><div className="flex h-9 w-9 items-center justify-center rounded-full bg-[#e8c7b0] font-bold text-caramel">FB</div><div className="hidden sm:block"><p className="text-sm font-semibold">Floora Team</p><p className="text-xs text-[#907f73]">Owner account</p></div></div>
        </header>
        <div className="p-5 sm:p-8"><div className="mb-6 rounded-2xl border border-[#eadfd3] bg-white p-3 shadow-soft"><div className="flex flex-col gap-3 md:flex-row md:items-center"><div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-cinnamon"><Filter size={15} /> Global filters</div><input className="field min-w-0 flex-1" type="date" value={filters.start_date || ""} onChange={(event) => updateFilter("start_date", event.target.value)} aria-label="Start date" /><input className="field min-w-0 flex-1" type="date" value={filters.end_date || ""} onChange={(event) => updateFilter("end_date", event.target.value)} aria-label="End date" /><button onClick={() => setFilters({})} className="secondary-button">Clear</button></div></div><Outlet /></div>
      </main>
    </div>
  );
}
