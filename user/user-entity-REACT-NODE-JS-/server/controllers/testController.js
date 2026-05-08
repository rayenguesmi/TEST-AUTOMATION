const Test = require('../models/Test');
const axios = require('axios');

/**
 * Initiates a new test by creating a record in MongoDB and notifying the FastAPI agent.
 */
const startTest = async (req, res) => {
  const { targetUrl, analysisType } = req.body;
  const ownerId = req.user.id;

  if (!targetUrl || !analysisType) {
    return res.status(400).json({ success: false, message: 'Target URL and analysis type are required.' });
  }

  try {
    // 1. Create test entry in MongoDB
    const test = await Test.create({
      ownerId,
      targetUrl,
      analysisType,
      status: 'pending',
    });

    // 2. Transmit request specifically to FastAPI
    // Pass the userId and testId for traceability
    try {
      // Assuming FastAPI is running and its URL is in .env
      const fastApiUrl = process.env.FASTAPI_URL || 'http://localhost:8000';
      
      // Non-blocking call or separate service would be better, 
      // but for now we'll do a simple POST
      axios.post(`${fastApiUrl}/run-test`, {
        testId: test._id,
        userId: ownerId,
        url: targetUrl,
        type: analysisType
      }).catch(err => console.error('Delayed FastAPI error:', err.message));

      test.status = 'running';
      await test.save();
    } catch (fastApiErr) {
      console.error('FastAPI immediate connection error:', fastApiErr.message);
      test.status = 'failed';
      test.logs.push({ 
        message: `Failed to connect to FastAPI engine: ${fastApiErr.message}`,
        level: 'error' 
      });
      await test.save();
    }

    return res.status(201).json({
      success: true,
      data: test,
      message: 'Test initiated successfully.'
    });
  } catch (err) {
    console.error('Start test error:', err);
    return res.status(500).json({ success: false, message: 'Server error while starting test.' });
  }
};

/**
 * Returns tests launched by the currently authenticated user.
 */
const getMyTests = async (req, res) => {
  try {
    const tests = await Test.find({ ownerId: req.user.id }).sort('-createdAt');
    return res.status(200).json({ success: true, data: tests });
  } catch (err) {
    console.error('Get my tests error:', err);
    return res.status(500).json({ success: false, message: 'Server error while fetching tests.' });
  }
};

/**
 * Returns all tests for Admin view.
 */
const getAllTests = async (req, res) => {
  try {
    const tests = await Test.find({})
      .populate('ownerId', 'name email')
      .sort('-createdAt');
    return res.status(200).json({ success: true, data: tests });
  } catch (err) {
    console.error('Get all tests error:', err);
    return res.status(500).json({ success: false, message: 'Server error while fetching tests.' });
  }
};

/**
 * Returns global platform statistics.
 */
const getGlobalStats = async (req, res) => {
  try {
    const totalTests = await Test.countDocuments();
    const completedTests = await Test.countDocuments({ status: 'completed' });
    const failedTests = await Test.countDocuments({ status: 'failed' });
    const activeUsers = await Test.distinct('ownerId');

    return res.status(200).json({
      success: true,
      data: {
        totalTests,
        completedTests,
        failedTests,
        activeUsersCount: activeUsers.length
      }
    });
  } catch (err) {
    console.error('Get stats error:', err);
    return res.status(500).json({ success: false, message: 'Server error while fetching stats.' });
  }
};

// ─── Helper: derive features array from report.tests ─────────────────────────
function extractFeaturesFromReport(reportTests = []) {
  const featureMap = {};
  reportTests.forEach((tc) => {
    const match = (tc.name || '').match(/test_CT_\d+_(.+?)(?:___|$)/);
    const rawName = match ? match[1] : tc.name || 'unknown';
    const area = rawName.replace(/_/g, ' ').trim();
    if (!featureMap[area]) featureMap[area] = { name: area, passed: 0, total: 0, testCases: [] };
    featureMap[area].total++;
    if (tc.statut === 'PASS') featureMap[area].passed++;
    featureMap[area].testCases.push({ name: tc.name, statut: tc.statut, duration: tc.durée_secondes || 0 });
  });
  return Object.entries(featureMap).map(([, d], i) => ({
    featureId: `F-${String(i + 1).padStart(3, '0')}`,
    name:      d.name,
    status:    d.passed === d.total ? 'PASS' : d.passed === 0 ? 'FAIL' : 'PARTIAL',
    passed:    d.passed,
    total:     d.total,
    testCases: d.testCases,
  }));
}

/**
 * GET /api/tests/:id/results
 * Returns the features array derived from report.tests (owned test only).
 */
const getTestResults = async (req, res) => {
  try {
    const test = await Test.findOne({ _id: req.params.id, ownerId: req.user.id });
    if (!test) return res.status(404).json({ success: false, message: 'Test not found.' });

    // Use persisted features or derive on-the-fly
    const features = test.features?.length
      ? test.features
      : extractFeaturesFromReport(test.report?.tests || []);

    res.json({ success: true, data: features });
  } catch (err) {
    console.error('getTestResults error:', err);
    res.status(500).json({ success: false, message: 'Server error.' });
  }
};

