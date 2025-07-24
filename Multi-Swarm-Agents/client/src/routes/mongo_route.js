// // pages/api/test-connect.js
// import connect from '../lib/mongo';

// export default async function handler(req, res) {
//   try {
//     await connect(); // This connects to MongoDB
//     res.status(200).json({ message: 'Connected to MongoDB' });
//   } catch (error) {
//     res.status(500).json({ error: 'Connection failed', details: error.message });
//   }
// }
