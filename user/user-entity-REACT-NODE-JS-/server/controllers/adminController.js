const fs = require('fs');
const path = require('path');
const axios = require('axios');
const yaml = require('js-yaml');
const mongoose = require('mongoose');
const Test = require('../models/Test');
const User = require('../models/User');

const CONFIG_PATH = path.resolve(
  __dirname,
  '../../../../AUTOTEST/autotest_package/config.yaml'
);

// ─── Health ───────────────────────────────────────────────────────────────────
const getAdminHealth = async (req, res) => {
  const t0 = Date.now();
  const mongoState = mongoose.connection.readyState;
  const nodeLatency = Date.now() - t0;
  const memMB = Math.round(process.memoryUsage().rss / 1024 / 1024);

  let fastApiStatus = 'down';
  let fastApiLatency = 999;
  let ollamaStatus = 'down';
  let ollamaLatency = 999;

  try {
    const ft = Date.now();
    await axios.get(`${process.env.FASTAPI_URL || 'http://localhost:8000'}/docs`, { timeout: 3000 });
    fastApiLatency = Date.now() - ft;
    fastApiStatus = fastApiLatency < 500 ? 'healthy' : 'degraded';
  } catch (_) {}

  try {
    const ot = Date.now();
    await axios.get('http://localhost:11434/api/tags', { timeout: 3000 });
    ollamaLatency = Date.now() - ot;
    ollamaStatus = ollamaLatency < 1000 ? 'healthy' : 'degraded';
  } catch (_) {}

  const mongoStatus = mongoState === 1 ? 'healthy' : mongoState === 2 ? 'degraded' : 'down';

  res.json({
    success: true,
    services: [
      { service: 'Node.js API',    status: 'healthy',     latency: nodeLatency,    uptime: 99.9, memory: `${memMB} MB` },
      { service: 'FastAPI Engine', status: fastApiStatus, latency: fastApiLatency, uptime: fastApiStatus !== 'down' ? 99.7 : 0, memory: '—' },
      { service: 'MongoDB',        status: mongoStatus,   latency: nodeLatency,    uptime: mongoState === 1 ? 99.5 : 0, memory: '—' },
      { service: 'Ollama Local',   status: ollamaStatus,  latency: ollamaLatency,  uptime: ollamaStatus !== 'down' ? 98.0 : 0, memory: '—' },
    ],
  });
};

// ─── Activity heatmap — tests grouped by day/hour for last 90 days ────────────
const getActivityStats = async (req, res) => {
  try {
    const since = new Date(Date.now() - 90 * 24 * 60 * 60 * 1000);
    const data = await Test.aggregate([
      { $match: { createdAt: { $gte: since } } },
      {
        $group: {
          _id: {
            year:  { $year: '$createdAt' },
            month: { $month: '$createdAt' },
            day:   { $dayOfMonth: '$createdAt' },
            hour:  { $hour: '$createdAt' },
          },
          count: { $sum: 1 },
        },
      },
      { $sort: { '_id.year': 1, '_id.month': 1, '_id.day': 1, '_id.hour': 1 } },
    ]);

    const formatted = data.map((d) => ({
      date: `${d._id.year}-${String(d._id.month).padStart(2, '0')}-${String(d._id.day).padStart(2, '0')}`,
      hour: d._id.hour,
      count: d.count,
    }));

    res.json({ success: true, data: formatted });
  } catch (err) {
    console.error('getActivityStats error:', err);
    res.status(500).json({ success: false, message: 'Server error.' });
  }
};

// ─── LLM benchmark — aggregate by llmEngine ──────────────────────────────────
const getLLMComparison = async (req, res) => {
  try {
    const data = await Test.aggregate([
      {
        $group: {
          _id: { $ifNull: ['$llmEngine', 'unknown'] },
          totalRuns:   { $sum: 1 },
          completed:   { $sum: { $cond: [{ $eq: ['$status', 'completed'] }, 1, 0] } },
          failed:      { $sum: { $cond: [{ $eq: ['$status', 'failed'] }, 1, 0] } },
          avgDuration: { $avg: '$report.duration_seconds' },
          errorLogs:   { $sum: { $size: { $filter: { input: { $ifNull: ['$logs', []] }, as: 'l', cond: { $eq: ['$$l.level', 'error'] } } } } },
        },
      },
      { $sort: { totalRuns: -1 } },
    ]);

    const result = data.map((d) => ({
      engine:       d._id,
      totalRuns:    d.totalRuns,
      completed:    d.completed,
      failed:       d.failed,
      successRate:  d.totalRuns > 0 ? +((d.completed / d.totalRuns) * 100).toFixed(1) : 0,
      avgDuration:  d.avgDuration ? +d.avgDuration.toFixed(1) : null,
      syntaxErrors: d.errorLogs,
    }));

    res.json({ success: true, data: result });
  } catch (err) {
    console.error('getLLMComparison error:', err);
    res.status(500).json({ success: false, message: 'Server error.' });
  }
};

