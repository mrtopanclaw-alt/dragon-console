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

  // skill name from query param
  const skillName = req.query?.skill || '';
  const skills = {
    web: '🌐 網頁搜索技能啟動',
    term: '💻 終端命令技能啟動',
    file: '📁 文件操作技能啟動',
    code: '🤖 代碼技能啟動',
    browser: '🌍 瀏覽器技能啟動',
    delegate: '👥 委派任務技能啟動'
  };

  const msg = skills[skillName] || '未知技能';

  return res.status(200).json({ skill: skillName, message: msg, done: true });
}
