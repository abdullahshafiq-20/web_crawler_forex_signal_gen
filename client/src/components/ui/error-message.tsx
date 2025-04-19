import * as React from "react"
import { cn } from "@/lib/utils"
import { AlertTriangle } from "lucide-react"
import { Button } from "./button"

interface ErrorMessageProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string
  message?: string
  onRetry?: () => void
}

export function ErrorMessage({ 
  className, 
  title = "Something went wrong", 
  message = "We couldn't load the data you requested", 
  onRetry,
  ...props 
}: ErrorMessageProps) {
  return (
    <div 
      className={cn(
        "min-h-screen bg-background flex flex-col items-center justify-center p-4",
        className
      )} 
      {...props}
    >
      <div className="max-w-md w-full border border-primary/20 bg-primary/5 rounded-xl p-6 backdrop-blur-sm shadow-lg">
        <div className="flex gap-4 items-start">
          <div className="rounded-full bg-primary/10 p-2">
            <AlertTriangle className="h-6 w-6 text-primary" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-medium text-foreground mb-2">{title}</h3>
            <p className="text-muted-foreground mb-4">{message}</p>
            {onRetry && (
              <Button 
                onClick={onRetry}
                className="bg-primary text-primary-foreground hover:bg-primary/90"
              >
                Try again
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}