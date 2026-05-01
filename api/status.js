export default function handler(req, res) {
  const token = req.cookies?.dragon_token;
  const GAME_PASSWORD = process.env.GAME_PASSWORD || 'dragon123';

  if (!token) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  try {
    const decoded = Buffer.from(token, 'base64').toString();
    const [ts, pwd] = decoded.split('|');
    const age = Date.now() - parseInt(ts);
    if (pwd !== GAME_PASSWORD || age > 86400000) {
      return res.status(401).json({ error: 'Unauthorized' });
    }
  } catch {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  return res.status(200).json({
    hp: 80,
    ap: 60,
    status: '待命中',
    dragon: '🐉 黑龍',
    online: true
  });
}
