// app/api/server/route.js
import connect from '@/lib/mongo';

export async function GET() {
  try {
    await connect(); // Connect to MongoDB
    return new Response(JSON.stringify({ message: 'Connected to MongoDB' }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: 'Connection failed', details: error.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}
