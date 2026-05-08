const express = require('express');
const { body } = require('express-validator');
const router = express.Router();

const {
  register,
  verifyEmail,
  login,
  forgotPassword,
  resetPassword,
  logout,
  getMe,
} = require('../controllers/authController');

const { verifyToken } = require('../middleware/authMiddleware');

// ─── Validation Rules ────────────────────────────────────────────────────────

const registerRules = [
  body('name').trim().notEmpty().withMessage('Name is required.')
    .isLength({ min: 2 }).withMessage('Name must be at least 2 characters.'),
  body('email').isEmail().withMessage('Please provide a valid email address.')
    .normalizeEmail(),
  body('password').isLength({ min: 6 }).withMessage('Password must be at least 6 characters.'),
];

const loginRules = [
  body('email').isEmail().withMessage('Please provide a valid email address.').normalizeEmail(),
  body('password').notEmpty().withMessage('Password is required.'),
];

const forgotPasswordRules = [
  body('email').isEmail().withMessage('Please provide a valid email address.').normalizeEmail(),
];

const resetPasswordRules = [
  body('token').notEmpty().withMessage('Reset token is required.'),
  body('password').isLength({ min: 6 }).withMessage('New password must be at least 6 characters.'),
];

// ─── Routes ──────────────────────────────────────────────────────────────────

// Public routes
router.post('/register', registerRules, register);
router.get('/verify-email', verifyEmail);
router.post('/login', loginRules, login);
router.post('/forgot-password', forgotPasswordRules, forgotPassword);
router.post('/reset-password', resetPasswordRules, resetPassword);
router.post('/logout', logout);

// Protected route — requires a valid JWT cookie
router.get('/me', verifyToken, getMe);

module.exports = router;
