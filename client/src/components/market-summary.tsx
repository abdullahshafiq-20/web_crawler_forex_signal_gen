import { Card, CardHeader, CardContent } from "@/components/ui/card"
import { Globe, TrendingUp, ExternalLink } from "lucide-react"
import {
  ChartContainer,
  ChartTooltipContent,
} from "./ui/chart"
import {
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  AreaChart,
} from "recharts"

type MarketSummaryProps = {
  summary: string
}

// Dummy data for demonstration
const marketData = [
  { date: "Apr 13", value: 112 },
  { date: "Apr 14", value: 125 },
  { date: "Apr 15", value: 118 },
  { date: "Apr 16", value: 130 },
  { date: "Apr 17", value: 126 },
  { date: "Apr 18", value: 140 },
  { date: "Apr 19", value: 152 },
]

export function MarketSummary({ summary }: MarketSummaryProps) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
      <Card className="col-span-1 lg:col-span-2 border shadow-card bg-card">
        <CardHeader className="border-b pb-3 text-black p-3 sm:p-4">
          <div className="flex items-center space-x-2">
            <Globe className="h-4 w-4 sm:h-5 sm:w-5 text-primary" />
            <h2 className="text-base sm:text-lg font-heading font-bold">Market Summary</h2>
          </div>
        </CardHeader>
        <CardContent className="p-3 sm:p-5">
          <p className="text-sm sm:text-base text-muted-foreground">{summary}</p>
          
          <div className="flex items-center justify-end mt-3 sm:mt-4 text-xs sm:text-sm">
            <a href="#" className="text-primary hover:underline flex items-center">
              Full market report <ExternalLink className="h-3 w-3 sm:h-3.5 sm:w-3.5 ml-1" />
            </a>
          </div>
        </CardContent>
      </Card>

      <Card className="col-span-1 border shadow-card">
        <CardHeader className="border-b pb-3 text-black p-3 sm:p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <TrendingUp className="h-4 w-4 sm:h-5 sm:w-5 text-primary" />
              <h2 className="text-base sm:text-lg font-heading font-bold">Market Index</h2>
            </div>
            <div className="flex items-center text-xs sm:text-sm">
              <span className="text-success font-medium">+3.2%</span>
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-2 sm:p-4 pb-1 sm:pb-2">
          <ChartContainer
            className="h-[160px] sm:h-[180px] w-full"
            config={{
              main: {
                theme: {
                  light: "hsl(221.2 83.2% 53.3%)",
                  dark: "hsl(217.2 91.2% 59.8%)",
                },
              },
              grid: {
                theme: {
                  light: "hsl(214.3 31.8% 91.4%)",
                  dark: "hsl(217.2 32.6% 17.5%)",
                },
              },
            }}
          >
            <AreaChart 
              data={marketData}
              margin={{
                top: 5,
                right: 5,
                left: -20,
                bottom: 0,
              }}
            >
              <defs>
                <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                  <stop
                    offset="5%"
                    stopColor="var(--color-main)"
                    stopOpacity={0.3}
                  />
                  <stop
                    offset="95%"
                    stopColor="var(--color-main)"
                    stopOpacity={0}
                  />
                </linearGradient>
              </defs>
              <CartesianGrid 
                strokeDasharray="3 3" 
                vertical={false} 
                stroke="var(--color-grid)" 
              />
              <XAxis
                dataKey="date"
                tickLine={false}
                axisLine={false}
                tick={{ fontSize: 10 }}
                tickMargin={8}
                interval="preserveStartEnd"
              />
              <YAxis
                tickLine={false}
                axisLine={false}
                tick={{ fontSize: 10 }}
                tickMargin={8}
                domain={["auto", "auto"]}
              />
              <Tooltip content={<ChartTooltipContent />} />
              <Area
                type="monotone"
                dataKey="value"
                stroke="var(--color-main)"
                fillOpacity={1}
                fill="url(#colorValue)"
              />
            </AreaChart>
          </ChartContainer>
        </CardContent>
      </Card>
    </div>
  )
}
