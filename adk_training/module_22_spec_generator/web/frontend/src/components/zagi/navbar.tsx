import * as React from "react";
import { Link, NavLink, useLocation, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Github, Sparkles } from "lucide-react";
import { ZagiLogo } from "./logo";
import { Button } from "@/components/ui/button";

export function Navbar() {
  const [scrolled, setScrolled] = React.useState(false);
  const loc = useLocation();
  const navigate = useNavigate();

  React.useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // Scroll do hash po nawigacji na "/"
  React.useEffect(() => {
    if (loc.pathname === "/" && loc.hash) {
      const id = loc.hash.replace("#", "");
      // odczekaj na render
      setTimeout(() => {
        document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
      }, 80);
    }
  }, [loc]);

  const goSection = (id: string) => (e: React.MouseEvent) => {
    e.preventDefault();
    if (loc.pathname !== "/") {
      navigate(`/#${id}`);
    } else {
      document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className={`fixed inset-x-0 top-0 z-50 transition-all duration-300 ${
        scrolled
          ? "border-b border-white/5 bg-zagi-bg/80 backdrop-blur-xl"
          : "bg-transparent"
      }`}
    >
      <div className="container flex h-16 items-center justify-between">
        <Link to="/" className="group">
          <ZagiLogo size={32} withWordmark />
        </Link>

        <nav className="hidden items-center gap-1 md:flex">
          <NavItem to="/" exact>
            Start
          </NavItem>
          <NavItem to="/studio">Studio</NavItem>
          <a
            href="/#how"
            className="rounded-full px-4 py-1.5 text-sm font-medium text-zagi-muted transition hover:text-white"
            onClick={goSection("how")}
          >
            Jak to dziala
          </a>
          <a
            href="/#author"
            className="rounded-full px-4 py-1.5 text-sm font-medium text-zagi-muted transition hover:text-white"
            onClick={goSection("author")}
          >
            Autor
          </a>
        </nav>

        <div className="flex items-center gap-2">
          <a
            href="https://github.com/"
            target="_blank"
            rel="noreferrer"
            className="hidden h-9 w-9 items-center justify-center rounded-full border border-white/5 text-zagi-muted transition hover:border-white/20 hover:text-white sm:inline-flex"
            aria-label="GitHub"
          >
            <Github className="h-4 w-4" />
          </a>
          <Link to="/studio">
            <Button
              size="sm"
              className="group bg-gradient-to-r from-zagi-crimson2 to-zagi-crimson font-semibold text-white shadow-glow-sm hover:shadow-glow"
            >
              <Sparkles className="h-4 w-4 transition group-hover:rotate-12" />
              Otworz Studio
            </Button>
          </Link>
        </div>
      </div>
    </motion.header>
  );
}

function NavItem({
  to,
  exact,
  children,
}: {
  to: string;
  exact?: boolean;
  children: React.ReactNode;
}) {
  return (
    <NavLink
      to={to}
      end={exact}
      className={({ isActive }) =>
        `rounded-full px-4 py-1.5 text-sm font-medium transition ${
          isActive
            ? "bg-white/5 text-white"
            : "text-zagi-muted hover:text-white"
        }`
      }
    >
      {children}
    </NavLink>
  );
}
