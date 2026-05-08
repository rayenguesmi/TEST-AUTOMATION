const express = require('express');
const router = express.Router();
const {
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
} = require('../controllers/testController');
const { verifyToken, checkRole } = require('../middleware/authMiddleware');

// ─── Static routes (MUST be declared before /:id) ────────────────────────────
router.post('/start',    verifyToken, startTest);
router.post('/run',      verifyToken, runTest);
router.post('/webhook',  handleWebhook);
router.get('/my-tests',  verifyToken, getMyTests);
router.get('/filtered',  verifyToken, getFilteredTests);
router.get('/compare',   verifyToken, compareTests);

// ─── Admin routes (static — before /:id) ─────────────────────────────────────
router.get('/all',   verifyToken, checkRole('admin'), getAllTests);
router.get('/stats', verifyToken, checkRole('admin'), getGlobalStats);

// ─── Dynamic routes LAST ──────────────────────────────────────────────────────
router.get('/:id/progress', verifyToken, getTestProgress);
router.get('/:id/results',  verifyToken, getTestResults);
router.get('/:id',          verifyToken, getTestById);

module.exports = router;
