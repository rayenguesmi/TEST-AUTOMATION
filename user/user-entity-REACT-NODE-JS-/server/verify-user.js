require('dotenv').config();
const mongoose = require('mongoose');
const User = require('./models/User');

const EMAIL = 'rayen1@gmail.com';

mongoose.connect(process.env.MONGO_URI).then(async () => {
  const result = await User.updateOne({ email: EMAIL }, { isVerified: true });
  if (result.matchedCount === 0) {
    console.log(`❌ Utilisateur "${EMAIL}" introuvable en base.`);
  } else {
    console.log(`✅ Utilisateur "${EMAIL}" marqué comme vérifié !`);
  }
  await mongoose.disconnect();
  process.exit(0);
}).catch(err => {
  console.error('❌ Connexion MongoDB échouée :', err.message);
  process.exit(1);
});
