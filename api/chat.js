export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

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

  const { message } = req.body || {};

  if (!message) {
    return res.status(400).json({ error: 'Empty message' });
  }

  // TODO: Connect to Hermes Agent via API
  // For now, echo with a dragon response
  const replies = [
    '🐉 我收到了：「' + message.slice(0, 50) + '」... 讓我想想',
    '⚡ 任務已記錄，我會處理的',
    '💭 收到指令，開始分析...',
    '🐉 好的，這件事我來幫你辦',
  ];
  const reply = replies[Math.floor(Math.random() * replies.length)];

  return res.status(200).json({ reply });
}
