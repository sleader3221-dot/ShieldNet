import { useState } from 'react';
import { useRouter } from 'next/router';
import { motion, AnimatePresence } from 'framer-motion';
import { Hexagon, Shield, Eye, EyeOff, AlertCircle, CheckCircle, ArrowRight, Sparkles, Loader } from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '@/hooks/useAuth';

export default function LoginPage() {
  const router = useRouter();
  const { login, register } = useAuth();
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (isRegister) {
        await register({ username, email, password, full_name: fullName || undefined });
        toast.success('Account created successfully');
      } else {
        await login(username, password);
        toast.success('Welcome back');
      }
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Authentication failed');
      toast.error(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async (user: string) => {
    setError('');
    setLoading(true);
    setUsername(user);
    setPassword(user === 'admin' ? 'Admin@1234' : 'User@1234');
    try {
      await login(user, user === 'admin' ? 'Admin@1234' : 'User@1234');
      toast.success('Welcome back');
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-surface-darker flex">
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden bg-gradient-to-br from-primary-500/20 via-secondary-500/10 to-accent-500/20">
        <div className="absolute inset-0 bg-grid-glow opacity-50" />
        <div className="relative z-10 flex flex-col justify-center p-16">
          <motion.div initial={{ opacity: 0, x: -30 }} animate={{ opacity: 1, x: 0 }} className="mb-12">
            <div className="flex items-center gap-3 mb-6">
              <Hexagon className="w-10 h-10 text-primary-400" />
              <span className="text-3xl font-bold gradient-text">ShieldNet</span>
            </div>
            <h1 className="text-4xl font-bold text-white mb-4">
              AI-Powered Security Platform
            </h1>
            <p className="text-white/50 text-lg max-w-md">
              Protect, analyze, and secure your digital assets with real-time AI threat detection and blockchain security.
            </p>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="space-y-4">
            {[
              { icon: Shield, text: 'Real-time threat detection & response', color: 'text-primary-400' },
              { icon: CheckCircle, text: '99.9% uptime with instant failover', color: 'text-accent-400' },
              { icon: Sparkles, text: 'AI-powered predictive intelligence', color: 'text-secondary-400' },
            ].map((item, i) => (
              <div key={i} className="flex items-center gap-3">
                <item.icon className={`w-5 h-5 ${item.color}`} />
                <span className="text-white/60">{item.text}</span>
              </div>
            ))}
          </motion.div>

          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }} className="mt-12 p-4 glass rounded-xl">
            <div className="flex items-center gap-2 text-sm text-white/40 mb-2">
              <div className="w-2 h-2 rounded-full bg-accent-400 animate-pulse" />
              Platform Status
            </div>
            <div className="grid grid-cols-3 gap-4 text-center">
              {[
                { label: 'Threats Blocked', value: '12,847' },
                { label: 'Active Nodes', value: '1,432' },
                { label: 'Response Time', value: '<1ms' },
              ].map((s, i) => (
                <div key={i}>
                  <div className="text-lg font-bold gradient-text">{s.value}</div>
                  <div className="text-xs text-white/30">{s.label}</div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center p-8">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-md">
          <div className="lg:hidden flex items-center gap-3 mb-8 justify-center">
            <Hexagon className="w-8 h-8 text-primary-400" />
            <span className="text-2xl font-bold gradient-text">ShieldNet</span>
          </div>

          <h2 className="text-3xl font-bold text-white mb-2">
            {isRegister ? 'Create Account' : 'Welcome Back'}
          </h2>
          <p className="text-white/40 mb-8">
            {isRegister ? 'Set up your security dashboard' : 'Sign in to your security dashboard'}
          </p>

          <AnimatePresence mode="wait">
            {error && (
              <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }} className="mb-4 p-3 rounded-xl bg-danger-500/10 border border-danger-500/20 flex items-center gap-2 text-sm text-danger-400">
                <AlertCircle className="w-4 h-4 shrink-0" />
                {error}
              </motion.div>
            )}
          </AnimatePresence>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm text-white/60 mb-1.5">Username</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full h-12 px-4 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-white/20 focus:outline-none focus:border-primary-500/50 focus:bg-white/10 transition-all"
                placeholder="Enter your username"
                required
              />
            </div>

            <AnimatePresence>
              {isRegister && (
                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }}>
                  <label className="block text-sm text-white/60 mb-1.5">Email</label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full h-12 px-4 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-white/20 focus:outline-none focus:border-primary-500/50 focus:bg-white/10 transition-all"
                    placeholder="your@email.com"
                    required
                  />
                </motion.div>
              )}
            </AnimatePresence>

            <AnimatePresence>
              {isRegister && (
                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }}>
                  <label className="block text-sm text-white/60 mb-1.5">Full Name</label>
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="w-full h-12 px-4 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-white/20 focus:outline-none focus:border-primary-500/50 focus:bg-white/10 transition-all"
                    placeholder="John Doe"
                  />
                </motion.div>
              )}
            </AnimatePresence>

            <div>
              <label className="block text-sm text-white/60 mb-1.5">Password</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full h-12 px-4 pr-12 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-white/20 focus:outline-none focus:border-primary-500/50 focus:bg-white/10 transition-all"
                  placeholder="Enter your password"
                  required
                />
                <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-white/30 hover:text-white/60">
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full h-12 rounded-xl bg-gradient-to-r from-primary-500 to-secondary-500 text-white font-semibold flex items-center justify-center gap-2 hover:shadow-lg hover:shadow-primary-500/25 transition-all disabled:opacity-50"
            >
              {loading ? <Loader className="w-5 h-5 animate-spin" /> : null}
              {loading ? 'Please wait...' : isRegister ? 'Create Account' : 'Sign In'}
              {!loading && <ArrowRight className="w-4 h-4" />}
            </button>
          </form>

          <div className="mt-6 text-center">
            <button
              onClick={() => { setIsRegister(!isRegister); setError(''); }}
              className="text-sm text-primary-400 hover:text-primary-300 transition-colors"
            >
              {isRegister ? 'Already have an account? Sign In' : "Don't have an account? Register"}
            </button>
          </div>

          <div className="mt-8 pt-6 border-t border-white/5">
            <p className="text-xs text-white/30 text-center mb-3">Demo Accounts (click to login instantly)</p>
            <div className="grid grid-cols-2 gap-3">
              <button onClick={() => handleDemoLogin('admin')} className="p-3 rounded-xl glass glass-hover text-sm text-left group">
                <div className="font-medium text-white/70 group-hover:text-primary-300 transition-colors">Admin</div>
                <div className="text-xs text-white/30 mt-0.5">Full access</div>
              </button>
              <button onClick={() => handleDemoLogin('analyst')} className="p-3 rounded-xl glass glass-hover text-sm text-left group">
                <div className="font-medium text-white/70 group-hover:text-primary-300 transition-colors">Analyst</div>
                <div className="text-xs text-white/30 mt-0.5">Read + analyze</div>
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
