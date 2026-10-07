import { motion } from "framer-motion";
import { LoaderCircle } from "lucide-react";

export const Card = ({ children, className = "", ...props }) => (
  <div className={`panel ${className}`} {...props}>{children}</div>
);

export const LoadingScreen = () => (
  <div className="flex min-h-[60vh] items-center justify-center">
    <LoaderCircle className="animate-spin text-cinnamon" size={34} />
    <span className="ml-3 text-sm font-medium text-[#7b685d]">Loading bakery intelligence…</span>
  </div>
);

export const SectionTitle = ({ eyebrow, title, description, action }) => (
  <div className="mb-5 flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
    <div>
      {eyebrow && <p className="mb-1 text-xs font-bold uppercase tracking-[0.18em] text-cinnamon">{eyebrow}</p>}
      <h2 className="font-display text-xl font-bold text-ink sm:text-2xl">{title}</h2>
      {description && <p className="mt-1 text-sm text-[#806f63]">{description}</p>}
    </div>
    {action}
  </div>
);

export const FadeIn = ({ children, delay = 0 }) => (
  <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.45, delay }}>{children}</motion.div>
);

export const EmptyState = ({ onUpload }) => (
  <Card className="flex min-h-[430px] flex-col items-center justify-center px-6 text-center">
    <div className="mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-[#fff0e4] text-cinnamon">✦</div>
    <h2 className="font-display text-2xl font-bold">No sales data yet.</h2>
    <p className="mt-2 max-w-md text-sm leading-6 text-[#806f63]">Upload your Excel file to generate your bakery sales dashboard and actionable business insights.</p>
    <button className="primary-button mt-6" onClick={onUpload}>Upload Sales Data</button>
  </Card>
);
