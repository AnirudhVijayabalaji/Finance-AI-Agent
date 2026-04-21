import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';
import { RefreshCw } from 'lucide-react';
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer
} from 'recharts';

export default function TransactionGraph() {
  const [savings, setSavings] = useState(0);
  const [simResult, setSimResult] = useState(null);
  const [stats, setStats] = useState([]);
  const [loading, setLoading] = useState(false);
  const [insights, setInsights] = useState({
    insight: "Upload a bank statement to get started.",
    reason: "",
    recommendation: ""
  });

  // Hardcoded color palette — Gemini's dynamic class names get purged by Tailwind so we override them here
  const colorMap = {
    "Food & Dining":  "#f97316",
    "Groceries":      "#eab308",
    "Shopping":       "#6366f1",
    "Transport":      "#3b82f6",
    "Transportation": "#3b82f6",
    "Bills":          "#ef4444",
    "Utilities":      "#f87171",
    "Housing":        "#ec4899",
    "Travel":         "#06b6d4",
    "Entertainment":  "#a855f7",
    "Health":         "#22c55e",
    "Subscriptions":  "#8b5cf6",
    "Other":          "#6b7280",
  };

  const getColor = (label) => colorMap[label] || "#818cf8";

  // Also keep the Tailwind bg classes for the legend dots  
  const twColorMap = {
    "Food & Dining":  "bg-orange-500",
    "Groceries":      "bg-yellow-500",
    "Shopping":       "bg-indigo-500",
    "Transport":      "bg-blue-500",
    "Transportation": "bg-blue-500",
    "Bills":          "bg-red-500",
    "Utilities":      "bg-red-400",
    "Housing":        "bg-pink-500",
    "Travel":         "bg-cyan-500",
    "Entertainment":  "bg-purple-500",
    "Health":         "bg-green-500",
    "Subscriptions":  "bg-violet-500",
    "Other":          "bg-gray-500",
  };

  const fetchSummary = useCallback(async (forceRefresh = false) => {
    setLoading(true);
    try {
      const url = forceRefresh
        ? 'http://localhost:8000/summary?refresh=true'
        : 'http://localhost:8000/summary';
      const res = await axios.get(url);
      if (res.data && !res.data.error) {
        setSavings(res.data.total_savings || 0);
        setStats(res.data.stats || []);
        setInsights({
          insight: res.data.insight || "No insights found.",
          reason: res.data.reason || "",
          recommendation: res.data.recommendation || ""
        });
      } else {
        setInsights({
          insight: "System Status",
          reason: `Error: ${res.data?.error || "Unknown Failure"}`,
          recommendation: "Check the backend console. The AI might have hit a rate limit."
        });
      }
    } catch (err) {
      setInsights({
        insight: "Network Error",
        reason: err.message,
        recommendation: "Make sure your FastAPI server is running!"
      });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchSummary(); }, [fetchSummary]);

  const handleSimulate = () => {
    const cost = parseFloat(prompt('Enter the cost of the item you want to buy (e.g. 50000):'));
    if (isNaN(cost) || cost <= 0) return;
    if (cost <= savings) {
      setSimResult({ affordable: true, text: `✅ Affordable! You have ₹${savings.toLocaleString()}. After buying for ₹${cost.toLocaleString()}, you will have ₹${(savings - cost).toLocaleString()} left.` });
    } else {
      setSimResult({ affordable: false, text: `❌ Not Recommended. This costs ₹${cost.toLocaleString()}, but you only have ₹${savings.toLocaleString()}. Shortfall: ₹${(cost - savings).toLocaleString()}.` });
    }
  };

  // Recharts needs { name, value, fill } format
  const chartData = stats.map(s => ({
    name: s.label,
    value: Number(s.amount),
    fill: getColor(s.label)
  }));

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const d = payload[0];
      return (
        <div className="bg-[#1a1a24] border border-white/10 px-4 py-2 rounded-xl text-sm">
          <p className="font-semibold" style={{ color: d.payload.fill }}>{d.name}</p>
          <p className="text-white">₹{d.value.toLocaleString()}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

      {/* Donut Chart */}
      <div className="glass p-8 rounded-2xl">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-semibold">Spending Category Breakdown</h3>
          <button
            onClick={() => fetchSummary(true)}
            title="Refresh dashboard after uploading a new statement"
            className="text-gray-400 hover:text-indigo-400 transition-colors"
          >
            <RefreshCw size={18} className={loading ? 'animate-spin text-indigo-400' : ''} />
          </button>
        </div>
        {loading ? (
          <div className="flex flex-col items-center justify-center h-48 gap-3">
            <RefreshCw size={32} className="animate-spin text-indigo-400" />
            <p className="text-gray-400 text-sm">AI is analyzing your transactions...</p>
          </div>
        ) : stats.length === 0 ? (
          <p className="text-gray-400 mt-4">No data. Please upload a bank statement first.</p>
        ) : (
          <>
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  innerRadius={70}
                  outerRadius={110}
                  paddingAngle={3}
                  dataKey="value"
                  animationBegin={0}
                  animationDuration={900}
                >
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} stroke="transparent" />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
              </PieChart>
            </ResponsiveContainer>

            {/* Legend */}
            <div className="flex flex-wrap gap-2 mt-2 justify-center">
              {stats.map((s, i) => (
                <div key={i} className="flex items-center gap-1.5 text-xs text-gray-300">
                  <span className={`w-2.5 h-2.5 rounded-full ${twColorMap[s.label] || 'bg-indigo-400'}`}/>
                  {s.label}
                </div>
              ))}
            </div>
          </>
        )}
      </div>

      {/* AI Insights & Simulator */}
      <div className="glass p-8 rounded-2xl flex flex-col justify-between">
        <div>
          <h3 className="text-xl font-semibold mb-4">AI Insights</h3>
          <div className="bg-indigo-500/10 border border-indigo-500/20 p-4 rounded-xl mb-4">
            <p className="text-indigo-200">
              <strong>Insight:</strong> {insights.insight}
            </p>
          </div>

          {simResult ? (
            <div className={`p-4 rounded-xl mb-4 border ${simResult.affordable ? 'bg-green-500/10 border-green-500/30 text-green-200' : 'bg-red-500/10 border-red-500/30 text-red-200'}`}>
              <strong>Simulation Result:</strong><br />{simResult.text}
            </div>
          ) : (
            <p className="text-gray-300 text-sm leading-relaxed">
              {insights.reason && <>Reason: {insights.reason}<br /><br /></>}
              Recommendation: {insights.recommendation}
            </p>
          )}
        </div>
        <button
          onClick={handleSimulate}
          className="mt-8 bg-indigo-500 hover:bg-indigo-600 text-white py-3 rounded-xl font-medium transition-colors w-full shadow-[0_0_20px_rgba(79,70,229,0.3)]"
        >
          Simulate a Purchase
        </button>
      </div>
    </div>
  );
}
