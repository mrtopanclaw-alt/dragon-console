export default function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { password } = req.body || {};
  const GAME_PASSWORD = process.env.GAME_PASSWORD || 'dragon123';

  if (!password || password !== GAME_PASSWORD) {
    return res.status(401).json({ error: 'Invalid password' });
  }

  // Simple token: base64 of timestamp|password
  const token = Buffer.from(`${Date.now()}|${GAME_PASSWORD}`).toString('base64');

  res.setHeader('Set-Cookie', `dragon_token=${token}; Path=/; HttpOnly; SameSite=Strict; Max-Age=86400`);
  res.setHeader('Access-Control-Allow-Origin', 'https://dragon-game.vercel.app');
  res.setHeader('Access-Control-Allow-Credentials', 'true');

  return res.status(200).json({ ok: true });
}
