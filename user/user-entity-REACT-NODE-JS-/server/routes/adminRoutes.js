const express = require('express');
const router = express.Router();
const { verifyToken, checkRole } = require('../middleware/authMiddleware');
const {
  getAdminHealth,
  getActivityStats,
  getLLMComparison,
  getAdminUsers,
  disableUser,
  getAlerts,
  getFeatureFailures,
  getPrompts,
  updatePrompts,
} = require('../controllers/adminController');

const admin = [verifyToken, checkRole('admin')];

router.get('/health',                ...admin, getAdminHealth);
router.get('/stats/activity',        ...admin, getActivityStats);
router.get('/stats/llm-comparison',  ...admin, getLLMComparison);
router.get('/users',                 ...admin, getAdminUsers);
router.patch('/users/:userId/disable', ...admin, disableUser);
router.get('/alerts',                ...admin, getAlerts);
router.get('/stats/feature-failures', ...admin, getFeatureFailures);
router.get('/config/prompts',        ...admin, getPrompts);
router.put('/config/prompts',        ...admin, updatePrompts);

module.exports = router;
