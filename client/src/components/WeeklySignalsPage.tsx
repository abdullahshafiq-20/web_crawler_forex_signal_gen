import { useState, useEffect } from "react"
import axios from "axios"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { MarketSummary } from "@/components/market-summary"
import { SignalCard } from "@/components/signal-card"
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { cn } from "@/lib/utils"
import { format, parseISO, startOfWeek, addDays, isSameDay } from "date-fns"
import { ArrowUpRight, ArrowDownRight, Minus, Calendar as CalendarIcon, Loader2 } from "lucide-react"

interface Signal {
  pair: string;
  direction: "BUY" | "SELL" | "NEUTRAL";
  strength: string;
  confidence: string;
  rationale: string;
  impact: string;
}

interface SignalData {
  _id: string;
  market_summary: string;
  signals: Signal[];
  date: string;
  timestamp: string;
  createdAt: string;
  updatedAt: string;
}

interface SignalsResponse {
  status: string;
  count: number;
  signals: SignalData[];
}

interface GenerateResponse {
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

export function WeeklySignalsPage() {
  const [selectedDate, setSelectedDate] = useState<string>(
    new Date().toISOString().split("T")[0]
  );
  const [weekDates, setWeekDates] = useState<string[]>([]);
  const [signalsData, setSignalsData] = useState<SignalData | null>(null);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const api = import.meta.env.VITE_API_URL
  
  // Initialize the week dates
  useEffect(() => {
    generateWeekDates(new Date());
  }, []);
  
  // Fetch signals for selected date
  useEffect(() => {
    if (selectedDate) {
      fetchSignalsForDate(selectedDate);
    }
  }, [selectedDate]);
  
  // Generate array of dates for the week containing the given date
  const generateWeekDates = (date: Date) => {
    const start = startOfWeek(date, { weekStartsOn: 1 }); // Start from Monday
    const dates: string[] = [];
    
    for (let i = 0; i < 7; i++) {
      const day = addDays(start, i);
      dates.push(format(day, 'yyyy-MM-dd'));
    }
    
    setWeekDates(dates);
  };
  
  // Fetch signals for a specific date
  const fetchSignalsForDate = async (date: string) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.get<SignalsResponse>(
        `${api}/signals?date=${date}`
      );
      
      if (response.data.status === "success" && response.data.signals.length > 0) {
        setSignalsData(response.data.signals[0]);
      } else {
        setSignalsData(null);
      }
    } catch (err) {
      console.error("Error fetching signals:", err);
      setError("Failed to fetch signals for the selected date.");
    } finally {
      setLoading(false);
    }
  };
  
  // Generate new signals for the selected date
  const generateSignals = async () => {
    try {
      setGenerating(true);
      setError(null);
      setSuccess(null);
      
      const response = await axios.get<GenerateResponse>(
        `${api}/generate-signals`,
      );
      
      if (response.data.status === "success") {
        // Convert the generated signals to the expected format
        const newSignalData: SignalData = {
          _id: new Date().toISOString(),
          market_summary: response.data.signals.market_summary,
          signals: response.data.signals.signals,
          date: response.data.signals.date,
          timestamp: response.data.signals.timestamp,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        };
        
        setSignalsData(newSignalData);
        setSuccess("Successfully generated new signals for the selected date.");
      } else {
        setError("Failed to generate signals. Please try again.");
      }
    } catch (err) {
      console.error("Error generating signals:", err);
      setError("Error occurred while generating signals.");
    } finally {
      setGenerating(false);
    }
  };
  
  // Handle date change from the calendar
  const handleDateChange = (date: Date | undefined) => {
    if (date) {
      const dateString = format(date, 'yyyy-MM-dd');
      setSelectedDate(dateString);
      generateWeekDates(date);
    }
  };
  
  // Get the direction icon and color
  const getDirectionIcon = (direction: Signal["direction"]) => {
    switch (direction) {
      case "BUY":
        return <ArrowUpRight className="h-5 w-5 text-success" />;
      case "SELL":
        return <ArrowDownRight className="h-5 w-5 text-danger" />;
      case "NEUTRAL":
      default:
        return <Minus className="h-5 w-5 text-warning" />;
    }
  };
  
  const getDirectionColor = (direction: Signal["direction"]) => {
    switch (direction) {
      case "BUY":
        return "text-success";
      case "SELL":
        return "text-danger";
      case "NEUTRAL":
      default:
        return "text-warning";
    }
  };
  
  const getStrengthClass = (strength: string) => {
    switch (strength.toUpperCase()) {
      case "LOW":
        return "bg-warning text-warning-foreground";
      case "MEDIUM":
        return "bg-warning/80 text-warning-foreground";
      case "HIGH":
        return "bg-danger text-danger-foreground";
      default:
        return "bg-muted text-muted-foreground";
    }
  };

  return (
    <div>
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 md:mb-8 gap-4">
        <div>
          <h1 className="font-heading text-2xl md:text-3xl font-bold tracking-tight mb-1">
            Weekly Forex Signals
          </h1>
          <p className="text-muted-foreground text-sm md:text-base">
            View and generate forex signals for specific dates
          </p>
        </div>

        <div className="flex flex-wrap gap-3">
          <Popover>
            <PopoverTrigger asChild>
              <Button 
                variant="outline" 
                className="w-full sm:w-auto justify-start text-left font-normal"
              >
                <CalendarIcon className="mr-2 h-4 w-4" />
                {selectedDate ? format(parseISO(selectedDate), 'MMMM d, yyyy') : "Select date"}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="end">
              <Calendar
                mode="single"
                selected={selectedDate ? parseISO(selectedDate) : undefined}
                onSelect={handleDateChange}
              />
            </PopoverContent>
          </Popover>

          <Button 
            onClick={generateSignals} 
            disabled={generating}
            className="bg-primary text-primary-foreground hover:bg-primary/90"
          >
            {generating ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <CalendarIcon className="mr-2 h-4 w-4" />
            )}
            {generating ? "Generating..." : "Generate Signals"}
          </Button>
        </div>
      </div>

      {/* Week selector */}
      <div className="mb-6 overflow-x-auto">
        <div className="flex space-x-2 min-w-max">
          {weekDates.map((date) => (
            <Button
              key={date}
              variant="outline"
              onClick={() => setSelectedDate(date)}
              className={cn(
                "px-3 py-1 h-auto text-xs sm:text-sm",
                selectedDate === date && "bg-primary text-primary-foreground border-primary"
              )}
            >
              <div className="flex flex-col items-center">
                <span>{format(parseISO(date), 'EEE')}</span>
                <span className="font-bold">{format(parseISO(date), 'd')}</span>
              </div>
            </Button>
          ))}
        </div>
      </div>

      {/* Error and success messages */}
      {error && (
        <div className="bg-destructive/10 border border-destructive/30 text-destructive px-4 py-3 rounded-md mb-6">
          {error}
        </div>
      )}

      {success && (
        <div className="bg-success/10 border border-success/30 text-success px-4 py-3 rounded-md mb-6">
          {success}
        </div>
      )}

      {/* Loading state */}
      {loading && (
        <Card className="border-border/30 shadow-card mb-6">
          <CardContent className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </CardContent>
        </Card>
      )}

      {/* No data state */}
      {!loading && !signalsData && (
        <Card className="border-border/30 shadow-card">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <CalendarIcon className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-xl font-medium mb-2">No Signals Available</h3>
            <p className="text-center text-muted-foreground max-w-md mb-6">
              There are no forex signals available for the selected date. 
              Generate new signals or select a different date.
            </p>
            <Button 
              onClick={generateSignals} 
              disabled={generating}
              className="bg-primary text-primary-foreground hover:bg-primary/90"
            >
              {generating ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <CalendarIcon className="mr-2 h-4 w-4" />
              )}
              Generate Signals
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Display signals data */}
      {!loading && signalsData && (
        <div className="space-y-6">
          {/* Market summary */}
          {/* <MarketSummary summary={signalsData.market_summary} /> */}

          {/* Signals */}
          <Card className="border-border/30 shadow-card">
            <CardHeader className="bg-card p-4 border-b border-border/30">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Forex Signals</CardTitle>
                <div className="text-sm text-muted-foreground">
                  {format(parseISO(signalsData.date), 'MMMM d, yyyy')}
                </div>
              </div>
            </CardHeader>
            <CardContent className="p-4">
              <Tabs defaultValue="all">
                <TabsList className="mb-4">
                  <TabsTrigger value="all">All Signals</TabsTrigger>
                  <TabsTrigger value="buy">Buy</TabsTrigger>
                  <TabsTrigger value="sell">Sell</TabsTrigger>
                  <TabsTrigger value="neutral">Neutral</TabsTrigger>
                </TabsList>

                <TabsContent value="all" className="mt-0">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
                    {signalsData.signals.map((signal, index) => (
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
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
                    {signalsData.signals
                      .filter(signal => signal.direction === "BUY")
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
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
                    {signalsData.signals
                      .filter(signal => signal.direction === "SELL")
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
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
                    {signalsData.signals
                      .filter(signal => signal.direction === "NEUTRAL")
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
              </Tabs>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}