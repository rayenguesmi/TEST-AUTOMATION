const mongoose = require('mongoose');

const userSchema = new mongoose.Schema(
  {
    name: {
      type: String,
      required: [true, 'Name is required'],
      trim: true,
      minlength: [2, 'Name must be at least 2 characters'],
      maxlength: [50, 'Name cannot exceed 50 characters'],
    },

    email: {
      type: String,
      required: [true, 'Email is required'],
      unique: true,
      lowercase: true,
      trim: true,
      match: [/^\S+@\S+\.\S+$/, 'Please provide a valid email address'],
    },

    passwordHash: {
      type: String,
      required: [true, 'Password is required'],
      minlength: 6,
    },

    // Whether the user has verified their email address
    isVerified: {
      type: Boolean,
      default: false,
    },

    // Token sent via email to confirm the account
    verificationToken: {
      type: String,
      default: null,
    },

    // Token for resetting a forgotten password
    resetPasswordToken: {
      type: String,
      default: null,
    },

    // Expiry date for the password reset token (1 hour window)
    resetPasswordExpires: {
      type: Date,
      default: null,
    },
    // Role-based access control
    role: {
      type: String,
      enum: ['user', 'admin'],
      default: 'user',
    },
  },
  {
    // Automatically adds createdAt and updatedAt fields
    timestamps: true,
  }
);

module.exports = mongoose.model('User', userSchema);
