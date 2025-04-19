import * as React from "react"
import { DateTime } from "luxon"
import { Button } from "@/components/ui/button"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { cn } from "@/lib/utils"

export type CalendarProps = {
  selected?: Date | Date[] | undefined
  onSelect?: (date: Date | undefined) => void
  disabled?: (date: Date) => boolean
  initialFocus?: boolean
  className?: string
}

export function Calendar({
  // Removed unused mode property
  onSelect,
  disabled,
  className,
  selected,
}: CalendarProps) {
  // Current view state
  const [viewDate, setViewDate] = React.useState(() => 
    selected && !Array.isArray(selected) 
      ? DateTime.fromJSDate(selected)
      : DateTime.now()
  )

  // Generate calendar grid
  const calendarDays = React.useMemo(() => {
    const monthStart = viewDate.startOf("month")
    const monthEnd = viewDate.endOf("month")
    
    // Get the Monday of the week containing the 1st of the month
    let weekStart = monthStart.startOf("week")
    
    // Get the Sunday of the week containing the last day of the month
    const weekEnd = monthEnd.endOf("week")
    
    const days: DateTime[] = []
    let current = weekStart
    
    while (current <= weekEnd) {
      days.push(current)
      current = current.plus({ days: 1 })
    }
    
    return days
  }, [viewDate])

  // Check if a date is selected
  const isSelected = React.useCallback((day: DateTime) => {
    if (!selected) return false
    
    if (Array.isArray(selected)) {
      return selected.some(date => 
        day.hasSame(DateTime.fromJSDate(date), "day")
      )
    }
    
    return day.hasSame(DateTime.fromJSDate(selected), "day")
  }, [selected])

  // Check if date is today
  const isToday = React.useCallback((day: DateTime) => {
    return day.hasSame(DateTime.now(), "day")
  }, [])

  // Check if date is in current month
  const isCurrentMonth = React.useCallback((day: DateTime) => {
    return day.month === viewDate.month
  }, [viewDate])

  // Check if date is disabled
  const isDateDisabled = React.useCallback((day: DateTime) => {
    if (typeof disabled === "function") {
      return disabled(day.toJSDate())
    }
    return false
  }, [disabled])
  
  // Change month handlers
  const previousMonth = () => {
    setViewDate(prev => prev.minus({ months: 1 }))
  }
  
  const nextMonth = () => {
    setViewDate(prev => prev.plus({ months: 1 }))
  }
  
  // Handle date selection
  const handleSelectDate = (day: DateTime) => {
    if (isDateDisabled(day)) return
    
    const date = day.toJSDate()
    if (onSelect) onSelect(date)
  }

  return (
    <div className={cn("p-3", className)}>
      <div className="flex items-center justify-between mb-4">
        <Button
          type="button"
          variant="outline"
          size="icon"
          className="h-7 w-7 bg-transparent p-0"
          onClick={previousMonth}
        >
          <ChevronLeft className="h-4 w-4" />
          <span className="sr-only">Previous month</span>
        </Button>
        
        <h2 className="text-sm font-medium">
          {viewDate.toFormat("MMMM yyyy")}
        </h2>
        
        <Button
          type="button"
          variant="outline"
          size="icon"
          className="h-7 w-7 bg-transparent p-0"
          onClick={nextMonth}
        >
          <ChevronRight className="h-4 w-4" />
          <span className="sr-only">Next month</span>
        </Button>
      </div>
      
      <div className="grid grid-cols-7 mb-1">
        {["M", "T", "W", "T", "F", "S", "S"].map((day, i) => (
          <div 
            key={i} 
            className="text-center text-xs font-medium text-muted-foreground h-9 flex items-center justify-center"
          >
            {day}
          </div>
        ))}
      </div>
      
      <div className="grid grid-cols-7 gap-1">
        {calendarDays.map((day, i) => {
          const isDisabled = isDateDisabled(day)
          
          return (
            <Button
              key={i}
              type="button"
              variant="ghost"
              size="icon"
              className={cn(
                "h-9 w-9 p-0 font-normal text-sm",
                !isCurrentMonth(day) && "text-muted-foreground opacity-50",
                isToday(day) && "bg-accent text-accent-foreground",
                isSelected(day) && "bg-primary text-primary-foreground hover:bg-primary hover:text-primary-foreground focus:bg-primary focus:text-primary-foreground",
                isDisabled && "opacity-50 cursor-not-allowed"
              )}
              disabled={isDisabled}
              onClick={() => handleSelectDate(day)}
            >
              {day.day}
            </Button>
          )
        })}
      </div>
    </div>
  )
}