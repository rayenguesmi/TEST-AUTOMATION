const User = require('../models/User');

/**
 * Returns a list of all registered users (Admin only).
 */
const getAllUsers = async (req, res) => {
  try {
    const users = await User.find({}).select('-passwordHash');
    return res.status(200).json({ success: true, data: users });
  } catch (err) {
    console.error('Get all users error:', err);
    return res.status(500).json({ success: false, message: 'Server error while fetching users.' });
  }
};

/**
 * Updates a user's role (Admin only).
 */
const updateUserRole = async (req, res) => {
  const { userId, role } = req.body;

  if (!['user', 'admin'].includes(role)) {
    return res.status(400).json({ success: false, message: 'Invalid role.' });
  }

  try {
    const user = await User.findByIdAndUpdate(userId, { role }, { new: true }).select('-passwordHash');
    if (!user) {
      return res.status(404).json({ success: false, message: 'User not found.' });
    }
    return res.status(200).json({ success: true, data: user, message: 'User role updated successfully.' });
  } catch (err) {
    console.error('Update user role error:', err);
    return res.status(500).json({ success: false, message: 'Server error while updating role.' });
  }
};

/**
 * Bans/Deletes a user (Admin only).
 */
const deleteUser = async (req, res) => {
  const { id } = req.params;

  try {
    const user = await User.findByIdAndDelete(id);
    if (!user) {
      return res.status(404).json({ success: false, message: 'User not found.' });
    }
    return res.status(200).json({ success: true, message: 'User deleted successfully.' });
  } catch (err) {
    console.error('Delete user error:', err);
    return res.status(500).json({ success: false, message: 'Server error while deleting user.' });
  }
};

module.exports = {
  getAllUsers,
  updateUserRole,
  deleteUser
};
