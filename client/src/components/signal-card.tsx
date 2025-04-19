import React from "react"
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import { Info } from "lucide-react"

interface SignalProps {
  signal: {
    pair: string
    direction: "BUY" | "SELL" | "NEUTRAL"
    strength: string
    confidence: string
    rationale: string
    impact?: string
  }
  directionIcon: React.ReactNode
  directionColor: string
  strengthClass: string
}

export function SignalCard({
  signal,
  directionIcon,
  directionColor,
  strengthClass,
}: SignalProps) {
  return (
    <Card className="overflow-hidden border shadow-card transition-all hover:shadow-lg h-full">
      <CardHeader className="bg-card p-3 sm:p-4 pb-2 border-b border-border/30 text-black">
        <div className="flex flex-wrap items-center justify-between gap-y-2">
          <div className="flex items-center gap-2">
            <span className="font-heading font-bold text-base sm:text-lg">{signal.pair}</span>
            <Badge variant="outline" className={strengthClass}>
              {signal.strength.toLowerCase()}
            </Badge>
          </div>
          <div className="flex items-center">
            {directionIcon}
            <span className={`ml-1 font-medium ${directionColor}`}>{signal.direction}</span>
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-3 sm:p-4 pt-2 sm:pt-3">
        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <span className="text-xs sm:text-sm font-medium text-muted-foreground">Confidence</span>
            <div className="flex items-center gap-1">
              <div className="w-16 sm:w-24 h-2 bg-muted rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary rounded-full"
                  style={{
                    width: `${parseInt(signal.confidence) || 0}%`,
                  }}
                />
              </div>
              <span className="text-xs font-medium">{signal.confidence}%</span>
            </div>
          </div>
          
          {signal.impact && (
            <div className="flex items-center justify-between">
              <span className="text-xs sm:text-sm font-medium text-muted-foreground">Impact</span>
              <Badge 
                variant="outline" 
                className={
                  signal.impact === "HIGH"
                    ? "bg-danger/10 text-danger border-danger/20"
                    : signal.impact === "MEDIUM"
                    ? "bg-warning/10 text-warning border-warning/20"
                    : "bg-muted text-muted-foreground"
                }
              >
                {signal.impact.toLowerCase()}
              </Badge>
            </div>
          )}
        </div>

        <div className="mt-3 sm:mt-4">
          <div className="flex items-center gap-1 mb-1">
            <span className="text-xs sm:text-sm font-medium text-foreground">Rationale</span>
            <Tooltip>
              <TooltipTrigger asChild>
                <Info className="h-3 w-3 sm:h-3.5 sm:w-3.5 text-muted-foreground cursor-help" />
              </TooltipTrigger>
              <TooltipContent>
                Analysis rationale
              </TooltipContent>
            </Tooltip>
          </div>
          <p className="text-xs sm:text-sm text-muted-foreground line-clamp-3">{signal.rationale}</p>
        </div>
      </CardContent>
      <CardFooter className="flex items-center justify-between p-3 sm:p-4 pt-2 border-t border-border/30 bg-muted/30">
        <button className="text-2xs sm:text-xs font-medium text-primary hover:underline">
          See full analysis
        </button>
        <button className="text-2xs sm:text-xs font-medium text-muted-foreground hover:text-primary">
          Add to watchlist
        </button>
      </CardFooter>
    </Card>
  )
}
