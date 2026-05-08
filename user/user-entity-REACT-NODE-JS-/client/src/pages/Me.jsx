import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { getMe, logoutUser } from '../api/auth';

/**
 * Protected page — demonstrates the GET /api/auth/me endpoint.
 * Redirects to /login if the user is not authenticated.
 */
export default function Me() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    getMe()
      .then(({ data }) => setUser(data.data))
      .catch(() => {
        // 401 means no valid cookie — send to login
        navigate('/login');
      });
  }, [navigate]);

  const handleLogout = async () => {
    await logoutUser();
    navigate('/login');
  };

  if (!user && !error) {
    return (
      <div style={styles.container}>
        <p style={{ color: '#6b7280' }}>Loading profile…</p>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2 style={styles.title}>My Profile</h2>

        {user && (
          <div style={styles.info}>
            <Row label="Name" value={user.name} />
            <Row label="Email" value={user.email} />
            <Row label="Verified" value={user.isVerified ? 'Yes' : 'No'} />
            <Row label="Member since" value={new Date(user.createdAt).toLocaleDateString()} />
          </div>
        )}

        <button onClick={handleLogout} style={styles.button}>
          Log Out
        </button>

        <p style={styles.footer}>
          <Link to="/login">Back to login</Link>
        </p>
      </div>
    </div>
  );
}

const Row = ({ label, value }) => (
  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 0', borderBottom: '1px solid #f3f4f6' }}>
    <span style={{ fontWeight: 600, color: '#374151', fontSize: 14 }}>{label}</span>
    <span style={{ color: '#6b7280', fontSize: 14 }}>{value}</span>
  </div>
);

const styles = {
  container: { display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', background: '#f3f4f6' },
  card: { background: '#fff', borderRadius: 10, padding: '40px 36px', width: '100%', maxWidth: 440, boxShadow: '0 4px 20px rgba(0,0,0,0.08)' },
  title: { marginBottom: 24, fontSize: 24, fontWeight: 700, color: '#111' },
  info: { marginBottom: 28 },
  button: { width: '100%', padding: '12px', background: '#EF4444', color: '#fff', border: 'none', borderRadius: 6, fontSize: 15, fontWeight: 600, cursor: 'pointer' },
  footer: { marginTop: 16, textAlign: 'center', fontSize: 14 },
};