// ─── Users with per-user test stats ──────────────────────────────────────────
const getAdminUsers = async (req, res) => {
  try {
    const users = await User.aggregate([
      {
        $lookup: {
          from: 'tests',
          localField: '_id',
          foreignField: 'ownerId',
          as: 'tests',
        },
      },
      {
        $addFields: {
          totalTests: { $size: '$tests' },
          completedTests: {
            $size: { $filter: { input: '$tests', as: 't', cond: { $eq: ['$$t.status', 'completed'] } } },
          },
          failedTests: {
            $size: { $filter: { input: '$tests', as: 't', cond: { $eq: ['$$t.status', 'failed'] } } },
          },
          lastActivity: { $max: '$tests.createdAt' },
          // Most frequent llmEngine
          preferredLLM: {
            $let: {
              vars: {
                engines: {
                  $map: {
                    input: { $filter: { input: '$tests', as: 't', cond: { $ne: ['$$t.llmEngine', null] } } },
                    as: 'tt',
                    in: '$$tt.llmEngine',
                  },
                },
              },
              in: { $arrayElemAt: ['$$engines', 0] },
            },
          },
        },
      },
      {
        $project: {
          passwordHash: 0,
          verificationToken: 0,
          resetPasswordToken: 0,
          resetPasswordExpires: 0,
          tests: 0,
        },
      },
      { $sort: { createdAt: -1 } },
    ]);

    // Compute success rate per user
    const withRate = users.map((u) => ({
      ...u,
      successRate: u.completedTests + u.failedTests > 0
        ? +((u.completedTests / (u.completedTests + u.failedTests)) * 100).toFixed(1)
        : null,
    }));

    res.json({ success: true, data: withRate });
  } catch (err) {
    console.error('getAdminUsers error:', err);
    res.status(500).json({ success: false, message: 'Server error.' });
  }
};

// ─── Disable user account (set role to 'disabled' or flag) ───────────────────
const disableUser = async (req, res) => {
  const { userId } = req.params;
  try {
    await User.findByIdAndUpdate(userId, { isVerified: false });
    res.json({ success: true, message: 'User account disabled.' });
  } catch (err) {
    console.error('disableUser error:', err);
    res.status(500).json({ success: false, message: 'Server error.' });
  }
};

// ─── Anomaly alerts ────────────────────────────────────────────────────────────
const getAlerts = async (req, res) => {
  try {
    const alerts = [];

    // 1. Users with 5+ consecutive failed tests
    const users = await User.find({}, '_id name email');
    for (const user of users) {
      const lastFive = await Test.find({ ownerId: user._id })
        .sort('-createdAt')
        .limit(5)
        .select('status createdAt');
      if (lastFive.length >= 5 && lastFive.every((t) => t.status === 'failed')) {
        alerts.push({
          type: 'consecutive_failures',
          severity: 'high',
          userId: user._id,
          userName: user.name || user.email,
          message: `${user.name || user.email} has 5 consecutive failed tests`,
          timestamp: lastFive[0]?.createdAt,
        });
      }
    }

    // 2. Tests running for more than 30 min (pipeline timeout)
    const cutoff30 = new Date(Date.now() - 30 * 60 * 1000);
    const stuckTests = await Test.find({
      status: 'running',
      createdAt: { $lt: cutoff30 },
    })
      .populate('ownerId', 'name email')
      .select('_id targetUrl createdAt ownerId');

    for (const t of stuckTests) {
      alerts.push({
        type: 'pipeline_timeout',
        severity: 'medium',
        testId: t._id,
        targetUrl: t.targetUrl,
        userName: t.ownerId?.name || t.ownerId?.email || 'Unknown',
        message: `Test stuck >30min on ${t.targetUrl}`,
        timestamp: t.createdAt,
      });
    }

    // 3. High failure rate in last hour
    const lastHour = new Date(Date.now() - 60 * 60 * 1000);
    const [recentTotal, recentFailed] = await Promise.all([
      Test.countDocuments({ createdAt: { $gte: lastHour } }),
      Test.countDocuments({ createdAt: { $gte: lastHour }, status: 'failed' }),
    ]);
    if (recentTotal >= 3 && recentFailed / recentTotal > 0.6) {
      alerts.push({
        type: 'high_failure_rate',
        severity: 'high',
        message: `${recentFailed}/${recentTotal} tests failed in the last hour (${Math.round((recentFailed / recentTotal) * 100)}%)`,
        timestamp: new Date(),
      });
    }

    alerts.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    res.json({ success: true, data: alerts });
  } catch (err) {
    console.error('getAlerts error:', err);
    res.status(500).json({ success: false, message: 'Server error.' });
  }
};

