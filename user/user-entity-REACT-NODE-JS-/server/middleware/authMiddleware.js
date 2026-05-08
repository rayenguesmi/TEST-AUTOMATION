const jwt = require('jsonwebtoken');
const User = require('../models/User');

/**
 * Middleware that protects routes requiring authentication.
 * Reads the JWT from the httpOnly cookie, verifies it, and attaches
 * the user payload to req.user so downstream handlers can use it.
 */
const verifyToken = async (req, res, next) => {
  const token = req.cookies?.token;

  if (!token) {
    return res.status(401).json({ success: false, message: 'Not authenticated. Please log in.' });
  }

  try {
    // Verify and decode the token
    const decoded = jwt.verify(token, process.env.JWT_SECRET);

    // Attach the user id and role to the request
    req.user = { id: decoded.id, role: decoded.role };

    next();
  } catch (err) {
    // Token is invalid or expired
    return res.status(401).json({ success: false, message: 'Session expired. Please log in again.' });
  }
};

/**
 * Middleware to restrict access based on user role.
 * @param {string} role - Required role ('admin' or 'user')
 */
const checkRole = (role) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ success: false, message: 'Authentication required.' });
    }

    if (req.user.role !== role && req.user.role !== 'admin') {
      return res.status(403).json({ success: false, message: `Access denied. Restricted to ${role}.` });
    }

    next();
  };
};

module.exports = { verifyToken, checkRole };
