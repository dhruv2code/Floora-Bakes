import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { ArrowDownRight, ArrowUpRight, CalendarDays, Clock3, PackageCheck, ReceiptText, ShoppingBag, Sparkles, TrendingUp } from "lucide-react";
import { Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { getDashboard, getInsights, getRecommendations } from "../services/api";
import { useFilters } from "../context/useFilters";
import { Card, FadeIn, LoadingScreen, SectionTitle } from "./ui";

const currency = new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 });
const compactCurrency = new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", notation: "compact", maximumFractionDigits: 1 });

function KpiCard({ icon: Icon, label, value, note, accent }) {
  return <FadeIn><Card className="relative overflow-hidden p-5"><div className={`absolute -right-8 -top-8 h-24 w-24 rounded-full ${accent}`} /><div className="relative"><div className="mb-5 flex items-center justify-between"><div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#fff0e4] text-cinnamon"><Icon size={19} /></div><span className="rounded-full bg-[#f1f6ef] px-2 py-1 text-[10px] font-bold text-[#4e744d]">LIVE</span></div><p className="text-xs font-semibold uppercase tracking-wider text-[#8d7970]">{label}</p><p className="mt-2 font-display text-2xl font-bold text-ink">{value}</p><p className="mt-2 text-xs text-[#9a887e]">{note}</p></div></Card></FadeIn>;
}

function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return <div className="rounded-xl border border-[#eadfd3] bg-white/95 p-3 shadow-soft"><p className="mb-1 text-xs font-semibold text-[#8b776b]">{label}</p>{payload.map((item) => <p key={item.dataKey} className="text-sm font-bold text-ink">{item.dataKey === "revenue" ? currency.format(item.value) : item.value}</p>)}</div>;
}

