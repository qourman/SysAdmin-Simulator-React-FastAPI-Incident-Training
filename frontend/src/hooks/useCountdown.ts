import { useEffect, useRef, useState } from 'react';

export function useCountdown(initialSeconds: number) {
  const [secondsRemaining, setSecondsRemaining] = useState(initialSeconds);
  const [isActive, setIsActive] = useState(false);
  const intervalRef = useRef<number | undefined>(undefined);

  useEffect(() => {
    if (!isActive) {
      if (intervalRef.current !== undefined) {
        window.clearInterval(intervalRef.current);
      }
      return;
    }

    intervalRef.current = window.setInterval(() => {
      setSecondsRemaining((prev) => Math.max(prev - 1, 0));
    }, 1000);

    return () => {
      if (intervalRef.current !== undefined) {
        window.clearInterval(intervalRef.current);
      }
    };
  }, [isActive]);

  const start = (seconds: number) => {
    setSecondsRemaining(seconds);
    setIsActive(true);
  };

  const stop = () => {
    setIsActive(false);
    if (intervalRef.current !== undefined) {
      window.clearInterval(intervalRef.current);
    }
  };

  return {
    secondsRemaining,
    isActive,
    start,
    stop,
    setSecondsRemaining,
  } as const;
}
