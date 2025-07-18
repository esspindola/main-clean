const express = require('express');
const { body, validationResult } = require('express-validator');
const bcrypt = require('bcryptjs');
const User = require('../models/User');
const { auth } = require('../middleware/auth');

const router = express.Router();

// Get user profile
router.get('/', auth, async (req, res) => {
  try {
    res.json({
      user: req.user.toJSON()
    });
  } catch (error) {
    console.error('Get profile error:', error);
    res.status(500).json({ error: 'Failed to get profile' });
  }
});

// Update profile
router.put('/', [
  body('fullName').optional().notEmpty().trim(),
  body('phone').optional().isMobilePhone(),
  body('address').optional().isString(),
  body('language').optional().isString(),
  body('timezone').optional().isString(),
  body('dateFormat').optional().isString(),
  body('currency').optional().isString(),
  body('notifications').optional().isObject(),
  body('notificationFrequency').optional().isString()
], auth, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const allowedFields = [
      'fullName', 'phone', 'address', 'language', 'timezone', 
      'dateFormat', 'currency', 'notifications', 'notificationFrequency'
    ];

    const updateData = {};
    for (const field of allowedFields) {
      if (req.body[field] !== undefined) {
        updateData[field] = req.body[field];
      }
    }

    await req.user.update(updateData);

    res.json({
      message: 'Profile updated successfully',
      user: req.user.toJSON()
    });
  } catch (error) {
    console.error('Update profile error:', error);
    res.status(500).json({ error: 'Failed to update profile' });
  }
});

// Change password
router.put('/password', [
  body('currentPassword').notEmpty(),
  body('newPassword').isLength({ min: 8 }),
  body('confirmPassword').notEmpty()
], auth, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { currentPassword, newPassword, confirmPassword } = req.body;

    // Check if new password matches confirmation
    if (newPassword !== confirmPassword) {
      return res.status(400).json({ error: 'New password and confirmation do not match' });
    }

    // Verify current password
    const isValidPassword = await req.user.comparePassword(currentPassword);
    if (!isValidPassword) {
      return res.status(400).json({ error: 'Current password is incorrect' });
    }

    // Update password
    req.user.password = newPassword;
    await req.user.save();

    res.json({ message: 'Password changed successfully' });
  } catch (error) {
    console.error('Change password error:', error);
    res.status(500).json({ error: 'Failed to change password' });
  }
});

// Update notification settings
router.put('/notifications', [
  body('notifications').isObject(),
  body('notificationFrequency').optional().isString()
], auth, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { notifications, notificationFrequency } = req.body;

    await req.user.update({
      notifications,
      notificationFrequency
    });

    res.json({
      message: 'Notification settings updated successfully',
      notifications: req.user.notifications,
      notificationFrequency: req.user.notificationFrequency
    });
  } catch (error) {
    console.error('Update notifications error:', error);
    res.status(500).json({ error: 'Failed to update notification settings' });
  }
});

// Get user sessions (mock data for now)
router.get('/sessions', auth, async (req, res) => {
  try {
    // In a real app, you would store sessions in a separate table
    // For now, return mock data
    const sessions = [
      {
        id: '1',
        device: 'MacBook Pro - Chrome',
        location: 'Ciudad de México, México',
        lastActive: 'Ahora',
        current: true
      },
      {
        id: '2',
        device: 'iPhone 14 - Safari',
        location: 'Ciudad de México, México',
        lastActive: 'Hace 2 horas',
        current: false
      }
    ];

    res.json({ sessions });
  } catch (error) {
    console.error('Get sessions error:', error);
    res.status(500).json({ error: 'Failed to get sessions' });
  }
});

// Close session (mock implementation)
router.delete('/sessions/:sessionId', auth, async (req, res) => {
  try {
    // In a real app, you would invalidate the session token
    res.json({ message: 'Session closed successfully' });
  } catch (error) {
    console.error('Close session error:', error);
    res.status(500).json({ error: 'Failed to close session' });
  }
});

// Get user statistics
router.get('/stats', auth, async (req, res) => {
  try {
    // In a real app, you would calculate these from actual data
    const stats = {
      totalProducts: 0,
      activeProducts: 0,
      totalSales: 0,
      totalRevenue: 0,
      lowStockProducts: 0,
      lastLogin: req.user.lastAccess
    };

    res.json({ stats });
  } catch (error) {
    console.error('Get stats error:', error);
    res.status(500).json({ error: 'Failed to get statistics' });
  }
});

// Export user data
router.get('/export', auth, async (req, res) => {
  try {
    // In a real app, you would generate a comprehensive export
    const exportData = {
      user: req.user.toJSON(),
      exportDate: new Date().toISOString(),
      format: 'json'
    };

    res.json(exportData);
  } catch (error) {
    console.error('Export data error:', error);
    res.status(500).json({ error: 'Failed to export data' });
  }
});

// Delete account
router.delete('/', [
  body('password').notEmpty()
], auth, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { password } = req.body;

    // Verify password
    const isValidPassword = await req.user.comparePassword(password);
    if (!isValidPassword) {
      return res.status(400).json({ error: 'Password is incorrect' });
    }

    // In a real app, you might want to soft delete or anonymize data
    await req.user.destroy();

    res.json({ message: 'Account deleted successfully' });
  } catch (error) {
    console.error('Delete account error:', error);
    res.status(500).json({ error: 'Failed to delete account' });
  }
});

module.exports = router; 