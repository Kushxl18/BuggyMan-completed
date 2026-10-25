import React from 'react';
import { AlertOctagon, RotateCcw, Home } from 'lucide-react';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('BuggyMan ErrorBoundary caught an exception:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    if (typeof window !== 'undefined') {
      window.location.reload();
    }
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="h-screen w-full flex items-center justify-center bg-slate-950 px-6 text-slate-100 font-sans">
          <div className="max-w-md w-full rounded-2xl border border-slate-800 bg-slate-900/90 p-8 text-center space-y-5 shadow-2xl">
            <div className="w-14 h-14 rounded-full bg-rose-500/10 border border-rose-500/20 flex items-center justify-center mx-auto text-rose-400">
              <AlertOctagon className="w-7 h-7" />
            </div>

            <div className="space-y-2">
              <h2 className="text-xl font-heading font-extrabold text-slate-100">Execution Exception</h2>
              <p className="text-xs text-slate-400 leading-relaxed">
                An unexpected component rendering error occurred. The application state has been isolated to prevent corruption.
              </p>
            </div>

            {this.state.error?.message && (
              <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl font-mono text-[11px] text-rose-400 text-left overflow-x-auto max-h-24">
                {this.state.error.message}
              </div>
            )}

            <div className="flex items-center justify-center gap-3 pt-2">
              <button
                onClick={this.handleReset}
                className="button-primary text-xs px-4 py-2.5 flex items-center gap-2"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Reload Workspace</span>
              </button>
              <a
                href="/dashboard"
                className="button-secondary text-xs px-4 py-2.5 flex items-center gap-2"
              >
                <Home className="w-3.5 h-3.5" />
                <span>Home</span>
              </a>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
