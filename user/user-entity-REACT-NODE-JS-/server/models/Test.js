const mongoose = require('mongoose');

const testSchema = new mongoose.Schema(
  {
    ownerId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: true,
    },
    targetUrl: { type: String, required: true },
    analysisType: {
      type: String,
      enum: ['Génération de script', 'Exécution'],
      required: true,
    },
    userSpecs: { type: String, default: '' },
    llmEngine: {
      type: String,
      enum: ['groq', 'ollama', null],
      default: null,
    },
    fastApiTaskId: { type: String, default: null },
    status: {
      type: String,
      enum: ['pending', 'running', 'completed', 'failed'],
      default: 'pending',
    },
    report: { type: Object, default: null },
    reportHtmlUrl: { type: String, default: null },
    generatedScript: { type: String, default: null },
    // Derived from report.tests on webhook — grouped by functional area
    features: [
      {
        featureId: String,
        name: String,
        status: { type: String, enum: ['PASS', 'FAIL', 'PARTIAL'] },
        passed: { type: Number, default: 0 },
        total: { type: Number, default: 0 },
        testCases: [{ name: String, statut: String, duration: Number }],
      },
    ],
    stepTimings: { type: Object, default: {} },
    screenshots: [
      {
        url: String,
        timestamp: { type: Date, default: Date.now },
      },
    ],
    logs: [
      {
        message: String,
        level: { type: String, enum: ['info', 'error', 'warning'], default: 'info' },
        timestamp: { type: Date, default: Date.now },
      },
    ],
  },
  { timestamps: true }
);

module.exports = mongoose.model('Test', testSchema);
