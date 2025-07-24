// app/api/signup/route.js
import connect from '@/lib/mongo';
import User from '@/models/User';

export async function POST(request) {
  try {
    // Connect to MongoDB
    await connect();

    // Parse the JSON body from the request
    const { wallet } = await request.json();
    if (!wallet) {
      return new Response(
        JSON.stringify({ error: 'Wallet address is required' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    // Generate a random nonce for future signature verification
    const nonce = Math.floor(Math.random() * 1000000).toString();

    // Create a new user document using the Mongoose User model
    const newUser = await User.create({ wallet, nonce });

    // Log the new user details on the server console
    console.log('User registered:', newUser);

    // Return a successful JSON response
    return new Response(
      JSON.stringify({
        message: 'User registered successfully',
        user: newUser,
      }),
      { status: 201, headers: { 'Content-Type': 'application/json' } }
    );
  } catch (error) {
    console.error('Registration error:', error);
    return new Response(
      JSON.stringify({ error: 'Registration failed', details: error.message }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
}
