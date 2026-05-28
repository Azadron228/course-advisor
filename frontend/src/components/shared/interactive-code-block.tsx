'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { useTranslations } from 'next-intl';
import { Play, RotateCcw, Copy, Check, Terminal, Eye, Code2, AlertTriangle, Info, X } from 'lucide-react';

declare global {
  interface Window {
    loadPyodide?: any;
    pyodidePromise?: Promise<any>;
  }
}

interface InteractiveCodeBlockProps {
  language: string;
  code: string;
}

interface LogEntry {
  type: 'stdout' | 'stderr' | 'system' | 'error' | 'warn' | 'info';
  text: string;
}

export function InteractiveCodeBlock({ language, code }: InteractiveCodeBlockProps) {
  const t = useTranslations('Plan');
  const [copied, setCopied] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [pyodideStatus, setPyodideStatus] = useState<string>('');
  const [consoleLogs, setConsoleLogs] = useState<LogEntry[]>([]);
  const [activeTab, setActiveTab] = useState<'code' | 'preview'>('code');
  const [previewKey, setPreviewKey] = useState(0);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  const lang = language.toLowerCase();
  const isPython = lang === 'python' || lang === 'py';
  const isJavaScript = lang === 'javascript' || lang === 'js' || lang === 'typescript' || lang === 'ts';
  const isHtml = lang === 'html' || lang === 'xml' || lang === 'svg';
  const isExecutable = isPython || isJavaScript || isHtml;

  const handleCopy = async () => {
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(code);
      } else {
        // Fallback for non-secure contexts (HTTP) or unsupported browsers
        const textArea = document.createElement('textarea');
        textArea.value = code;
        textArea.style.top = '0';
        textArea.style.left = '0';
        textArea.style.position = 'fixed';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
      }
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy code:', err);
    }
  };

  const loadPyodideRuntime = async (): Promise<any> => {
    if (window.pyodidePromise) {
      return window.pyodidePromise;
    }

    setPyodideStatus(t('downloadingPython'));
    window.pyodidePromise = (async () => {
      if (!window.loadPyodide) {
        await new Promise<void>((resolve, reject) => {
          const script = document.createElement('script');
          script.src = 'https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.js';
          script.onload = () => resolve();
          script.onerror = () => reject(new Error('Failed to load Pyodide runtime script'));
          document.head.appendChild(script);
        });
      }
      setPyodideStatus(t('initializingInterpreter'));
      const pyodide = await window.loadPyodide({
        indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.25.0/full/',
      });
      setPyodideStatus('');
      return pyodide;
    })();

    return window.pyodidePromise;
  };

  const runPython = async () => {
    setIsRunning(true);
    setConsoleLogs([{ type: 'system', text: t('initializingEnv') }]);
    
    try {
      const pyodide = await loadPyodideRuntime();
      setConsoleLogs([]); // Clear loading logs

      const outputLogs: LogEntry[] = [];
      pyodide.setStdout({
        batched: (msg: string) => {
          outputLogs.push({ type: 'stdout', text: msg });
          setConsoleLogs([...outputLogs]);
        },
      });
      pyodide.setStderr({
        batched: (msg: string) => {
          outputLogs.push({ type: 'stderr', text: msg });
          setConsoleLogs([...outputLogs]);
        },
      });

      // Run Python Code
      const result = await pyodide.runPythonAsync(code);
      
      if (result !== undefined && result !== null && String(result) !== 'None') {
        outputLogs.push({ type: 'stdout', text: `\n→ ${String(result)}` });
      }

      if (outputLogs.length === 0) {
        outputLogs.push({ type: 'system', text: t('execSuccessNoOutput') });
      }

      setConsoleLogs(outputLogs);
    } catch (err: any) {
      setConsoleLogs(prev => [
        ...prev.filter(l => l.type !== 'system'),
        { type: 'error', text: err.message || String(err) }
      ]);
    } finally {
      setIsRunning(false);
      setPyodideStatus('');
    }
  };

  const runJavaScript = () => {
    setIsRunning(true);
    setConsoleLogs([]);
    const logs: LogEntry[] = [];

    const customConsole = {
      log: (...args: any[]) => {
        logs.push({
          type: 'stdout',
          text: args.map(arg => typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)).join(' ')
        });
      },
      error: (...args: any[]) => {
        logs.push({
          type: 'error',
          text: args.map(arg => String(arg)).join(' ')
        });
      },
      warn: (...args: any[]) => {
        logs.push({
          type: 'warn',
          text: args.map(arg => String(arg)).join(' ')
        });
      },
      info: (...args: any[]) => {
        logs.push({
          type: 'info',
          text: args.map(arg => String(arg)).join(' ')
        });
      }
    };

    try {
      // Execute the script by passing custom console in a wrapper function
      const runner = new Function('console', code);
      const result = runner(customConsole);
      
      if (result !== undefined && result !== null) {
        logs.push({
          type: 'stdout',
          text: `\n→ ${typeof result === 'object' ? JSON.stringify(result, null, 2) : String(result)}`
        });
      }
      
      if (logs.length === 0) {
        logs.push({ type: 'system', text: t('execSuccessNoOutput') });
      }
      setConsoleLogs(logs);
    } catch (err: any) {
      logs.push({
        type: 'error',
        text: `Runtime Error: ${err.message || String(err)}`
      });
      setConsoleLogs(logs);
    } finally {
      setIsRunning(false);
    }
  };

  const handleRun = () => {
    if (isPython) {
      runPython();
    } else if (isJavaScript) {
      runJavaScript();
    } else if (isHtml) {
      setActiveTab('preview');
      setPreviewKey(prev => prev + 1);
    }
  };

  const clearConsole = () => {
    setConsoleLogs([]);
  };

  // Compile full HTML with basic container styles if needed
  const getIframeSrcDoc = () => {
    if (code.includes('<html') || code.includes('<body')) {
      return code;
    }
    return `
      <!DOCTYPE html>
      <html>
        <head>
          <meta charset="utf-8">
          <style>
            body {
              font-family: system-ui, -apple-system, sans-serif;
              margin: 1.5rem;
              color: #f8fafc;
              background-color: #0f172a;
            }
          </style>
        </head>
        <body>
          ${code}
        </body>
      </html>
    `;
  };

  return (
    <div className="my-6 border border-[#2d3139] bg-[#1e222b] rounded-2xl overflow-hidden shadow-2xl transition-all duration-300 hover:shadow-primary/5">
      {/* Header Toolbar */}
      <div className="flex items-center justify-between px-5 py-3 border-b border-[#2d3139] bg-[#181a1f] select-none">
        <div className="flex items-center gap-3">
          {/* Status/Language badge */}
          <span className="px-2.5 py-1 bg-primary/10 text-primary text-[10px] font-black uppercase tracking-wider rounded-md">
            {language}
          </span>
          
          {/* HTML Preview tabs */}
          {isHtml && (
            <div className="flex items-center gap-1.5 p-1 bg-surface/50 border border-border/60 rounded-lg">
              <button
                type="button"
                onClick={() => setActiveTab('code')}
                className={`flex items-center gap-1 px-2.5 py-1 text-[11px] font-bold rounded-md transition-all ${
                  activeTab === 'code'
                    ? 'bg-primary text-primary-foreground shadow-md'
                    : 'text-muted hover:text-foreground'
                }`}
              >
                <Code2 className="w-3 h-3" />
                {t('code')}
              </button>
              <button
                type="button"
                onClick={() => {
                  setActiveTab('preview');
                  setPreviewKey(prev => prev + 1);
                }}
                className={`flex items-center gap-1 px-2.5 py-1 text-[11px] font-bold rounded-md transition-all ${
                  activeTab === 'preview'
                    ? 'bg-primary text-primary-foreground shadow-md'
                    : 'text-muted hover:text-foreground'
                }`}
              >
                <Eye className="w-3 h-3" />
                {t('preview')}
              </button>
            </div>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* Run button */}
          {isExecutable && (
            <button
              type="button"
              disabled={isRunning}
              onClick={handleRun}
              className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-lg shadow-sm border transition-all select-none ${
                isRunning
                  ? 'bg-muted border-border text-muted cursor-wait'
                  : 'bg-emerald-500/10 hover:bg-emerald-500/25 border-emerald-500/20 text-emerald-400 hover:text-emerald-300 active:scale-95'
              }`}
            >
              <Play className={`w-3.5 h-3.5 fill-current ${isRunning ? 'animate-pulse' : ''}`} />
              {isRunning ? t('running') : isHtml ? t('preview') : t('run')}
            </button>
          )}

          {/* Copy button */}
          <button
            type="button"
            onClick={handleCopy}
            className="p-1.5 text-muted hover:text-foreground border border-border/40 hover:border-border rounded-lg bg-surface/50 transition-all active:scale-95"
            title={t('copyCode')}
          >
            {copied ? (
              <Check className="w-3.5 h-3.5 text-emerald-400" />
            ) : (
              <Copy className="w-3.5 h-3.5" />
            )}
          </button>
        </div>
      </div>

      {/* Code Display Area */}
      <div className="relative">
        <div className={activeTab === 'code' ? 'block' : 'hidden'}>
          <SyntaxHighlighter
            language={lang}
            style={oneDark}
            customStyle={{
              margin: 0,
              padding: '1.25rem',
              background: 'transparent',
              fontSize: '0.88rem',
              lineHeight: '1.6',
            }}
            PreTag="div"
          >
            {code}
          </SyntaxHighlighter>
        </div>

        {/* HTML Iframe Live Preview */}
        {isHtml && activeTab === 'preview' && (
          <div className="p-4 bg-[#16181d] min-h-[220px]">
            <iframe
              key={previewKey}
              ref={iframeRef}
              srcDoc={getIframeSrcDoc()}
              sandbox="allow-scripts"
              className="w-full min-h-[220px] rounded-xl border border-border/80 bg-white"
              title="HTML Sandbox Preview"
            />
          </div>
        )}
      </div>

      {/* Terminal / Output Console */}
      {isExecutable && !isHtml && (consoleLogs.length > 0 || pyodideStatus || isRunning) && (
        <div className="border-t border-[#2d3139] bg-[#16181d] overflow-hidden transition-all duration-300">
          {/* Console Header */}
          <div className="flex items-center justify-between px-5 py-2 border-b border-[#282c34] bg-[#121417] select-none text-[10px] font-bold text-muted uppercase tracking-wider">
            <span className="flex items-center gap-1.5">
              <Terminal className="w-3 h-3 text-emerald-400" />
              {t('terminalOutput')}
            </span>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={clearConsole}
                className="hover:text-foreground transition-colors p-0.5"
                title="Clear Output"
              >
                <RotateCcw className="w-3 h-3" />
              </button>
              <button
                type="button"
                onClick={clearConsole}
                className="hover:text-foreground transition-colors p-0.5"
                title="Close Terminal"
              >
                <X className="w-3 h-3" />
              </button>
            </div>
          </div>

          {/* Console Output Logs */}
          <div className="p-5 font-mono text-[12px] leading-relaxed max-h-[280px] overflow-y-auto space-y-2.5 selection:bg-primary/25 scrollbar-thin">
            {pyodideStatus && (
              <div className="flex items-center gap-2 text-primary font-semibold italic animate-pulse">
                <span className="w-1.5 h-1.5 rounded-full bg-primary animate-ping" />
                {pyodideStatus}
              </div>
            )}
            
            {consoleLogs.map((log, index) => {
              if (log.type === 'error') {
                return (
                  <div key={index} className="flex gap-2 text-rose-400 bg-rose-500/5 p-2 border border-rose-500/10 rounded-lg whitespace-pre-wrap">
                    <AlertTriangle className="w-4 h-4 shrink-0 text-rose-400 mt-0.5" />
                    <span>{log.text}</span>
                  </div>
                );
              }
              if (log.type === 'warn') {
                return (
                  <div key={index} className="flex gap-2 text-amber-400 bg-amber-500/5 p-2 border border-amber-500/10 rounded-lg whitespace-pre-wrap">
                    <AlertTriangle className="w-4 h-4 shrink-0 text-amber-400 mt-0.5" />
                    <span>{log.text}</span>
                  </div>
                );
              }
              if (log.type === 'info') {
                return (
                  <div key={index} className="flex gap-2 text-blue-400 bg-blue-500/5 p-2 border border-blue-500/10 rounded-lg whitespace-pre-wrap">
                    <Info className="w-4 h-4 shrink-0 text-blue-400 mt-0.5" />
                    <span>{log.text}</span>
                  </div>
                );
              }
              if (log.type === 'system') {
                return (
                  <div key={index} className="text-muted font-bold tracking-wide italic border-l-2 border-border/80 pl-2.5 py-0.5">
                    {log.text}
                  </div>
                );
              }
              return (
                <div key={index} className="text-slate-200 whitespace-pre-wrap">
                  {log.text}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
