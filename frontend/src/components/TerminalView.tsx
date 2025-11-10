import { useEffect, useMemo, useRef } from 'react';
import { FitAddon } from '@xterm/addon-fit';
import { Terminal } from '@xterm/xterm';
import '@xterm/xterm/css/xterm.css';

interface TerminalViewProps {
  lines: string[];
  disabled?: boolean;
  onCommand?: (command: string) => void;
  promptLabel?: string;
}

const PROMPT_SUFFIX = '$ ';

export function TerminalView({
  lines,
  disabled = false,
  onCommand,
  promptLabel = 'sysadmin',
}: TerminalViewProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const terminalRef = useRef<Terminal | null>(null);
  const fitAddonRef = useRef<FitAddon | null>(null);
  const writtenLinesRef = useRef(0);
  const currentInputRef = useRef('');
  const commandHandlerRef = useRef<TerminalViewProps['onCommand']>(onCommand);

  useEffect(() => {
    commandHandlerRef.current = onCommand;
  }, [onCommand]);

  const prompt = useMemo(() => `${promptLabel}${PROMPT_SUFFIX}`, [promptLabel]);

  useEffect(() => {
    const term = new Terminal({
      cols: 80,
      rows: 24,
      cursorBlink: true,
      disableStdin: false,
      allowProposedApi: true,
    });
    const fitAddon = new FitAddon();
    terminalRef.current = term;
    fitAddonRef.current = fitAddon;

    if (containerRef.current) {
      term.loadAddon(fitAddon);
      term.open(containerRef.current);
      fitAddon.fit();
      term.write(`${prompt}`);
    }

    const handleResize = () => fitAddon.fit();
    window.addEventListener('resize', handleResize);

    const dataListener = term.onData((data: string) => {
      if (!commandHandlerRef.current || disabled) {
        return;
      }

      switch (data) {
        case '\r': {
          term.write('\r\n');
          const command = currentInputRef.current.trim();
          currentInputRef.current = '';
          commandHandlerRef.current(command);
          term.write(`${prompt}`);
          break;
        }
        case '\u0003': {
          term.write('^C\r\n');
          currentInputRef.current = '';
          term.write(`${prompt}`);
          break;
        }
        case '\u007F': {
          if (currentInputRef.current.length > 0) {
            term.write('\b \b');
            currentInputRef.current = currentInputRef.current.slice(0, -1);
          }
          break;
        }
        default: {
          if (data >= ' ') {
            term.write(data);
            currentInputRef.current += data;
          }
        }
      }
    });

    return () => {
      window.removeEventListener('resize', handleResize);
      dataListener.dispose();
      term.dispose();
    };
  }, [disabled, prompt]);

  useEffect(() => {
    if (!terminalRef.current) {
      return;
    }
    const term = terminalRef.current;

    if (lines.length < writtenLinesRef.current) {
      term.reset();
      writtenLinesRef.current = 0;
      currentInputRef.current = '';
      term.write(`${prompt}`);
    }

    const unwritten = lines.slice(writtenLinesRef.current);
    if (unwritten.length === 0) {
      return;
    }

    // Move cursor to new line to avoid cluttering the prompt.
    term.write('\r\n');
    unwritten.forEach((line) => {
      term.writeln(line);
    });
    writtenLinesRef.current = lines.length;
    term.write(`${prompt}${currentInputRef.current}`);
  }, [lines, prompt]);

  useEffect(() => {
    if (!terminalRef.current) {
      return;
    }
    terminalRef.current.options.disableStdin = disabled || !onCommand;
  }, [disabled, onCommand]);

  return <div className="terminal" ref={containerRef} />;
}
