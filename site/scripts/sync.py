"""从「资料库/资料」和「资料库/培养方案/专业课程.csv」生成网站数据。

用法（在 site 目录下）：  python3 scripts/sync.py
- 生成 src/data/resources.json（每门课的资料列表）和 src/data/plans.json（各专业课表）
- 课程页 src/content/docs/courses/**.mdx 不存在时才创建，已有的页面不会覆盖（可以放心手写内容）
- 在 public/files 下为可公开的资料目录建立符号链接，方便本地预览（不提交到 git）
"""
import csv, json, os, re
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
ROOT = SITE.parent
DATA_DIR = ROOT / '资料'
PLAN_CSV = ROOT / '培养方案' / '专业课程.csv'
PRIVATE = {'参考书_版权所有_不公开'}
SKIP = {'待识别'}

# 课程名 → (侧边栏分组目录, URL slug)
COURSES = {
    '数学分析': ('foundation', 'mathematical-analysis'),
    '高等代数与几何': ('foundation', 'advanced-algebra'),
    '数论': ('foundation', 'number-theory'),
    '常微分方程': ('major-basic', 'ode'),
    '抽象代数': ('major-basic', 'abstract-algebra'),
    '实变函数': ('major-basic', 'real-analysis'),
    '复变函数': ('major-basic', 'complex-analysis'),
    '概率论': ('major-basic', 'probability'),
    '概率论基础': ('major-basic', 'probability-foundations'),
    '数理统计': ('major-basic', 'mathematical-statistics'),
    '泛函分析': ('major-basic', 'functional-analysis'),
    '偏微分方程': ('major-basic', 'pde'),
    '随机过程': ('major-basic', 'stochastic-process'),
    '测度论': ('major-basic', 'measure-theory'),
    '机器学习基础': ('major-basic', 'machine-learning'),
    '拓扑学': ('math', 'topology'),
    '微分几何': ('math', 'differential-geometry'),
    '数值分析': ('math', 'numerical-analysis'),
    '运筹学': ('math', 'operations-research'),
    '偏微分方程数值解法': ('icm', 'numerical-pde'),
    '矩阵分析': ('icm', 'matrix-analysis'),
    '最优化方法': ('icm', 'optimization'),
    '人工智能的算法基础': ('icm', 'ai-algorithms'),
    '现代回归分析': ('stat', 'regression'),
    '非参数统计': ('stat', 'nonparametric'),
    '时间序列分析': ('stat', 'time-series'),
    '多元统计分析': ('stat', 'multivariate'),
    '贝叶斯统计': ('stat', 'bayesian'),
    '解析数论': ('other', 'analytic-number-theory'),
    '数学建模': ('other', 'mathematical-modeling'),
}
ALIAS = {'微分几何与流形': '微分几何'}  # 资料目录名 → 课程页名
TYPE_ORDER = ['真题', '练习题', '讲义与复习']
# 资料信息.csv 的「类型」→ 网站上的分组
KIND = {'期末': '真题', '期中': '真题', '月考': '真题', '习题': '练习题', '模拟': '练习题', '讲义': '讲义与复习', '复习': '讲义与复习'}
FOLDER_KIND = {'试卷与习题': '真题', '复习资料': '讲义与复习', '讲义': '讲义与复习'}


def human(n):
    for u in ['B', 'KB', 'MB', 'GB']:
        if n < 1024:
            return f'{n:.0f} {u}' if u == 'B' else f'{n:.1f} {u}'
        n /= 1024
    return f'{n:.1f} TB'


def year_key(name):
    m = re.findall(r'20\d\d', name)
    return -int(m[0]) if m else 0


def term_label(t):
    """2025-2026-2 → 25–26 春；2025-2026-1 → 25–26 秋；2024-2025 → 24–25"""
    m = re.match(r'(\d{4})-(\d{4})(?:-(\d))?$', t or '')
    if not m:
        return ''
    s = f'{m[1][2:]}–{m[2][2:]}'
    return s + {'1': ' 秋', '2': ' 春'}.get(m[3] or '', '')


def load_meta():
    p = DATA_DIR / '资料信息.csv'
    if not p.exists():
        return {}
    with open(p, encoding='utf-8') as fh:
        return {r['路径']: r for r in csv.DictReader(fh)}


