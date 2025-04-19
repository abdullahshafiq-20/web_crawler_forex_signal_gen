import * as React from "react"
import { cn } from "@/lib/utils"
import { Button } from "./button"
import { LineChart, RefreshCcw, Database, Calendar, CheckCircle, XCircle } from "lucide-react"
import { NavLink } from "react-router-dom"
import axios from "axios"
import { useState, useEffect } from "react"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "./tooltip"

interface HeaderProps extends React.HTMLAttributes<HTMLElement> {
  brandName?: string
}

export function Header({
  className,
  brandName = "Forex Signal Dashboard",
  ...props
}: HeaderProps) {
  const [serverStatus, setServerStatus] = useState<"online" | "offline" | "checking">("checking")
  const [lastChecked, setLastChecked] = useState<Date>(new Date())

  // Check server health on component mount and periodically
  useEffect(() => {
    checkServerHealth()
    
    // Check every 30 seconds
    const intervalId = setInterval(checkServerHealth, 30000)
    
    // Clean up on unmount
    return () => clearInterval(intervalId)
  }, [])
  
  // Function to check server health
  const checkServerHealth = async () => {
    try {
      setServerStatus("checking")
      // Try to fetch the root endpoint - update to your actual backend URL
      const response = await axios.get("http://127.0.0.1:8000/", { timeout: 5000 })
      
      if (response.status === 200) {
        setServerStatus("online")
      } else {
        setServerStatus("offline")
      }
    } catch (error) {
      console.error("Server health check failed:", error)
      setServerStatus("offline")
    }
    
    // Update the last checked timestamp
    setLastChecked(new Date())
  }
  
  // Get status indicator properties
  const getStatusIndicator = () => {
    switch (serverStatus) {
      case "online":
        return {
          icon: <CheckCircle className="h-4 w-4" />,
          color: "text-white",
          text: "Server Online",
          bgColor: "bg-green-500/30",
          borderColor: "border-white/40"
        }
      case "offline":
        return {
          icon: <XCircle className="h-4 w-4" />,
          color: "text-white",
          text: "Server Offline",
          bgColor: "bg-red-500/30",
          borderColor: "border-white/40"
        }
      case "checking":
        return {
          icon: <div className="h-4 w-4 rounded-full border-2 border-t-transparent border-white animate-spin"></div>,
          color: "text-white",
          text: "Checking...",
          bgColor: "bg-blue-500/30",
          borderColor: "border-white/40"
        }
    }
  }
  
  const indicator = getStatusIndicator()
  
  return (
    <div className="w-full py-2 sm:py-3 px-2 sm:px-4">
      <header
        className={cn(
          "max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 rounded-xl sm:rounded-2xl bg-primary shadow-lg",
          className
        )}
        {...props}
      >
        <div className="flex h-14 sm:h-16 items-center justify-between">
          {/* Logo and brand name */}
          <div className="flex items-center gap-1.5 sm:gap-2">
            <LineChart className="h-6 w-6 sm:h-7 sm:w-7 text-white" />
            <span className="font-heading text-lg sm:text-xl font-bold text-white truncate max-w-[150px] sm:max-w-none">
              {brandName}
            </span>
          </div>

          {/* Navigation links - desktop */}
          <nav className="hidden md:flex items-center space-x-1">
            <NavLink
              to="/dashboard"
              className={({ isActive }) =>
                cn(
                  "px-4 py-2 rounded-lg text-sm font-medium transition-colors",
                  isActive
                    ? "bg-white text-primary"
                    : "text-white/80 hover:bg-white/10 hover:text-white"
                )
              }
            >
              <div className="flex items-center gap-2">
                <LineChart className="h-4 w-4" />
                <span>Dashboard</span>
              </div>
            </NavLink>
            
            <NavLink
              to="/scraped-data"
              className={({ isActive }) =>
                cn(
                  "px-4 py-2 rounded-lg text-sm font-medium transition-colors",
                  isActive
                    ? "bg-white text-primary"
                    : "text-white/80 hover:bg-white/10 hover:text-white"
                )
              }
            >
              <div className="flex items-center gap-2">
                <Database className="h-4 w-4" />
                <span>Scraped Data</span>
              </div>
            </NavLink>

            <NavLink
              to="/weekly-signals"
              className={({ isActive }) =>
                cn(
                  "px-4 py-2 rounded-lg text-sm font-medium transition-colors",
                  isActive
                    ? "bg-white text-primary"
                    : "text-white/80 hover:bg-white/10 hover:text-white"
                )
              }
            >
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                <span>Weekly Signals</span>
              </div>
            </NavLink>
          </nav>

          {/* Action buttons */}
          <div className="flex items-center gap-2 sm:gap-3">
            {/* Server Status Indicator - desktop */}
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <div 
                    className={cn(
                      "hidden md:flex items-center gap-2 py-1 px-2.5 rounded-full border cursor-pointer",
                      indicator.bgColor,
                      indicator.borderColor
                    )}
                    onClick={checkServerHealth}
                  >
                    <span className={cn("flex items-center", indicator.color)}>
                      {indicator.icon}
                    </span>
                    <span className={cn("text-xs font-medium", indicator.color)}>
                      {indicator.text}
                    </span>
                  </div>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Last checked: {lastChecked.toLocaleTimeString()}</p>
                  <p>Click to check again</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
            
            {/* Server Status Indicator - mobile */}
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <div 
                    className={cn(
                      "md:hidden flex items-center justify-center h-7 w-7 sm:h-8 sm:w-8 rounded-full border cursor-pointer",
                      indicator.bgColor,
                      indicator.borderColor
                    )}
                    onClick={checkServerHealth}
                  >
                    <span className={cn("flex items-center", indicator.color)}>
                      {indicator.icon}
                    </span>
                  </div>
                </TooltipTrigger>
                <TooltipContent>
                  <p>{indicator.text}</p>
                  <p>Last checked: {lastChecked.toLocaleTimeString()}</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
            
            <Button size="sm" className="hidden md:flex gap-1.5 text-primary bg-white hover:bg-white/90"
              onClick={() => window.location.reload()}
            >
              <RefreshCcw className="h-4 w-4" />
              Refresh
            </Button>
            
            {/* Mobile refresh button - icon only */}
            <Button size="icon" className="md:hidden h-7 w-7 sm:h-8 sm:w-8 text-primary bg-white hover:bg-white/90 p-1.5"
              onClick={() => window.location.reload()}
            >
              <RefreshCcw className="h-full w-full" />
            </Button>
          </div>
        </div>
        
        {/* Mobile navigation tabs */}
        <div className="md:hidden pt-2 pb-1 flex border-t border-white/10 mt-1 justify-around px-1 sm:px-4">
          <NavLink
            to="/dashboard"
            className={({ isActive }) =>
              cn(
                "flex flex-col flex-1 items-center justify-center py-2 px-1 rounded-md text-xs font-medium transition-colors",
                isActive
                  ? "bg-white/10 text-white"
                  : "text-white/70 hover:text-white hover:bg-white/5"
              )
            }
          >
            <LineChart className="h-5 w-5 mb-1" />
            <span>Dashboard</span>
          </NavLink>
          
          <NavLink
            to="/scraped-data"
            className={({ isActive }) =>
              cn(
                "flex flex-col flex-1 items-center justify-center py-2 px-1 rounded-md text-xs font-medium transition-colors mx-1",
                isActive
                  ? "bg-white/10 text-white"
                  : "text-white/70 hover:text-white hover:bg-white/5"
              )
            }
          >
            <Database className="h-5 w-5 mb-1" />
            <span>Data</span>
          </NavLink>
          
          <NavLink
            to="/weekly-signals"
            className={({ isActive }) =>
              cn(
                "flex flex-col flex-1 items-center justify-center py-2 px-1 rounded-md text-xs font-medium transition-colors",
                isActive
                  ? "bg-white/10 text-white"
                  : "text-white/70 hover:text-white hover:bg-white/5"
              )
            }
          >
            <Calendar className="h-5 w-5 mb-1" />
            <span>Signals</span>
          </NavLink>
        </div>
      </header>
    </div>
  )
}