import { Outlet, NavLink } from "react-router-dom"
import { Header } from "@/components/ui/header"
import { LineChart, Database, Calendar } from "lucide-react"
import { cn } from "@/lib/utils"

export function AppLayout() {
  const navItems = [
    {
      name: "Dashboard",
      href: "/dashboard",
      icon: <LineChart className="h-5 w-5" />,
    },
    {
      name: "Scraped Data",
      href: "/scraped-data",
      icon: <Database className="h-5 w-5" />,
    },
    {
      name: "Weekly Signals",
      href: "/weekly-signals",
      icon: <Calendar className="h-5 w-5" />,
    },
  ]

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header />

      <div className="flex-1 flex">
        {/* Sidebar */}
        <aside className="hidden md:flex w-64 flex-col border-r border-border/30 overflow-y-auto">
          <nav className="flex-1 px-4 py-6 space-y-1 sticky top-0">
            {navItems.map((item) => (
              <NavLink
                key={item.name}
                to={item.href}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-3 px-4 py-3 text-sm rounded-md transition-colors",
                    isActive
                      ? "bg-primary/10 text-primary font-medium"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  )
                }
              >
                {item.icon}
                <span>{item.name}</span>
              </NavLink>
            ))}
          </nav>
        </aside>

        {/* Mobile navigation */}
        <div className="fixed bottom-0 left-0 right-0 border-t border-border/30 bg-background p-2 md:hidden z-10 shadow-header">
          <div className="flex justify-around">
            {navItems.map((item) => (
              <NavLink
                key={item.name}
                to={item.href}
                className={({ isActive }) =>
                  cn(
                    "flex flex-col items-center gap-1 px-4 py-2 text-xs rounded-md transition-colors",
                    isActive
                      ? "text-primary font-medium"
                      : "text-muted-foreground hover:text-foreground"
                  )
                }
              >
                {item.icon}
                <span>{item.name}</span>
              </NavLink>
            ))}
          </div>
        </div>

        {/* Main content */}
        <main className="flex-1 overflow-auto">
          <div className="container mx-auto py-6 px-4 pb-20 md:pb-6">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}