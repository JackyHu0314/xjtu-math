// POST /api/feedback：读者补充某份资料的班型、学期、任课等信息。
// 不需要登录；按 IP（哈希后）限流，数据存 D1，维护者审核后再写进资料表。

const LIMIT_PER_HOUR = 20;
const MAX = { path: 300, title: 200, cls: 20, term: 40, teacher: 40, note: 500 };
const CLASSES = ['', '数学大类', '强基', '数学试验班', '几个班共用', '不确定'];

const json = (data, status = 200) =>
	new Response(JSON.stringify(data), { status, headers: { 'content-type': 'application/json; charset=utf-8' } });

async function sha256(text) {
	const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
	return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, '0')).join('');
}

export async function onRequestPost({ request, env }) {
	let body;
	try {
		body = await request.json();
	} catch {
		return json({ ok: false, error: '格式不对' }, 400);
	}
	const v = {};
	for (const [k, max] of Object.entries(MAX)) {
		v[k] = String(body?.[k] ?? '').trim().slice(0, max);
	}
	if (!v.path) return json({ ok: false, error: '缺少资料' }, 400);
	if (!CLASSES.includes(v.cls)) return json({ ok: false, error: '班型不对' }, 400);
	if (!v.cls && !v.term && !v.teacher && !v.note) return json({ ok: false, error: '至少填一项' }, 400);

	// 只存 IP 的哈希，用来限流，不保存原始 IP
	const ip = request.headers.get('cf-connecting-ip') || '';
	const ipHash = (await sha256('xjtu-math:' + ip)).slice(0, 32);
	const now = Date.now();
	const { n } = await env.DB.prepare('SELECT COUNT(*) AS n FROM feedback WHERE ip_hash = ? AND created > ?')
		.bind(ipHash, now - 3600_000)
		.first();
	if (n >= LIMIT_PER_HOUR) return json({ ok: false, error: '提交太频繁，请稍后再试' }, 429);

	await env.DB.prepare(
		'INSERT INTO feedback (path, title, cls, term, teacher, note, ip_hash, created) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
	)
		.bind(v.path, v.title, v.cls, v.term, v.teacher, v.note, ipHash, now)
		.run();
	return json({ ok: true });
}

export const onRequest = () => json({ ok: false, error: '只接受 POST' }, 405);
