'use client';

import { useState } from 'react';
import { User } from '@/hooks/use-auth';
import { X } from 'lucide-react';

interface EditUserModalProps {
  user: User | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: (id: number, data: Partial<User>) => Promise<void>;
}

export function EditUserModal({ user, isOpen, onClose, onSave }: EditUserModalProps) {
  const [formData, setFormData] = useState<Partial<User>>({
    full_name: user?.full_name || '',
    email: user?.email || '',
    is_admin: user?.is_admin || false,
    disabled: user?.disabled || false,
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen || !user) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await onSave(user.id, formData);
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-surface rounded-2xl shadow-xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in duration-200 border border-border">
        <div className="flex items-center justify-between p-6 border-b border-border">
          <h3 className="text-xl font-bold text-foreground font-lexend">Edit User</h3>
          <button onClick={onClose} className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 transition-all">
            <X className="w-5 h-5" />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">Full Name</label>
            <input
              type="text"
              className="w-full px-4 py-2 rounded-lg border border-border bg-input text-foreground focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none"
              value={formData.full_name || ''}
              onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">Email</label>
            <input
              type="email"
              className="w-full px-4 py-2 rounded-lg border border-border bg-input/50 text-muted cursor-not-allowed outline-none"
              value={formData.email || ''}
              disabled
            />
          </div>
          <div className="flex items-center justify-between py-2">
            <div>
              <div className="text-sm font-medium text-foreground">Administrator</div>
              <div className="text-xs text-muted">Grant admin privileges</div>
            </div>
            <button
              type="button"
              onClick={() => setFormData({ ...formData, is_admin: !formData.is_admin })}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none ${
                formData.is_admin ? 'bg-primary' : 'bg-slate-200 dark:bg-slate-700'
              }`}
            >
              <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                formData.is_admin ? 'translate-x-6' : 'translate-x-1'
              }`} />
            </button>
          </div>
          <div className="flex items-center justify-between py-2 border-t border-border pt-4">
            <div>
              <div className="text-sm font-medium text-foreground">Disabled</div>
              <div className="text-xs text-muted">Disable user account</div>
            </div>
            <button
              type="button"
              onClick={() => setFormData({ ...formData, disabled: !formData.disabled })}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none ${
                formData.disabled ? 'bg-red-500' : 'bg-slate-200 dark:bg-slate-700'
              }`}
            >
              <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                formData.disabled ? 'translate-x-6' : 'translate-x-1'
              }`} />
            </button>
          </div>
          <div className="pt-6">
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full bg-primary hover:bg-primary-dark text-white font-semibold py-3 rounded-xl shadow-lg shadow-primary/20 transition-all disabled:opacity-50 flex items-center justify-center"
            >
              {isSubmitting ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
