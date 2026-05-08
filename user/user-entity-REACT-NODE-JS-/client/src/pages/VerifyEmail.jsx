import { Link, useSearchParams } from 'react-router-dom';

/**
 * Landing page for the email verification flow.
 * The server redirects to: /verify-email?status=success  or  /verify-email?status=error
 */
export default function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const status = searchParams.get('status');

  const isSuccess = status === 'success';

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.icon}>{isSuccess ? '✅' : '❌'}</div>

        <h2 style={{ ...styles.title, color: isSuccess ? '#065f46' : '#991b1b' }}>
          {isSuccess ? 'Email Verified!' : 'Verification Failed'}
        </h2>

        <p style={styles.message}>
          {isSuccess
            ? 'Your email has been successfully verified. You can now log in to your account.'
            : 'The verification link is invalid or has already been used. Please register again or contact support.'}
        </p>

        {isSuccess ? (
          <Link to="/login" style={styles.button}>
            Go to Login
          </Link>
        ) : (
          <Link to="/register" style={{ ...styles.button, background: '#EF4444' }}>
            Back to Register
          </Link>
        )}
      </div>
    </div>
  );
}

const styles = {
  container: { display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', background: '#f3f4f6' },
  card: { background: '#fff', borderRadius: 10, padding: '48px 36px', width: '100%', maxWidth: 420, boxShadow: '0 4px 20px rgba(0,0,0,0.08)', textAlign: 'center' },
  icon: { fontSize: 52, marginBottom: 16 },
  title: { fontSize: 24, fontWeight: 700, marginBottom: 12 },
  message: { fontSize: 15, color: '#6b7280', marginBottom: 28, lineHeight: 1.6 },
  button: { display: 'inline-block', padding: '12px 28px', background: '#4F46E5', color: '#fff', borderRadius: 6, textDecoration: 'none', fontWeight: 600, fontSize: 15 },
};
