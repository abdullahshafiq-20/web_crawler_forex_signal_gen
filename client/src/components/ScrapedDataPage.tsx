import { useState, useEffect } from "react"
import axios from "axios"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { RefreshCw, Calendar, Clock, Globe, Flag, TrendingUp } from "lucide-react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { DateTime } from "luxon"
import { Calendar as CalendarComponent } from "@/components/ui/luxon-calendar"

interface ScrapedEvent {
  date: string
  time: string
  country: string
  event: string
  impact: string
  actual: string | null
  forecast: string | null
  previous: string | null
  source: string
}

interface ScrapeResponse {
  status: string
  data: ScrapedEvent[]
  db_result: {
    created: number
    updated: number
  }
}

interface EventsResponse {
  status: string
  data: ScrapedEvent[]
}

interface FilterParams {
  start_date?: string
  end_date?: string
  countries?: string[]
  impact?: string[]
  sources?: string[]
}

export function ScrapedDataPage() {
  const [events, setEvents] = useState<ScrapedEvent[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [filters, setFilters] = useState<FilterParams>({})
  const [availableCountries, setAvailableCountries] = useState<string[]>([])
  const [availableSources, setAvailableSources] = useState<string[]>([])
  const [startDate, setStartDate] = useState<Date | undefined>(undefined)
  const [endDate, setEndDate] = useState<Date | undefined>(undefined)
  const api = import.meta.env.VITE_API_URL

  // Fetch events when component mounts
  useEffect(() => {
    fetchEvents()
  }, [])

  // Extract unique countries and sources from events
  useEffect(() => {
    if (events.length > 0) {
      const countries = [...new Set(events.map(event => event.country))].sort()
      const sources = [...new Set(events.map(event => event.source))].sort()
      setAvailableCountries(countries)
      setAvailableSources(sources)
    }
  }, [events])

  // Function to fetch events from database with filters
  const fetchEvents = async (filterParams: FilterParams = {}) => {
    try {
      setLoading(true)
      setError(null)
      
      // Build query parameters
      const params = new URLSearchParams()
      
      if (filterParams.start_date) {
        params.append('start_date', filterParams.start_date)
      }
      
      if (filterParams.end_date) {
        params.append('end_date', filterParams.end_date)
      }
      
      if (filterParams.countries?.length) {
        filterParams.countries.forEach(country => {
          params.append('countries', country)
        })
      }
      
      if (filterParams.impact?.length) {
        filterParams.impact.forEach(impact => {
          params.append('impact', impact)
        })
      }
      
      if (filterParams.sources?.length) {
        filterParams.sources.forEach(source => {
          params.append('sources', source)
        })
      }
      
      const url = `${api}/events${params.toString() ? `?${params}` : ''}`
      const response = await axios.get<EventsResponse>(url)
      
      if (response.data.status === "success" && Array.isArray(response.data.data)) {
        setEvents(response.data.data)
        setSuccess(`Successfully loaded ${response.data.data.length} events from database`)
      } else {
        setError("Invalid response format from server")
      }
    } catch (err) {
      console.error("Error fetching events from database:", err)
      setError("Failed to load events. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  const fetchScrapedData = async () => {
    try {
      setLoading(true)
      setError(null)
      setSuccess(null)
      
      const response = await axios.get<ScrapeResponse>(`${api}/scrape/cashbackforex`)
      setEvents(response.data.data)
      
      const message = `Successfully retrieved ${response.data.data.length} events (${response.data.db_result.created} new, ${response.data.db_result.updated} updated)`
      setSuccess(message)
    } catch (err) {
      console.error("Error fetching scraped data:", err)
      setError("Failed to fetch scraped data. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  const handleImpactChange = (value: string) => {
    const newFilters = { ...filters }
    
    if (value === "all") {
      delete newFilters.impact
    } else {
      newFilters.impact = [value]
    }
    
    setFilters(newFilters)
    fetchEvents(newFilters)
  }

  const handleCountryChange = (value: string) => {
    const newFilters = { ...filters }
    
    if (value === "all") {
      delete newFilters.countries
    } else {
      newFilters.countries = [value]
    }
    
    setFilters(newFilters)
    fetchEvents(newFilters)
  }

  const handleSourceChange = (value: string) => {
    const newFilters = { ...filters }
    
    if (value === "all") {
      delete newFilters.sources
    } else {
      newFilters.sources = [value]
    }
    
    setFilters(newFilters)
    fetchEvents(newFilters)
  }

  const handleStartDateChange = (date?: Date) => {
    setStartDate(date)
    const newFilters = { ...filters }
    
    if (date) {
      // Format date using Luxon
      newFilters.start_date = DateTime.fromJSDate(date).toFormat("yyyy-MM-dd")
    } else {
      delete newFilters.start_date
    }
    
    setFilters(newFilters)
    fetchEvents(newFilters)
  }

  const handleEndDateChange = (date?: Date) => {
    setEndDate(date)
    const newFilters = { ...filters }
    
    if (date) {
      // Format date using Luxon
      newFilters.end_date = DateTime.fromJSDate(date).toFormat("yyyy-MM-dd")
    } else {
      delete newFilters.end_date
    }
    
    setFilters(newFilters)
    fetchEvents(newFilters)
  }

  const resetFilters = () => {
    setFilters({})
    setStartDate(undefined)
    setEndDate(undefined)
    fetchEvents({})
  }

  const getImpactColor = (impact: string) => {
    switch (impact.toLowerCase()) {
      case "high":
        return "bg-danger text-danger-foreground"
      case "medium":
        return "bg-warning text-warning-foreground"
      case "low":
        return "bg-muted text-muted-foreground"
      default:
        return "bg-muted text-muted-foreground"
    }
  }

  // Format date for display using Luxon
  const formatDate = (date: Date) => {
    return DateTime.fromJSDate(date).toFormat("MMMM d, yyyy")
  }

  return (
    <div>
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h1 className="font-heading text-3xl font-bold tracking-tight mb-1">Economic Events</h1>
          <p className="text-muted-foreground">
            View and update scraped forex economic event data
          </p>
        </div>
        
        <div className="flex gap-3">
          <Button 
            onClick={() => fetchEvents(filters)}
            variant="outline"
            disabled={loading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
          
          <Button 
            onClick={fetchScrapedData} 
            disabled={loading}
            className="bg-primary text-primary-foreground hover:bg-primary/90"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
            {loading ? "Scraping..." : "Scrape New Data"}
          </Button>
        </div>
      </div>

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

      {/* Filter panel */}
      <Card className="border-border/30 mb-6">
        <CardHeader className="bg-card px-6 py-4 border-b border-border/30 text-black">
          <div className="flex justify-between items-center">
            <CardTitle>Filter Events</CardTitle>
            <Button variant="ghost" size="sm" onClick={resetFilters} className="border-2 border-border/30 ">
              Reset Filters
            </Button>
          </div>
        </CardHeader>
        <CardContent className="p-6 grid grid-cols-1 md:grid-cols-5 gap-4">
          {/* Date Range Filter */}
          <div className="flex flex-col space-y-2">
            <label className="text-sm font-medium">Start Date</label>
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant={"outline"}
                  className={`w-full justify-start text-left font-normal ${
                    startDate ? "" : "text-muted-foreground"
                  }`}
                >
                  <Calendar className="mr-2 h-4 w-4" />
                  {startDate ? formatDate(startDate) : "Pick a date"}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0">
                <CalendarComponent
                  selected={startDate}
                  onSelect={handleStartDateChange}
                  initialFocus
                />
              </PopoverContent>
            </Popover>
          </div>
          
          <div className="flex flex-col space-y-2">
            <label className="text-sm font-medium">End Date</label>
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant={"outline"}
                  className={`w-full justify-start text-left font-normal ${
                    endDate ? "" : "text-muted-foreground"
                  }`}
                >
                  <Calendar className="mr-2 h-4 w-4" />
                  {endDate ? formatDate(endDate) : "Pick a date"}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0">
                <CalendarComponent
                  selected={endDate}
                  onSelect={handleEndDateChange}
                  initialFocus
                />
              </PopoverContent>
            </Popover>
          </div>
          
          {/* Country Filter */}
          <div className="flex flex-col space-y-2">
            <label className="text-sm font-medium">Country</label>
            <Select onValueChange={handleCountryChange} value={filters.countries?.[0] || "all"}>
              <SelectTrigger>
                <SelectValue placeholder="All Countries" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Countries</SelectItem>
                {availableCountries.map(country => (
                  <SelectItem key={country} value={country}>{country}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          {/* Impact Filter */}
          <div className="flex flex-col space-y-2">
            <label className="text-sm font-medium">Impact</label>
            <Select onValueChange={handleImpactChange} value={filters.impact?.[0] || "all"}>
              <SelectTrigger>
                <SelectValue placeholder="All Impacts" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Impacts</SelectItem>
                <SelectItem value="high">High</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="low">Low</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          {/* Source Filter */}
          <div className="flex flex-col space-y-2">
            <label className="text-sm font-medium">Source</label>
            <Select onValueChange={handleSourceChange} value={filters.sources?.[0] || "all"}>
              <SelectTrigger>
                <SelectValue placeholder="All Sources" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Sources</SelectItem>
                {availableSources.map(source => (
                  <SelectItem key={source} value={source}>{source}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 gap-6">
        {events.length === 0 && !loading ? (
          <Card className="border-border/30">
            <CardContent className="flex flex-col items-center justify-center py-12">
              <div className="rounded-full bg-muted p-3 mb-4">
                <Calendar className="h-6 w-6 text-muted-foreground" />
              </div>
              <h3 className="text-xl font-medium mb-1">No Events Found</h3>
              <p className="text-center text-muted-foreground max-w-md">
                There are no economic events available. Try adjusting your filters or click the "Scrape New Data" button 
                to fetch the latest events.
              </p>
            </CardContent>
          </Card>
        ) : (
          <Card className="border-border/30 shadow-card overflow-hidden">
            <CardHeader className="bg-card px-6 py-4 border-b border-border/30 text-black">
              <CardTitle>Forex Economic Events ({events.length})</CardTitle>
            </CardHeader>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border/30">
                    <th className="text-left text-xs font-medium text-muted-foreground uppercase tracking-wider px-6 py-3">Date/Time</th>
                    <th className="text-left text-xs font-medium text-muted-foreground uppercase tracking-wider px-6 py-3">Country</th>
                    <th className="text-left text-xs font-medium text-muted-foreground uppercase tracking-wider px-6 py-3">Event</th>
                    <th className="text-left text-xs font-medium text-muted-foreground uppercase tracking-wider px-6 py-3">Impact</th>
                    <th className="text-left text-xs font-medium text-muted-foreground uppercase tracking-wider px-6 py-3">Actual</th>
                    <th className="text-left text-xs font-medium text-muted-foreground uppercase tracking-wider px-6 py-3">Forecast</th>
                    <th className="text-left text-xs font-medium text-muted-foreground uppercase tracking-wider px-6 py-3">Previous</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/30">
                  {events.map((event, index) => (
                    <tr 
                      key={index} 
                      className="hover:bg-muted/30 transition-colors"
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center text-sm">
                          <Calendar className="h-4 w-4 mr-2 text-muted-foreground" />
                          <span className="font-medium">{event.date}</span>
                          <span className="mx-1.5 text-muted-foreground">•</span>
                          <Clock className="h-4 w-4 mr-2 text-muted-foreground" />
                          <span>{event.time}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <Flag className="h-4 w-4 mr-2 text-muted-foreground" />
                          <span className="text-sm">{event.country}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-start">
                          <Globe className="h-4 w-4 mr-2 mt-0.5 text-muted-foreground" />
                          <span className="text-sm">{event.event}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <Badge className={getImpactColor(event.impact)}>
                          {event.impact}
                        </Badge>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <TrendingUp className="h-4 w-4 mr-2 text-muted-foreground" />
                          <span className="text-sm font-medium">{event.actual || "-"}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {event.forecast || "-"}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {event.previous || "-"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        )}
      </div>
    </div>
  )
}