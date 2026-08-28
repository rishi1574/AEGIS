"use client";
import { useState, useCallback } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || (typeof window !== 'undefined' ? `http://${window.location.hostname}:8000` : "http://127.0.0.1:8000");

export function useApi() {
  const [loading, setLoading] = useState(false);

  const get = useCallback(async (path: string) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}${path}`);
      return await res.json();
    } finally {
      setLoading(false);
    }
  }, []);

  const post = useCallback(async (path: string, body: any) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      return await res.json();
    } finally {
      setLoading(false);
    }
  }, []);

  return { get, post, loading };
}
