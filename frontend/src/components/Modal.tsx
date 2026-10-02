"use client";

import { X } from "lucide-react";
import { ReactNode, useEffect } from "react";

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  actions?: ReactNode;
}

export default function Modal({ open, onClose, title, children, actions }: ModalProps) {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    if (open) window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-dark-800 border border-dark-600 rounded-2xl shadow-2xl w-full max-w-md mx-4 animate-slide-in">
        <div className="flex items-center justify-between px-6 py-4 border-b border-dark-600">
          <h3 className="text-lg font-semibold text-white">{title}</h3>
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-dark-700 text-slate-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="px-6 py-4">{children}</div>
        {actions && <div className="px-6 py-4 border-t border-dark-600 flex justify-end gap-3">{actions}</div>}
      </div>
    </div>
  );
}
