const crypto = require('crypto');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { validationResult } = require('express-validator');
const User = require('../models/User');
const { sendVerificationEmail, sendPasswordResetEmail } = require('../utils/sendEmail');

// ─── Helpers ────────────────────────────────────────────────────────────────

/**
 * Signs a JWT access token valid for 7 days.
 * @param {string} userId - MongoDB _id of the user
 * @param {string} role   - User role (user/admin)
 */
const signToken = (userId, role) =>
  jwt.sign({ id: userId, role: role }, process.env.JWT_SECRET, { expiresIn: '7d' });

/**
 * Attaches a JWT in an httpOnly cookie and returns it in the response.
 * @param {Object} res      - Express response object
 * @param {string} token    - Signed JWT string
 */
const attachCookie = (res, token) => {
  res.cookie('token', token, {
    httpOnly: true,               // Not accessible via document.cookie (XSS protection)
    secure: process.env.NODE_ENV === 'production', // HTTPS only in prod
    sameSite: 'lax',
    maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days in ms
  });
};

// ─── Controllers ────────────────────────────────────────────────────────────

/**
 * POST /api/auth/register
 * Creates a new unverified user and sends a verification email.
 */
const register = async (req, res) => {
  // Check express-validator results
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ success: false, message: errors.array()[0].msg });
  }

  const { name, email, password } = req.body;

  try {
    // Reject if email already exists
    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(409).json({ success: false, message: 'Email already registered.' });
    }

    // Hash the password (salt rounds = 12)
    const passwordHash = await bcrypt.hash(password, 12);

    // Generate a secure random token for email verification
    const verificationToken = crypto.randomBytes(32).toString('hex');

    const user = await User.create({
      name,
      email,
      passwordHash,
      verificationToken,
    });

    // Send the verification email (non-blocking — don't fail registration if email fails)
    try {
      await sendVerificationEmail(email, verificationToken);
    } catch (emailErr) {
      console.error('Verification email failed:', emailErr.message);
    }

    return res.status(201).json({
      success: true,
      message: 'Registration successful. Please check your email to verify your account.',
    });
  } catch (err) {
    console.error('Register error:', err);
    return res.status(500).json({ success: false, message: 'Server error during registration.' });
  }
};

/**
 * GET /api/auth/verify-email?token=<verificationToken>
 * Verifies the user's email and clears the token.
 */
const verifyEmail = async (req, res) => {
  const { token } = req.query;
  console.log(`Verification attempt with token: ${token}`);

  if (!token) {
    return res.status(400).json({ success: false, message: 'Verification token is missing.' });
  }

  try {
    const user = await User.findOne({ verificationToken: token });

    if (!user) {
      return res.status(400).json({ success: false, message: 'Invalid or expired verification token.' });
    }

    // Mark as verified and clear the one-time token
    user.isVerified = true;
    user.verificationToken = null;
    await user.save();

    // Redirect the browser to the frontend success page
    return res.redirect(`${process.env.CLIENT_URL}/verify-email?status=success`);
  } catch (err) {
    console.error('Verify email error:', err);
    return res.redirect(`${process.env.CLIENT_URL}/verify-email?status=error`);
  }
};

/**
 * POST /api/auth/login
 * Authenticates a verified user and issues a JWT cookie.
 */
const login = async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ success: false, message: errors.array()[0].msg });
  }

  const { email, password } = req.body;
  console.log(`Login attempt for: ${email}`);

  try {
    const user = await User.findOne({ email });

    // Generic message to avoid user enumeration
    if (!user) {
      console.log('Login failed: User not found');
      return res.status(401).json({ success: false, message: 'Invalid email or password.' });
    }

    // Block login for unverified accounts
    if (!user.isVerified) {
      console.log('Login failed: Email not verified');
      return res.status(403).json({
        success: false,
        message: 'Please verify your email address before logging in.',
      });
    }

    const isMatch = await bcrypt.compare(password, user.passwordHash);
    if (!isMatch) {
      console.log('Login failed: Password mismatch');
      return res.status(401).json({ success: false, message: 'Invalid email or password.' });
    }

    const token = signToken(user._id, user.role);
    attachCookie(res, token);
    console.log(`Login successful for: ${email} (Role: ${user.role})`);

    return res.status(200).json({
      success: true,
      message: 'Login successful.',
      data: {
        id: user._id,
        name: user.name,
        email: user.email,
        role: user.role,
      },
    });
  } catch (err) {
    console.error('Login error detail:', err);
    return res.status(500).json({ success: false, message: 'Server error during login.' });
  }
};

