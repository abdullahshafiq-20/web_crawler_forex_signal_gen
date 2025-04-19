"use client"

import { useState } from "react"
import { MarketSummary } from "@/components/market-summary"
import { SignalCard } from "@/components/signal-card"
import { formatDate } from "@/lib/utils"
import { ArrowUpRight, ArrowDownRight, Minus, RefreshCw, SearchIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Header } from "@/components/ui/header"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

interface ForexData {
  status: string
  message: string
  db_result: {
    success: boolean
    updated: boolean
    message: string
  }
  signals: {
    market_summary: string
    signals: Signal[]
    date: string
    timestamp: string
  }
}

interface Signal {
  pair: string
  direction: "BUY" | "SELL" | "NEUTRAL"
  strength: "LOW" | "MEDIUM" | "HIGH"
  confidence: string
  rationale: string
  impact: "LOW" | "MEDIUM" | "HIGH"
}

export function ForexDashboard({ data }: { data?: ForexData }) {
    const api = import.meta.env.VITE_API_URL
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")

  // Add a null check for data
  if (!data || !data.signals) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <div className="text-center max-w-md">
          <h2 className="text-xl sm:text-2xl font-heading text-primary mb-3 sm:mb-4">Loading Forex Data...</h2>
          <p className="text-sm sm:text-base text-muted-foreground">Please wait while we fetch the latest signals.</p>
        </div>
      </div>
    )
  }

  const handleRefresh = () => {
    setIsRefreshing(true)
    // Simulate refresh
    setTimeout(() => {
      setIsRefreshing(false)
    }, 1500)
  }

  const getDirectionIcon = (direction: Signal["direction"]) => {
    switch (direction) {
      case "BUY":
        return <ArrowUpRight className="h-5 w-5 text-success" />
      case "SELL":
        return <ArrowDownRight className="h-5 w-5 text-danger" />
      case "NEUTRAL":
      default:
        return <Minus className="h-5 w-5 text-warning" />
    }
  }

  const getDirectionColor = (direction: Signal["direction"]) => {
    switch (direction) {
      case "BUY":
        return "text-success"
      case "SELL":
        return "text-danger"
      case "NEUTRAL":
      default:
        return "text-warning"
    }
  }

  const getStrengthClass = (strength: Signal["strength"]) => {
    switch (strength) {
      case "LOW":
        return "bg-warning text-warning-foreground"
      case "MEDIUM":
        return "bg-warning/80 text-warning-foreground"
      case "HIGH":
        return "bg-danger text-danger-foreground"
      default:
        return "bg-muted text-muted-foreground"
    }
  }

  // Filter signals based on search query
  const filteredSignals = Array.isArray(data.signals.signals) 
    ? data.signals.signals.filter(signal => 
        searchQuery ? 
        signal.pair.toLowerCase().includes(searchQuery.toLowerCase()) || 
        signal.rationale.toLowerCase().includes(searchQuery.toLowerCase()) 
        : true
      )
    : []

  return (
    <div className="min-h-screen bg-background text-foreground">
      <main>
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-6 md:mb-8 gap-3 md:gap-4">
          <div>
            <h1 className="font-heading text-2xl md:text-3xl font-bold tracking-tight text-foreground mb-1">
              Market Analysis
            </h1>
            <div className="flex flex-wrap items-center gap-2 sm:gap-3 text-muted-foreground">
              <p className="text-xs sm:text-sm">Last updated: {formatDate(data.signals.timestamp || "")}</p>
              <div className="h-1.5 w-1.5 rounded-full bg-success hidden sm:block"></div>
              <p className="text-xs sm:text-sm">Date: {data.signals.date || "N/A"}</p>
            </div>
          </div>
          
          <div className="flex flex-col sm:flex-row w-full sm:w-auto gap-2 sm:gap-3">
            <div className="relative flex-grow sm:flex-grow-0 sm:min-w-[200px]">
              <input 
                type="text" 
                placeholder="Search signals..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9 pr-4 py-2 h-9 w-full rounded-md border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/30"
              />
              <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
            </div>
            <Button
              onClick={handleRefresh}
              className="bg-primary text-primary-foreground hover:bg-primary/90 h-9"
            >
              <RefreshCw className={`h-3.5 w-3.5 mr-2 ${isRefreshing ? "animate-spin" : ""}`} />
              Refresh
            </Button>
          </div>
        </div>

        <MarketSummary summary={data.signals.market_summary} />

        <Card className="mt-6 md:mt-8 p-0 sm:p-1 border-border/30 shadow-card">
          <Tabs defaultValue="all" className="w-full">
            <TabsList className="w-full sm:w-auto justify-start border-b border-border/30 rounded-none bg-transparent h-auto p-0">
              <TabsTrigger 
                value="all" 
                className="data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:border-primary data-[state=active]:border-b-2 rounded-none px-3 sm:px-4 py-2 text-xs sm:text-sm"
              >
                All Signals
                <Badge variant="secondary" className="ml-1.5 bg-muted text-muted-foreground text-xs py-0 h-5">
                  {filteredSignals.length}
                </Badge>
              </TabsTrigger>
              <TabsTrigger 
                value="buy" 
                className="data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:border-success data-[state=active]:border-b-2 rounded-none px-3 sm:px-4 py-2 text-xs sm:text-sm"
              >
                Buy
                <Badge variant="secondary" className="ml-1.5 bg-muted text-muted-foreground text-xs py-0 h-5">
                  {filteredSignals.filter(s => s.direction === "BUY").length}
                </Badge>
              </TabsTrigger>
              <TabsTrigger 
                value="sell" 
                className="data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:border-danger data-[state=active]:border-b-2 rounded-none px-3 sm:px-4 py-2 text-xs sm:text-sm"
              >
                Sell
                <Badge variant="secondary" className="ml-1.5 bg-muted text-muted-foreground text-xs py-0 h-5">
                  {filteredSignals.filter(s => s.direction === "SELL").length}
                </Badge>
              </TabsTrigger>
              <TabsTrigger 
                value="neutral" 
                className="data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:border-warning data-[state=active]:border-b-2 rounded-none px-3 sm:px-4 py-2 text-xs sm:text-sm"
              >
                Neutral
                <Badge variant="secondary" className="ml-1.5 bg-muted text-muted-foreground text-xs py-0 h-5">
                  {filteredSignals.filter(s => s.direction === "NEUTRAL").length}
                </Badge>
              </TabsTrigger>
            </TabsList>

            <div className="p-3 sm:p-4">
              <TabsContent value="all" className="mt-0">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 md:gap-6">
                  {filteredSignals.map((signal, index) => (
                    <SignalCard
                      key={index}
                      signal={signal}
                      directionIcon={getDirectionIcon(signal.direction)}
                      directionColor={getDirectionColor(signal.direction)}
                      strengthClass={getStrengthClass(signal.strength)}
                    />
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="buy" className="mt-0">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 md:gap-6">
                  {filteredSignals
                    .filter((signal) => signal.direction === "BUY")
                    .map((signal, index) => (
                      <SignalCard
                        key={index}
                        signal={signal}
                        directionIcon={getDirectionIcon(signal.direction)}
                        directionColor={getDirectionColor(signal.direction)}
                        strengthClass={getStrengthClass(signal.strength)}
                      />
                    ))}
                </div>
              </TabsContent>

              <TabsContent value="sell" className="mt-0">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 md:gap-6">
                  {filteredSignals
                    .filter((signal) => signal.direction === "SELL")
                    .map((signal, index) => (
                      <SignalCard
                        key={index}
                        signal={signal}
                        directionIcon={getDirectionIcon(signal.direction)}
                        directionColor={getDirectionColor(signal.direction)}
                        strengthClass={getStrengthClass(signal.strength)}
                      />
                    ))}
                </div>
              </TabsContent>

              <TabsContent value="neutral" className="mt-0">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 md:gap-6">
                  {filteredSignals
                    .filter((signal) => signal.direction === "NEUTRAL")
                    .map((signal, index) => (
                      <SignalCard
                        key={index}
                        signal={signal}
                        directionIcon={getDirectionIcon(signal.direction)}
                        directionColor={getDirectionColor(signal.direction)}
                        strengthClass={getStrengthClass(signal.strength)}
                      />
                    ))}
                </div>
              </TabsContent>
            </div>
          </Tabs>
        </Card>
      </main>
    </div>
  )
}