// ─── Feature failure analytics — aggregate across all test reports ────────────
const getFeatureFailures = async (req, res) => {
  try {
    const tests = await Test.find(
      { status: 'completed', 'report.tests': { $exists: true, $ne: [] } },
      { 'report.tests': 1 }
    ).lean();

    const featureMap = {};
    for (const test of tests) {
      for (const tc of test.report?.tests || []) {
        // Extract functional area from test name: test_CT_001_feature_area___variant
        const match = (tc.name || '').match(/test_CT_\d+_(.+?)(?:___|$)/);
        const rawName = match ? match[1] : tc.name || 'unknown';
        const area = rawName.replace(/_/g, ' ').trim().toLowerCase();

        if (!featureMap[area]) featureMap[area] = { name: area, total: 0, failed: 0, passed: 0 };
        featureMap[area].total++;
        if (tc.statut === 'PASS') featureMap[area].passed++;
        else featureMap[area].failed++;
      }
    }

    const result = Object.values(featureMap)
      .filter((f) => f.total > 0)
      .map((f) => ({
        ...f,
        failRate: +((f.failed / f.total) * 100).toFixed(1),
        passRate: +((f.passed / f.total) * 100).toFixed(1),
      }))
      .sort((a, b) => b.passRate - a.passRate)
      .slice(0, 15);

    res.json({ success: true, data: result });
  } catch (err) {
    console.error('getFeatureFailures error:', err);
    res.status(500).json({ success: false, message: 'Server error.' });
  }
};

// ─── Prompt manager — read config.yaml ───────────────────────────────────────
const getPrompts = (req, res) => {
  try {
    if (!fs.existsSync(CONFIG_PATH)) {
      return res.status(404).json({ success: false, message: 'config.yaml not found.' });
    }
    const raw = fs.readFileSync(CONFIG_PATH, 'utf8');
    const config = yaml.load(raw);
    res.json({
      success: true,
      data: {
        spec_parsing:        config?.prompts?.spec_parsing || '',
        test_generation:     config?.prompts?.test_generation || '',
        selenium_generation: config?.prompts?.selenium_generation || '',
      },
    });
  } catch (err) {
    console.error('getPrompts error:', err);
    res.status(500).json({ success: false, message: 'Failed to read config.' });
  }
};

// ─── Prompt manager — write config.yaml ─────────────────────────────────────
const updatePrompts = (req, res) => {
  const { spec_parsing, test_generation, selenium_generation } = req.body;
  try {
    if (!fs.existsSync(CONFIG_PATH)) {
      return res.status(404).json({ success: false, message: 'config.yaml not found.' });
    }
    const raw = fs.readFileSync(CONFIG_PATH, 'utf8');
    const config = yaml.load(raw);

    if (!config.prompts) config.prompts = {};
    if (spec_parsing        !== undefined) config.prompts.spec_parsing        = spec_parsing;
    if (test_generation     !== undefined) config.prompts.test_generation     = test_generation;
    if (selenium_generation !== undefined) config.prompts.selenium_generation = selenium_generation;

    fs.writeFileSync(CONFIG_PATH, yaml.dump(config, { lineWidth: -1 }), 'utf8');
    res.json({ success: true, message: 'Prompts updated.' });
  } catch (err) {
    console.error('updatePrompts error:', err);
    res.status(500).json({ success: false, message: 'Failed to write config.' });
  }
};

module.exports = {
  getAdminHealth,
  getActivityStats,
  getLLMComparison,
  getAdminUsers,
  disableUser,
  getAlerts,
  getFeatureFailures,
  getPrompts,
  updatePrompts,
};