/**
 * GET /api/tests/filtered?status=&llm=&from=&to=
 * Returns current user's tests with optional filters.
 */
const getFilteredTests = async (req, res) => {
  const { status, llm, from, to } = req.query;
  try {
    const query = { ownerId: req.user.id };
    if (status && status !== 'all') query.status = status;
    if (llm    && llm    !== 'all') query.llmEngine = llm;
    if (from || to) {
      query.createdAt = {};
      if (from) query.createdAt.$gte = new Date(from);
      if (to)   query.createdAt.$lte = new Date(to);
    }
    const tests = await Test.find(query).sort('-createdAt');
    res.json({ success: true, data: tests });
  } catch (err) {
    console.error('getFilteredTests error:', err);
    res.status(500).json({ success: false, message: 'Server error.' });
  }
};

/**
 * GET /api/tests/compare?id1=&id2=
 * Compare features of two tests owned by the current user.
 */
const compareTests = async (req, res) => {
  const { id1, id2 } = req.query;
  if (!id1 || !id2) return res.status(400).json({ success: false, message: 'id1 and id2 required.' });
  try {
    const [t1, t2] = await Promise.all([
      Test.findOne({ _id: id1, ownerId: req.user.id }),
      Test.findOne({ _id: id2, ownerId: req.user.id }),
    ]);
    if (!t1 || !t2) return res.status(404).json({ success: false, message: 'One or both tests not found.' });

    const feat1 = t1.features?.length ? t1.features : extractFeaturesFromReport(t1.report?.tests || []);
    const feat2 = t2.features?.length ? t2.features : extractFeaturesFromReport(t2.report?.tests || []);

    // Build diff: features that changed status between run1 → run2
    const map1 = Object.fromEntries(feat1.map((f) => [f.name, f]));
    const map2 = Object.fromEntries(feat2.map((f) => [f.name, f]));
    const allNames = [...new Set([...Object.keys(map1), ...Object.keys(map2)])];

    const diff = allNames.map((name) => ({
      name,
      run1: map1[name] || null,
      run2: map2[name] || null,
      changed: map1[name]?.status !== map2[name]?.status,
      direction:
        !map1[name] ? 'new'
        : !map2[name] ? 'removed'
        : map1[name].status === 'FAIL' && map2[name].status === 'PASS' ? 'improved'
        : map1[name].status === 'PASS' && map2[name].status === 'FAIL' ? 'regressed'
        : 'unchanged',
    }));

    res.json({
      success: true,
      data: {
        test1: { _id: t1._id, targetUrl: t1.targetUrl, createdAt: t1.createdAt, status: t1.status },
        test2: { _id: t2._id, targetUrl: t2.targetUrl, createdAt: t2.createdAt, status: t2.status },
        diff,
      },
    });
  } catch (err) {
    console.error('compareTests error:', err);
    res.status(500).json({ success: false, message: 'Server error.' });
  }
};

/**
 * POST /api/tests/run
 * Orchestrates a generation-only pipeline: creates a DB record, calls FastAPI
 * /generate, and returns immediately. Results arrive via /webhook.
 */
const runTest = async (req, res) => {
  const { targetUrl, userSpecs, groqApiKey, provider = 'groq' } = req.body;
  const ownerId = req.user.id;

  if (!targetUrl || !userSpecs) {
    return res.status(400).json({ success: false, message: 'targetUrl and userSpecs are required.' });
  }
  // API key required only for cloud providers (not Ollama)
  if (provider !== 'ollama' && !groqApiKey) {
    return res.status(400).json({ success: false, message: 'groqApiKey is required for cloud providers.' });
  }

  let test;
  try {
    test = await Test.create({
      ownerId,
      targetUrl,
      userSpecs,
      analysisType: 'Génération de script',
      llmEngine: provider,
      status: 'running',
    });
  } catch (err) {
    console.error('runTest create error:', err);
    return res.status(500).json({ success: false, message: 'Failed to create test record.' });
  }

  const fastApiUrl = process.env.FASTAPI_URL || 'http://localhost:8000';
  const callbackUrl = `${process.env.SERVER_URL || 'http://localhost:5000'}/api/tests/webhook`;

  const faPayload = {
    url: targetUrl,
    specs: userSpecs,
    callback_url: callbackUrl,
    test_id: test._id.toString(),
    provider,
    ...(provider !== 'ollama' && groqApiKey ? { api_key: groqApiKey } : {}),
  };

  axios
    .post(`${fastApiUrl}/generate`, faPayload)
    .then(async (resp) => {
      const fastApiTaskId = resp.data?.task_id;
      if (fastApiTaskId) {
        await Test.findByIdAndUpdate(test._id, { fastApiTaskId });
      }
    })
    .catch(async (err) => {
      console.error('FastAPI /generate error:', err.message);
      await Test.findByIdAndUpdate(test._id, {
        status: 'failed',
        $push: { logs: { message: `FastAPI unreachable: ${err.message}`, level: 'error' } },
      });
    });

  return res.status(201).json({ success: true, data: test });
};

