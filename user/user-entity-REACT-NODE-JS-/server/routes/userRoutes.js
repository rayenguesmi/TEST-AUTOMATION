const express = require('express');
const router = express.Router();
const { getAllUsers, updateUserRole, deleteUser } = require('../controllers/userController');
const { verifyToken, checkRole } = require('../middleware/authMiddleware');

// All routes here are Admin only
router.use(verifyToken);
router.use(checkRole('admin'));

router.get('/all', getAllUsers);
router.patch('/role', updateUserRole);
router.delete('/:id', deleteUser);

module.exports = router;