/**
 * POST /api/auth/forgot-password
 * Generates a password reset token and emails the reset link.
 */
const forgotPassword = async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ success: false, message: errors.array()[0].msg });
  }

  const { email } = req.body;

  try {
    const user = await User.findOne({ email });

    // Always return success to prevent email enumeration attacks
    if (!user) {
      return res.status(200).json({
        success: true,
        message: 'If that email is registered, a reset link has been sent.',
      });
    }

    // Generate a secure random reset token, valid for 1 hour
    const resetToken = crypto.randomBytes(32).toString('hex');
    user.resetPasswordToken = resetToken;
    user.resetPasswordExpires = Date.now() + 60 * 60 * 1000; // 1 hour from now
    await user.save();

    try {
      await sendPasswordResetEmail(email, resetToken);
    } catch (emailErr) {
      console.error('Reset email failed:', emailErr.message);
      // Clear the token if email sending failed
      user.resetPasswordToken = null;
      user.resetPasswordExpires = null;
      await user.save();
      return res.status(500).json({ success: false, message: 'Failed to send reset email. Try again.' });
    }

    return res.status(200).json({
      success: true,
      message: 'If that email is registered, a reset link has been sent.',
    });
  } catch (err) {
    console.error('Forgot password error:', err);
    return res.status(500).json({ success: false, message: 'Server error.' });
  }
};

/**
 * POST /api/auth/reset-password
 * Validates the reset token, then updates the password.
 */
const resetPassword = async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ success: false, message: errors.array()[0].msg });
  }

  const { token, password } = req.body;

  try {
    // Find user with a valid, non-expired token
    const user = await User.findOne({
      resetPasswordToken: token,
      resetPasswordExpires: { $gt: Date.now() }, // token must not be expired
    });

    if (!user) {
      return res.status(400).json({ success: false, message: 'Invalid or expired password reset token.' });
    }

    // Hash and save the new password, then clear reset fields
    user.passwordHash = await bcrypt.hash(password, 12);
    user.resetPasswordToken = null;
    user.resetPasswordExpires = null;
    await user.save();

    return res.status(200).json({
      success: true,
      message: 'Password has been reset successfully. You can now log in.',
    });
  } catch (err) {
    console.error('Reset password error:', err);
    return res.status(500).json({ success: false, message: 'Server error.' });
  }
};

/**
 * POST /api/auth/logout
 * Clears the httpOnly JWT cookie.
 */
const logout = (req, res) => {
  res.clearCookie('token', {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
  });

  return res.status(200).json({ success: true, message: 'Logged out successfully.' });
};

/**
 * GET /api/auth/me
 * Returns the currently authenticated user's profile.
 * Protected by authMiddleware (JWT required).
 */
const getMe = async (req, res) => {
  try {
    // req.user is attached by authMiddleware
    const user = await User.findById(req.user.id).select('-passwordHash -verificationToken -resetPasswordToken -resetPasswordExpires');

    if (!user) {
      return res.status(404).json({ success: false, message: 'User not found.' });
    }

    return res.status(200).json({
      success: true,
      data: user,
    });
  } catch (err) {
    console.error('Get me error:', err);
    return res.status(500).json({ success: false, message: 'Server error.' });
  }
};

module.exports = { register, verifyEmail, login, forgotPassword, resetPassword, logout, getMe };
