import { ForexDashboard } from "@/components/Dashbaord"
import { ScrapedDataPage } from "@/components/ScrapedDataPage"
import { WeeklySignalsPage } from "@/components/WeeklySignalsPage"
import { Loader } from "@/components/ui/loader"
import { ErrorMessage } from "@/components/ui/error-message"
import { useState, useEffect } from "react"
import { TooltipProvider } from "@/components/ui/tooltip"
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import { Header } from "@/components/ui/header"
import axios from "axios"

// Interfaces remain the same
interface Signal {
  pair: string;
  direction: "BUY" | "SELL" | "NEUTRAL";
  strength: "LOW" | "MEDIUM" | "HIGH";
  confidence: string;
  rationale: string;
  impact: "LOW" | "MEDIUM" | "HIGH";
}

interface ForexData {
  status: string;
  message: string;
  db_result: {
    success: boolean;
    updated: boolean;
    message: string;
  };
  signals: {
    market_summary: string;
    signals: Signal[];
    date: string;
    timestamp: string;
  };
}

export default function App() {
  const api = import.meta.env.VITE_API_URL
  const [forexData, setForexData] = useState<ForexData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchForexData = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${api}/signals`)
      console.log("API response:", response.data)
      
      // Transform API response to match expected ForexData structure
      if (response.data && response.data.signals && response.data.signals.length > 0) {
        const signalData = response.data.signals[0];
        
        const transformedData: ForexData = {
          status: response.data.status || "",
          message: response.data.message || "",
          db_result: {
            success: true,
            updated: true,
            message: "Data fetched successfully"
          },
          signals: {
            market_summary: signalData.market_summary || "",
            signals: signalData.signals || [],
            date: signalData.date || "",
            timestamp: signalData.timestamp || ""
          }
        };
        
        console.log("Transformed data:", transformedData);
        setForexData(transformedData);
        setError(null);
      } else {
        console.error("Invalid or empty response data:", response.data);
        setError("Invalid data format received from API.");
      }
    } catch (err) {
      console.error("Error fetching forex data:", err)
      setError("Failed to fetch forex data. Please try again later.")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchForexData()
  }, [])

  if (loading) {
    return <Loader />
  }

  if (error || !forexData) {
    return <ErrorMessage message={error || "Failed to load data"} onRetry={fetchForexData} />
  }

  return (
    <TooltipProvider>
      <BrowserRouter>
        <div className="min-h-screen bg-background">
          <Header />
          
          <main className="container mx-auto px-4 py-6">
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<ForexDashboard data={forexData} />} />
              <Route path="/scraped-data" element={<ScrapedDataPage />} />
              <Route path="/weekly-signals" element={<WeeklySignalsPage />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </TooltipProvider>
  )
}