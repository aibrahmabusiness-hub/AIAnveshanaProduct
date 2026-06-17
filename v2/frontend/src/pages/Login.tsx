import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Login() {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.error || data.detail || 'Login failed');
        setLoading(false);
        return;
      }

      localStorage.removeItem('username');
      localStorage.setItem('username', data.username || username);
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('ap_token', data.ap_token || '');
      localStorage.setItem('ap_projectId', data.ap_projectId || '');
      navigate('/');
    } catch (err) {
      setError('Network error. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-800 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-slate-950/90 border border-slate-700 rounded-3xl shadow-2xl p-8 backdrop-blur-sm">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-extrabold text-cyan-300 mb-2">AI Anveshana</h1>
          <p className="text-slate-300">Sign in to your intelligent workflow workspace</p>
        </div>

        {error && (
          <div className="mb-6 p-3 bg-red-950/80 border border-red-500 rounded-xl">
            <p className="text-sm text-red-300 font-medium">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-slate-300 mb-2">
              Username
            </label>
            <input
              id="username"
              type="text"
              placeholder="Enter your username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-2xl text-slate-100 focus:outline-none focus:ring-2 focus:ring-cyan-400"
              required
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-slate-300 mb-2">
              Password
            </label>
            <input
              id="password"
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-2xl text-slate-100 focus:outline-none focus:ring-2 focus:ring-cyan-400"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-cyan-500 hover:bg-cyan-400 disabled:bg-slate-600 text-slate-950 font-semibold rounded-2xl transition"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-slate-400">
          Don't have an account?{' '}
          <button
            onClick={() => navigate('/signup')}
            className="text-cyan-300 hover:text-cyan-200 font-semibold"
          >
            Sign up
          </button>
        </div>
      </div>
    </div>
  );
}
