// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

// https://astro.build/config
export default defineConfig({
	markdown: {
		remarkPlugins: [remarkMath],
		rehypePlugins: [rehypeKatex],
	},
	integrations: [
		starlight({
			title: '西交数学资料站',
			description: '西安交通大学数学与统计学院往年试卷、复习资料、培养方案',
			defaultLocale: 'root',
			locales: { root: { label: '简体中文', lang: 'zh-CN' } },
			customCss: ['katex/dist/katex.min.css', './src/styles/custom.css'],
			lastUpdated: true,
			tableOfContents: false,
			// 第一版不让搜索引擎收录，只有拿到链接的人能看到
			head: [{ tag: 'meta', attrs: { name: 'robots', content: 'noindex, nofollow' } }],
			sidebar: [
				{ label: '开始', items: [{ label: '首页', link: '/' }, { slug: 'guide/about' }, { slug: 'guide/wanted' }, { slug: 'guide/contribute' }] },
				{ label: '培养方案', items: [{ autogenerate: { directory: 'plans' } }] },
				{ label: '大类基础课', items: [{ autogenerate: { directory: 'courses/foundation' } }] },
				{ label: '专业大类基础课', items: [{ autogenerate: { directory: 'courses/major-basic' } }] },
				{ label: '数学与应用数学 · 核心课', collapsed: true, items: [{ autogenerate: { directory: 'courses/math' } }] },
				{ label: '信息与计算科学 · 核心课', collapsed: true, items: [{ autogenerate: { directory: 'courses/icm' } }] },
				{ label: '统计学 · 核心课', collapsed: true, items: [{ autogenerate: { directory: 'courses/stat' } }] },
				{ label: '其他课程', collapsed: true, items: [{ autogenerate: { directory: 'courses/other' } }] },
				{ label: '课外', collapsed: true, items: [{ autogenerate: { directory: 'more' } }] },
			],
		}),
	],
});
