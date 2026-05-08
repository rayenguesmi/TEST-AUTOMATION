const nodemailer = require('nodemailer');

/**
 * Creates a reusable transporter using Gmail SMTP.
 * For production, consider using a dedicated email service (SendGrid, Resend, etc.)
 */
const createTransporter = () => {
  return nodemailer.createTransport({
    host: 'smtp.gmail.com',
    port: 465,
    secure: true, // true for 465 (SSL)
    auth: {
      user: process.env.EMAIL_USER.toLowerCase(),
      pass: process.env.EMAIL_PASS.replace(/\s+/g, ''), // Remove any spaces
    },
  });
};

/**
 * Sends an email using Nodemailer.
 * @param {Object} options
 * @param {string} options.to      - Recipient email address
 * @param {string} options.subject - Email subject line
 * @param {string} options.html    - HTML body content
 */
const sendEmail = async ({ to, subject, html }) => {
  const transporter = createTransporter();

  const mailOptions = {
    from: `"User Auth App" <${process.env.EMAIL_USER}>`,
    to,
    subject,
    html,
  };

  await transporter.sendMail(mailOptions);
};

/**
 * Builds and sends the email verification message.
 * @param {string} to    - Recipient email
 * @param {string} token - The verification token stored in the DB
 */
const sendVerificationEmail = async (to, token) => {
  const baseUrl = process.env.SERVER_URL || 'http://127.0.0.1:5000';
  const verificationUrl = `${baseUrl}/api/auth/verify-email?token=${token}`.trim();

  await sendEmail({
    to,
    subject: 'Vérifiez votre compte AUTOTEST',
    html: `
      <div style="font-family: sans-serif; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
        <h2 style="color: #4F46E5;">Bienvenue sur AUTOTEST</h2>
        <p>Merci de vous être inscrit. Pour activer votre compte, veuillez cliquer sur le bouton ci-dessous :</p>
        <div style="margin: 30px 0;">
          <a href="${verificationUrl}" 
             style="background-color: #4F46E5; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">
            ACTIVER MON COMPTE
          </a>
        </div>
        <p style="font-size: 12px; color: #666;">Si le bouton ne fonctionne pas, copiez ce lien :</p>
        <p style="font-size: 12px; color: #4F46E5;">${verificationUrl}</p>
      </div>
    `,
  });
};

/**
 * Builds and sends the password reset email.
 * The link points to the React frontend route /reset-password.
 * @param {string} to    - Recipient email
 * @param {string} token - The reset token stored in the DB
 */
const sendPasswordResetEmail = async (to, token) => {
  const resetUrl = `${process.env.CLIENT_URL}/reset-password?token=${token}`;

  await sendEmail({
    to,
    subject: 'Reset your password',
    html: `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #333;">Reset Your Password</h2>
        <p>You requested a password reset. Click the button below to choose a new password.</p>
        <a
          href="${resetUrl}"
          style="display:inline-block;padding:12px 24px;background:#EF4444;color:#fff;text-decoration:none;border-radius:6px;margin:16px 0;"
        >
          Reset Password
        </a>
        <p style="color:#666;font-size:14px;">Or copy and paste this link in your browser:</p>
        <p style="color:#EF4444;font-size:14px;">${resetUrl}</p>
        <p style="color:#999;font-size:12px;">This link will expire in 1 hour. If you did not request this, ignore this email.</p>
      </div>
    `,
  });
};

module.exports = { sendEmail, sendVerificationEmail, sendPasswordResetEmail };