export default function Dashboard() {
  const [analytics, setAnalytics] = useState(null);
  const [insights, setInsights] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const { filters } = useFilters();

  useEffect(() => {
    setLoading(true);
    Promise.all([getDashboard(filters), getInsights(filters), getRecommendations(filters)]).then(([dashboard, insightResponse, recommendationResponse]) => {
      setAnalytics(dashboard.data); setInsights(insightResponse.data.items); setRecommendations(recommendationResponse.data.items); setLoading(false);
    }).catch(() => { setError("Unable to load analytics. Check the API connection."); setLoading(false); });
  }, [filters]);

  const kpis = analytics?.kpis || {};
  const topItems = analytics?.top_items || [];
  const shareData = useMemo(() => analytics?.sales_share?.slice(0, 6).map((item, index) => ({ name: item.item_name, value: item.revenue, color: ["#D86A2E", "#B94D20", "#E9A066", "#7B4B3A", "#C8936B", "#E1B795"][index % 6] })) || [], [analytics]);
  const dayData = analytics?.day_analysis || [];

  if (loading) return <LoadingScreen />;
  if (error) return <Card className="p-8 text-center text-sm text-red-600">{error}</Card>;
  if (!analytics?.kpis?.total_transactions) return <div className="text-center"><h1 className="text-2xl font-bold">No data loaded</h1></div>;

  return <div className="space-y-7">
    <div className="flex flex-col justify-between gap-3 md:flex-row md:items-end"><div><p className="mb-1 text-xs font-bold uppercase tracking-[0.18em] text-cinnamon">Business intelligence</p><h1 className="font-display text-3xl font-bold sm:text-4xl">Your bakery at a glance.</h1><p className="mt-2 text-sm text-[#806f63]">Notify your team of sales performance, demand, and profitable opportunities.</p></div><div className="flex items-center gap-2 rounded-xl border border-[#eadfd3] bg-white px-3 py-2 text-xs font-medium text-[#74645a]"><CalendarDays size={15} /> Live analytics</div></div>
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      <KpiCard icon={ReceiptText} label="Total sales" value={currency.format(kpis.total_sales)} note="Across all imported records" accent="bg-[#f6c9a9]/50" />
      <KpiCard icon={ShoppingBag} label="Transactions" value={kpis.total_transactions.toLocaleString()} note="Completed sales records" accent="bg-[#f2dfcb]/70" />
      <KpiCard icon={TrendingUp} label="Average sale" value={currency.format(kpis.average_sale)} note="Revenue per transaction" accent="bg-[#f4c6b0]/50" />
      <KpiCard icon={PackageCheck} label="Best seller" value={kpis.best_seller_by_revenue || "—"} note="By total revenue" accent="bg-[#edc1a5]/60" />
      <KpiCard icon={ArrowUpRight} label="Best day" value={kpis.best_day || "—"} note="Highest revenue day" accent="bg-[#f2d2bd]/70" />
      <KpiCard icon={Clock3} label="Peak time" value={kpis.peak_time || "—"} note={`${kpis.peak_time_start || "—"} to ${kpis.peak_time_end || "—"}`} accent="bg-[#f1c8ad]/50" />
    </div>
    <div className="grid gap-5 xl:grid-cols-[1.5fr_1fr]">
      <Card className="p-5 sm:p-6"><SectionTitle eyebrow="Revenue movement" title="Sales over time" description="Daily revenue and transaction volume" /><div className="h-[290px]"><ResponsiveContainer width="100%" height="100%"><AreaChart data={analytics.sales_trend}><defs><linearGradient id="salesGradient" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#D86A2E" stopOpacity={0.35}/><stop offset="95%" stopColor="#D86A2E" stopOpacity={0}/></linearGradient></defs><CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#eee2d7" /><XAxis dataKey="label" tick={{ fontSize: 11, fill: "#8d7970" }} interval={Math.max(0, analytics.sales_trend.length - 8)} /><YAxis tickFormatter={(value) => compactCurrency.format(value)} tick={{ fontSize: 11, fill: "#8d7970" }} /><Tooltip content={<ChartTooltip />} /><Area type="monotone" dataKey="revenue" stroke="#D86A2E" strokeWidth={3} fill="url(#salesGradient)" animationDuration={900} /></AreaChart></ResponsiveContainer></div></Card>
      <Card className="p-5 sm:p-6"><SectionTitle eyebrow="Daily performance" title="Sales by weekday" /><div className="h-[290px]"><ResponsiveContainer width="100%" height="100%"><BarChart data={dayData}><CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#eee2d7" /><XAxis dataKey="day" tick={{ fontSize: 10, fill: "#8d7970" }} /><YAxis tickFormatter={(value) => compactCurrency.format(value)} tick={{ fontSize: 11, fill: "#8d7970" }} /><Tooltip content={<ChartTooltip />} /><Bar dataKey="revenue" fill="#B94D20" radius={[6, 6, 0, 0]} animationDuration={900} /></BarChart></ResponsiveContainer></div></Card>
    </div>
    <div className="grid gap-5 xl:grid-cols-[1.25fr_0.75fr]">
      <Card className="p-5 sm:p-6"><SectionTitle eyebrow="Product performance" title="Top-selling products" description="Ranked by revenue" /><div className="space-y-4">{topItems.slice(0, 5).map((item, index) => <div key={item.item_name}><div className="mb-1.5 flex justify-between text-sm"><span className="font-semibold">{index + 1}. {item.item_name}</span><span className="font-bold text-cinnamon">{currency.format(item.revenue)}</span></div><div className="h-2 overflow-hidden rounded-full bg-[#f3ebe3]"><motion.div initial={{ width: 0 }} animate={{ width: `${Math.max(8, (item.revenue / topItems[0]?.revenue) * 100)}%` }} transition={{ delay: index * 0.08, duration: 0.7 }} className="h-full rounded-full bg-gradient-to-r from-caramel to-[#E8A064]" /></div></div>)}</div></Card>
      <Card className="p-5 sm:p-6"><SectionTitle eyebrow="Revenue mix" title="Sales share" /><div className="h-[220px]"><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={shareData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={56} outerRadius={80} paddingAngle={3}>{shareData.map((entry) => <Cell key={entry.name} fill={entry.color} />)}</Pie><Tooltip formatter={(value) => currency.format(value)} /></PieChart></ResponsiveContainer></div><div className="grid grid-cols-2 gap-2">{shareData.slice(0, 4).map((entry) => <div key={entry.name} className="flex items-center gap-2 text-xs"><span className="h-2.5 w-2.5 rounded-full" style={{ background: entry.color }} /><span className="truncate">{entry.name}</span></div>)}</div></Card>
    </div>
    <Card className="p-5 sm:p-6"><SectionTitle eyebrow="Automated intelligence" title="Insights & recommendations" /><div className="grid gap-4 lg:grid-cols-2"><div><p className="mb-3 text-xs font-bold uppercase tracking-wider text-cinnamon">Business insights</p><div className="space-y-3">{insights.map((insight, index) => <div key={index} className="flex gap-3 rounded-2xl bg-[#fff8f1] p-4"><Sparkles className="mt-0.5 shrink-0 text-cinnamon" size={17} /><p className="text-sm leading-6 text-[#5f5048]">{insight}</p></div>)}</div></div><div><p className="mb-3 text-xs font-bold uppercase tracking-wider text-cinnamon">Recommended actions</p><div className="space-y-3">{recommendations.map((recommendation, index) => <div key={index} className="flex gap-3 rounded-2xl border border-[#eadfd3] p-4"><span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[#f5e1d3] text-xs font-bold text-caramel">{index + 1}</span><p className="text-sm leading-6 text-[#5f5048]">{recommendation}</p></div>)}</div></div></div></Card>
  </div>;
}
