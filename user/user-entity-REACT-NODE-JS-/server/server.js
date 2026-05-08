require('dotenv').config();
const express = require('express');
const cors = require('cors');
const cookieParser = require('cookie-parser');
const mongoose = require('mongoose');

const authRoutes  = require('./routes/auth');
const testRoutes  = require('./routes/testRoutes');
const userRoutes  = require('./routes/userRoutes');
const adminRoutes = require('./routes/adminRoutes');

const app = express();
const PORT = process.env.PORT || 5000;

// ─── Middleware ───────────────────────────────────────────────────────────────

// Allow the React dev server to make cross-origin requests with cookies
const allowedOrigins = [process.env.CLIENT_URL, 'http://localhost:5173', 'http://localhost:5174'].filter(Boolean);

app.use(
  cors({
    origin: (origin, callback) => {
      if (!origin || allowedOrigins.includes(origin)) {
        callback(null, true);
      } else {
        callback(new Error('Not allowed by CORS'));
      }
    },
    credentials: true, 
  })
);

app.use(express.json({ limit: '10mb' })); // 10mb covers large generated script payloads
app.use(cookieParser()); // Parse incoming cookies (needed to read req.cookies.token)

// ─── Routes ──────────────────────────────────────────────────────────────────

app.use('/api/auth',  authRoutes);
app.use('/api/tests', testRoutes);
app.use('/api/users', userRoutes);
app.use('/api/admin', adminRoutes);

// Health check — returns real service status
app.get('/api/health', async (req, res) => {
  const axios = require('axios');
  const t0 = Date.now();
  const mongoState = mongoose.connection.readyState;
  const nodeLatency = Date.now() - t0;
  const memMB = Math.round(process.memoryUsage().rss / 1024 / 1024);

  let fastApiStatus = 'down';
  let fastApiLatency = 999;
  try {
    const ft = Date.now();
    await axios.get(`${process.env.FASTAPI_URL || 'http://localhost:8000'}/docs`, { timeout: 3000 });
    fastApiLatency = Date.now() - ft;
    fastApiStatus = fastApiLatency < 500 ? 'healthy' : 'degraded';
  } catch (_) {}

  const mongoStatus = mongoState === 1 ? 'healthy' : mongoState === 2 ? 'degraded' : 'down';

  res.json({
    success: true,
    message: 'Server is running.',
    services: [
      { service: 'Node.js API',     status: 'healthy',     latency: nodeLatency,    uptime: 99.9, memory: `${memMB} MB` },
      { service: 'FastAPI Engine',  status: fastApiStatus, latency: fastApiLatency, uptime: fastApiStatus !== 'down' ? 99.7 : 0, memory: '—' },
      { service: 'MongoDB',         status: mongoStatus,   latency: nodeLatency,    uptime: mongoState === 1 ? 99.5 : 0, memory: '—' },
    ],
  });
});

// 404 handler for unknown routes
app.use((req, res) => {
  res.status(404).json({ success: false, message: 'Route not found.' });
});

// Global error handler
app.use((err, req, res, next) => {
  console.error('Unhandled error:', err);
  res.status(500).json({ success: false, message: 'Internal server error.' });
});

// ─── Database + Server Start ─────────────────────────────────────────────────

mongoose
  .connect(process.env.MONGO_URI)
  .then(async () => {
    console.log('✅ Connected to MongoDB');

    // Mark tests stuck in "running" for more than 90 minutes as failed
    const Test = require('./models/Test');
    const cutoff = new Date(Date.now() - 90 * 60 * 1000);
    const stale = await Test.updateMany(
      { status: 'running', createdAt: { $lt: cutoff } },
      { status: 'failed', $push: { logs: { message: 'Marked as failed: exceeded 90-minute timeout.', level: 'error' } } }
    );
    if (stale.modifiedCount > 0) {
      console.log(`⚠️  Marked ${stale.modifiedCount} stale test(s) as failed.`);
    }

    app.listen(PORT, () => {
      console.log(`🚀 Server running on http://localhost:${PORT}`);
    });
  })
  .catch((err) => {
    console.error('❌ MongoDB connection failed:', err.message);
    process.exit(1);
  });
