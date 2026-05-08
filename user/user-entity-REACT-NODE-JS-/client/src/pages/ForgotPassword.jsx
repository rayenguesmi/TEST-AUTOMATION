import { useState } from 'react';
import { Link } from 'react-router-dom';
import { forgotPassword } from '../api/auth';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState({ loading: false, success: '', error: '' });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus({ loading: true, success: '', error: '' });

    try {
      const { data } = await forgotPassword({ email });
      setStatus({ loading: false, success: data.message, error: '' });
      setEmail('');
    } catch (err) {
      setStatus({
        loading: false,
        success: '',
        error: err.response?.data?.message || 'Something went wrong. Please try again.',
      });
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2 style={styles.title}>Forgot your password?</h2>
        <p style={styles.subtitle}>
          Enter your email and we will send you a link to reset your password.
        </p>

        {status.success && <p style={styles.success}>{status.success}</p>}
        {status.error && <p style={styles.error}>{status.error}</p>}

        <form onSubmit={handleSubmit} style={styles.form}>
          <label style={styles.label}>Email address</label>
          <input
            type="email"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={styles.input}
          />

          <button type="submit" disabled={status.loading} style={styles.button}>
            {status.loading ? 'Sending…' : 'Send Reset Link'}
          </button>
        </form>

        <p style={styles.footer}>
          <Link to="/login">Back to login</Link>
        </p>
      </div>
    </div>
  );
}

const styles = {
  container: { display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', background: '#f3f4f6' },
  card: { background: '#fff', borderRadius: 10, padding: '40px 36px', width: '100%', maxWidth: 420, boxShadow: '0 4px 20px rgba(0,0,0,0.08)' },
  title: { marginBottom: 8, fontSize: 24, fontWeight: 700, color: '#111' },
  subtitle: { marginBottom: 24, fontSize: 14, color: '#6b7280' },
  form: { display: 'flex', flexDirection: 'column', gap: 12 },
  label: { fontSize: 14, fontWeight: 600, color: '#374151' },
  input: { padding: '10px 14px', borderRadius: 6, border: '1px solid #d1d5db', fontSize: 14, outline: 'none' },
  button: { marginTop: 8, padding: '12px', background: '#4F46E5', color: '#fff', border: 'none', borderRadius: 6, fontSize: 15, fontWeight: 600, cursor: 'pointer' },
  success: { background: '#d1fae5', color: '#065f46', padding: '10px 14px', borderRadius: 6, marginBottom: 12, fontSize: 14 },
  error: { background: '#fee2e2', color: '#991b1b', padding: '10px 14px', borderRadius: 6, marginBottom: 12, fontSize: 14 },
  footer: { marginTop: 20, textAlign: 'center', fontSize: 14 },
};
