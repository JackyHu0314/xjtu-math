-- 读者提交的资料信息补充（班型、学期、任课等），由维护者审核后写入 资料/资料信息.csv
CREATE TABLE IF NOT EXISTS feedback (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  path TEXT NOT NULL,
  title TEXT NOT NULL DEFAULT '',
  cls TEXT NOT NULL DEFAULT '',
  term TEXT NOT NULL DEFAULT '',
  teacher TEXT NOT NULL DEFAULT '',
  note TEXT NOT NULL DEFAULT '',
  ip_hash TEXT NOT NULL DEFAULT '',
  status TEXT NOT NULL DEFAULT 'new',
  created INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_feedback_ip_created ON feedback (ip_hash, created);
CREATE INDEX IF NOT EXISTS idx_feedback_status ON feedback (status, created);