/**
 * POST /api/tests/webhook  (internal — called by FastAPI)
 * Updates the test record once FastAPI finishes generating the script.
 */
const handleWebhook = async (req, res) => {
  const { testId, status, script, report, reportHtmlUrl, logs, error } = req.body;

  if (!testId) {
    return res.status(400).json({ success: false, message: 'testId is required.' });
  }

  try {
    const features = report?.tests?.length ? extractFeaturesFromReport(report.tests) : [];
    const update = {
      status: status === 'completed' ? 'completed' : 'failed',
      ...(script && { generatedScript: script }),
      ...(report && { report }),
      ...(reportHtmlUrl && { reportHtmlUrl }),
      ...(features.length && { features }),
    };

    if (Array.isArray(logs) && logs.length) {
      update.$push = { logs: { $each: logs.map((msg) => ({ message: msg, level: 'info' })) } };
    } else if (error) {
      update.$push = { logs: { $each: [{ message: error, level: 'error' }] } };
    }

    await Test.findByIdAndUpdate(testId, update);
    return res.json({ success: true });
  } catch (err) {
    console.error('handleWebhook error:', err);
    return res.status(500).json({ success: false, message: 'Failed to update test record.' });
  }
};

/**
 * GET /api/tests/:id
 * Returns a single test belonging to the current user.
 */
const getTestById = async (req, res) => {
  try {
    const test = await Test.findOne({ _id: req.params.id, ownerId: req.user.id });
    if (!test) return res.status(404).json({ success: false, message: 'Test not found.' });
    return res.json({ success: true, data: test });
  } catch (err) {
    console.error('getTestById error:', err);
    return res.status(500).json({ success: false, message: 'Server error.' });
  }
};

/**
 * GET /api/tests/:id/progress
 * Returns the test status, enriched with live FastAPI progress.
 * If FastAPI reports completed/failed and the webhook hasn't fired yet,
 * syncs MongoDB directly so the frontend never gets stuck on 'running'.
 */
const getTestProgress = async (req, res) => {
  try {
    const test = await Test.findOne({ _id: req.params.id, ownerId: req.user.id });
    if (!test) return res.status(404).json({ success: false, message: 'Test not found.' });

    // Start with whatever is already in MongoDB
    let finalStatus      = test.status;
    let progress         = test.status;
    let finalScript      = test.generatedScript || null;
    let finalReport      = test.report          || null;
    let finalReportHtmlUrl = test.reportHtmlUrl || null;

    if (test.status === 'running' && test.fastApiTaskId) {
      try {
        const fastApiUrl = process.env.FASTAPI_URL || 'http://localhost:8000';
        const { data: fa } = await axios.get(
          `${fastApiUrl}/status/${test.fastApiTaskId}`,
          { timeout: 3000 }
        );

        progress = fa.progress || progress;

        // FastAPI finished — sync MongoDB directly (webhook may have failed)
        if (fa.status === 'completed' || fa.status === 'failed') {
          finalStatus = fa.status;
          finalScript = fa.script         || finalScript;
          finalReport = fa.test_results   || finalReport; // FastAPI key is "test_results"

          const syncUpdate = { status: finalStatus };
          if (finalScript) syncUpdate.generatedScript = finalScript;
          if (finalReport) syncUpdate.report          = finalReport;

          if (fa.status === 'completed') {
            const base = process.env.FASTAPI_URL || 'http://localhost:8000';
            finalReportHtmlUrl = `${base}/autotest-output/${test.fastApiTaskId}/reports/report.html`;
            syncUpdate.reportHtmlUrl = finalReportHtmlUrl;
          }

          await Test.findByIdAndUpdate(test._id, syncUpdate);
          console.log(`[progress] synced test ${test._id} → ${finalStatus} (webhook bypass)`);
        }

      } catch (err) {
        if (err.response?.status === 404) {
          // FastAPI restarted — task no longer in memory
          const updated = await Test.findOneAndUpdate(
            { _id: test._id, status: 'running' },
            {
              status: 'failed',
              $push: { logs: { message: "Le moteur IA a redémarré pendant l'exécution. Relancez le test.", level: 'error' } },
            },
            { new: true }
          );
          return res.json({
            success: true,
            data: {
              status:   updated ? 'failed' : test.status,
              progress: updated ? 'Moteur IA redémarré' : test.status,
              script:   finalScript,
              report:   finalReport,
              reportHtmlUrl: finalReportHtmlUrl,
              logs: test.logs,
            },
          });
        }
        // Network error / timeout — FastAPI temporarily unreachable, keep polling
      }
    }

    return res.json({
      success: true,
      data: {
        status:       finalStatus,
        progress,
        script:       finalScript,
        report:       finalReport,
        reportHtmlUrl: finalReportHtmlUrl,
        logs: test.logs,
      },
    });
  } catch (err) {
    console.error('getTestProgress error:', err);
    return res.status(500).json({ success: false, message: 'Server error.' });
  }
};

module.exports = {
  startTest,
  getMyTests,
  getAllTests,
  getGlobalStats,
  runTest,
  handleWebhook,
  getTestById,
  getTestProgress,
  getTestResults,
  getFilteredTests,
  compareTests,
};
