import { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { resetPassword } from '../api/auth';

export default function ResetPassword() {
  // Read the token from the URL: /reset-password?token=<value>
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [status, setStatus] = useState({ loading: false, success: '', error: '' });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus({ loading: true, success: '', error: '' });

    if (password !== confirm) {
      return setStatus({ loading: false, success: '', error: 'Passwords do not match.' });
    }

    if (!token) {
      return setStatus({ loading: false, success: '', error: 'Reset token is missing from the URL.' });
    }

    try {
      const { data } = await resetPassword({ token, password });
      setStatus({ loading: false, success: data.message, error: '' });
      setPassword('');
      setConfirm('');
    } catch (err) {
      setStatus({
        loading: false,
        success: '',
        error: err.response?.data?.message || 'Reset failed. The link may have expired.',
      });
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2 style={styles.title}>Set a new password</h2>

        {status.success && (
          <div style={styles.success}>
            <p>{status.success}</p>
            <Link to="/login" style={{ color: '#065f46', fontWeight: 600 }}>Go to login</Link>
          </div>
        )}
        {status.error && <p style={styles.error}>{status.error}</p>}

        {!status.success && (
          <form onSubmit={handleSubmit} style={styles.form}>
            <label style={styles.label}>New Password</label>
            <input
              type="password"
              placeholder="At least 6 characters"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={styles.input}
            />

            <label style={styles.label}>Confirm Password</label>
            <input
              type="password"
              placeholder="Repeat new password"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              required
              style={styles.input}
            />

            <button type="submit" disabled={status.loading} style={styles.button}>
              {status.loading ? 'Resetting…' : 'Reset Password'}
            </button>
          </form>
        )}

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
  title: { marginBottom: 24, fontSize: 24, fontWeight: 700, color: '#111' },
  form: { display: 'flex', flexDirection: 'column', gap: 12 },
  label: { fontSize: 14, fontWeight: 600, color: '#374151' },
  input: { padding: '10px 14px', borderRadius: 6, border: '1px solid #d1d5db', fontSize: 14, outline: 'none' },
  button: { marginTop: 8, padding: '12px', background: '#EF4444', color: '#fff', border: 'none', borderRadius: 6, fontSize: 15, fontWeight: 600, cursor: 'pointer' },
  success: { background: '#d1fae5', color: '#065f46', padding: '10px 14px', borderRadius: 6, marginBottom: 12, fontSize: 14 },
  error: { background: '#fee2e2', color: '#991b1b', padding: '10px 14px', borderRadius: 6, marginBottom: 12, fontSize: 14 },
  footer: { marginTop: 20, textAlign: 'center', fontSize: 14 },
};