def scan():
    res = {}
    meta = load_meta()
    for f in sorted(DATA_DIR.rglob('*')):
        if not f.is_file() or f.name.startswith('.') or f.suffix == '.csv':
            continue
        rel = f.relative_to(DATA_DIR)
        parts = rel.parts
        if parts[0] in PRIVATE:
            course = ALIAS.get(parts[1], parts[1])
            res.setdefault(course, {}).setdefault('books', []).append(f.stem)
            continue
        if any(p in SKIP for p in parts):
            continue
        if parts[0] == '课程':
            course, typ = parts[1], parts[2]
        else:
            course, typ = parts[0].split('/')[0], (parts[1] if len(parts) > 2 else '资料')
        m = meta.get(rel.as_posix(), {})
        typ = KIND.get(m.get('类型', ''), FOLDER_KIND.get(typ, typ))
        item = {
            'name': m.get('标题') or f.stem,
            'ext': f.suffix.lstrip('.').upper(),
            'path': rel.as_posix(),
            'size': human(f.stat().st_size),
            'term': m.get('学年学期', ''),
            'termLabel': term_label(m.get('学年学期', '')),
            'grade': m.get('年级', ''),
            'cls': m.get('班型', ''),
            'teacher': m.get('教师', ''),
            'author': m.get('作者', ''),
            'contributor': m.get('上传人', ''),
            'answer': m.get('答案', '') == '有',
            'note': m.get('备注', ''),
        }
        res.setdefault(course, {}).setdefault(typ, []).append(item)
    for c in res.values():
        for k, v in c.items():
            if k != 'books':
                # 新的在前；没有学期信息的排最后
                v.sort(key=lambda x: (x['term'] == '', [-int(n) for n in re.findall(r'\d+', x['term'])] or [0], x['name']))
    return res


def coverage():
    """每门课每个学年有哪些考试卷，用于「资料征集」页面"""
    meta = load_meta()
    years = [f'{y}-{y + 1}' for y in range(2020, 2026)]
    rows, todo = [], []
    for r in meta.values():
        if '待确认' in r.get('备注', '') or '待识别' in r.get('备注', ''):
            todo.append({'title': r['标题'], 'course': r['课程'], 'note': r['备注']})
    for name, (group, slug) in COURSES.items():
        cells = {y: [] for y in years}
        for r in meta.values():
            if r['课程'] != name or r['类型'] not in ('期末', '期中', '月考'):
                continue
            y = r['学年学期'][:9]
            if y in cells:
                label = r['类型'] + ('（' + r['班型'] + '）' if r['班型'] else '')
                if label not in cells[y]:
                    cells[y].append(label)
        rows.append({'course': name, 'link': f'/courses/{group}/{slug}/', 'cells': [cells[y] for y in years]})
    return {'years': years, 'rows': rows, 'todo': todo}


def plans():
    out = {}
    with open(PLAN_CSV, encoding='utf-8') as fh:
        for r in csv.DictReader(fh):
            slug = COURSES.get(r['课程名称'], (None, None))
            r['link'] = f"/courses/{slug[0]}/{slug[1]}/" if slug[0] else None
            out.setdefault(r['专业'], []).append(r)
    return out


def ensure_course_pages(plan):
    used_by = {}
    for major, rows in plan.items():
        for r in rows:
            used_by.setdefault(r['课程名称'], []).append((major, r))
    for name, (group, slug) in COURSES.items():
        p = SITE / 'src/content/docs/courses' / group / f'{slug}.mdx'
        if p.exists():
            continue
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"""---
title: {name}
---
import CourseMeta from '../../../../components/CourseMeta.astro';
import Resources from '../../../../components/Resources.astro';

<CourseMeta course="{name}" />

<Resources course="{name}" />
""", encoding='utf-8')
        print('新建课程页', p.relative_to(SITE))


def link_public_files():
    pub = SITE / 'public/files'
    pub.mkdir(parents=True, exist_ok=True)
    for d in DATA_DIR.iterdir():
        if d.is_dir() and d.name not in PRIVATE and not d.name.startswith('.'):
            link = pub / d.name
            if not link.exists():
                link.symlink_to(d)


if __name__ == '__main__':
    out = SITE / 'src/data'
    out.mkdir(parents=True, exist_ok=True)
    r, p = scan(), plans()
    (out / 'resources.json').write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
    (out / 'coverage.json').write_text(json.dumps(coverage(), ensure_ascii=False, indent=1), encoding='utf-8')
    (out / 'plans.json').write_text(json.dumps(p, ensure_ascii=False, indent=1), encoding='utf-8')
    ensure_course_pages(p)
    link_public_files()
    n = sum(len(v) for c in r.values() for k, v in c.items() if k != 'books')
    print(f'资料 {n} 个，涉及 {len(r)} 个分类；培养方案 {len(p)} 个专业')
