import * as React from "react";

interface State {
  error: Error | null;
  info: string | null;
}

export class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  State
> {
  state: State = { error: null, info: null };

  static getDerivedStateFromError(error: Error): State {
    return { error, info: null };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    // eslint-disable-next-line no-console
    console.error("[Concierge ErrorBoundary]", error, info);
    this.setState({ error, info: info.componentStack ?? null });
  }

  reset = () => this.setState({ error: null, info: null });

  render() {
    if (!this.state.error) return this.props.children;
    return (
      <div className="min-h-screen bg-cnc-bg p-8 text-cnc-ink">
        <div className="container max-w-3xl">
          <div className="rounded-2xl border border-cnc-rose/40 bg-cnc-rose/5 p-6 shadow-glow-sm">
            <div className="mb-2 text-xs font-bold uppercase tracking-widest text-cnc-rose">
              UI Error · Concierge crashed
            </div>
            <h1 className="mb-3 text-2xl font-extrabold text-white">
              {this.state.error.name}: {this.state.error.message}
            </h1>
            <pre className="max-h-72 overflow-auto rounded-lg bg-cnc-bg/80 p-3 text-[11px] text-cnc-muted">
              {this.state.error.stack}
              {this.state.info && `\n\nComponent stack:${this.state.info}`}
            </pre>
            <div className="mt-4 flex gap-2">
              <button
                onClick={() => location.reload()}
                className="rounded-lg bg-cnc-electric px-4 py-2 text-sm font-bold text-white hover:brightness-110"
              >
                Reload
              </button>
              <button
                onClick={this.reset}
                className="rounded-lg border border-cnc-border bg-cnc-surface/40 px-4 py-2 text-sm font-bold text-cnc-ink hover:border-cnc-electric/60"
              >
                Try again
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }
}
