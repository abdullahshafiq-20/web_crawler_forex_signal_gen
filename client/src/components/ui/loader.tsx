import * as React from "react"
import { LineChart } from "lucide-react"
import { cn } from "@/lib/utils"

interface LoaderProps extends React.HTMLAttributes<HTMLDivElement> {
  text?: string
}

export function Loader({ className, text = "Loading data...", ...props }: LoaderProps) {
  return (
    <div 
      className={cn(
        "min-h-screen bg-background flex flex-col items-center justify-center",
        className
      )} 
      {...props}
    >
      <div className="flex flex-col items-center bg-primary/5 border border-primary/20 rounded-xl p-10 backdrop-blur-sm shadow-lg">
        <div className="relative flex flex-col items-center">
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="h-16 w-16 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
          </div>
          <LineChart className="h-8 w-8 text-primary" />
        </div>
        <h3 className="mt-8 font-heading text-xl font-bold text-primary">{text}</h3>
        <p className="mt-2 text-muted-foreground">Please wait while we fetch the latest market data</p>
      </div>
    </div>
  )
}