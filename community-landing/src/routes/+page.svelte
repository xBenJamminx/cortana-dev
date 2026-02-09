<script lang="ts">
	import { onMount } from 'svelte';

	let openFaq = $state<number | null>(null);
	let mounted = $state(false);

	function toggleFaq(index: number) {
		openFaq = openFaq === index ? null : index;
	}

	onMount(() => {
		mounted = true;
		const observer = new IntersectionObserver(
			(entries) => {
				entries.forEach((entry) => {
					if (entry.isIntersecting) entry.target.classList.add('visible');
				});
			},
			{ threshold: 0.1 }
		);
		document.querySelectorAll('.reveal').forEach((el) => observer.observe(el));
		return () => observer.disconnect();
	});

	const faqs = [
		{
			q: 'Is this a course?',
			a: "No. It's a growing library of resources plus a community. No curriculum, no timeline, no homework. You get everything the moment you join, and new content is added every week."
		},
		{
			q: 'How is this different from free AI content on YouTube or Twitter?',
			a: 'Free content shows you the concept. This gives you the execution: the actual prompts, step-by-step tutorials, and people to ask when you get stuck. Free content teaches the "what." This gives you the "how."'
		},
		{
			q: 'Do I need to be technical?',
			a: "No. Most of the content is designed for people who are not developers. If you can use a web browser and copy-paste a prompt, you can use everything in here. Advanced resources exist for people who want to go deeper, but they're not the focus."
		},
		{
			q: "What if I'm not sure it's worth $29/mo?",
			a: "The prompt packs alone sell for $9-$29 each on their own. The tool deals are designed to offset your membership cost entirely. Everything added after you join is included at no extra cost. The library only gets more valuable over time."
		},
		{
			q: 'Can I cancel anytime?',
			a: 'Yes. Monthly billing. No contracts. Founding member pricing is locked as long as you stay subscribed. If you cancel and come back later, you rejoin at whatever the current price is.'
		},
		{
			q: "Who runs this?",
			a: "BuildsByBen is run by Ben, a technical program manager and AI automation consultant who uses AI across client work, side projects, and family life. New resources are added weekly and the community includes weekly calls, dedicated channels, and a growing resource library."
		}
	];
</script>

<svelte:head>
	<title>BuildsByBen — Learn AI. Use it everywhere.</title>
</svelte:head>

<!-- Nav -->
<nav class="fixed top-0 z-50 w-full border-b-4 border-ink bg-bg/90 backdrop-blur-md">
	<div class="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
		<span class="font-display text-2xl font-black uppercase tracking-tight text-ink">BuildsByBen</span>
		<a href="#founding" class="neo-btn rounded-lg bg-cyan px-5 py-2.5 text-sm text-ink">
			Join Now
		</a>
	</div>
</nav>

<!-- ============================================ -->
<!-- HERO -->
<!-- ============================================ -->
<section class="relative overflow-hidden pt-28 pb-12 md:pt-40 md:pb-20">
	<!-- Floating geometric shapes -->
	<div class="geo-shape hidden h-16 w-16 rotate-12 rounded-lg bg-cyan-light md:block" style="top: 120px; right: 8%;"></div>
	<div class="geo-shape hidden h-10 w-10 -rotate-6 rounded-md bg-yellow-light md:block" style="top: 200px; right: 15%;"></div>
	<div class="geo-shape hidden h-12 w-12 rotate-45 bg-pink-light md:block" style="top: 300px; right: 5%;"></div>
	<div class="geo-shape hidden h-8 w-8 rotate-12 rounded-sm bg-green-light md:block" style="bottom: 60px; left: 5%;"></div>
	<div class="geo-shape hidden h-14 w-14 -rotate-12 rounded-lg bg-yellow-light md:block" style="bottom: 40px; right: 12%;"></div>

	<div class="relative z-10 mx-auto max-w-5xl px-6">
		<div class="grid items-center gap-8 md:gap-10 md:grid-cols-2">
			<div>
				<div class="{mounted ? 'reveal visible' : 'opacity-0'}">
					<div class="mb-6 inline-block -rotate-1 rounded-lg border-4 border-ink bg-cyan px-4 py-1.5 font-mono text-xs font-bold uppercase tracking-wider text-ink shadow-[4px_4px_0_#000]">
						AI for everyday people
					</div>
				</div>

				<h1 class="{mounted ? 'reveal visible' : 'opacity-0'} font-display text-3xl font-black leading-[1.05] text-ink sm:text-4xl md:text-6xl lg:text-7xl">
					Learn AI.<br />Use it everywhere.
				</h1>

				<p class="{mounted ? 'reveal visible' : 'opacity-0'} mt-5 max-w-md text-base leading-relaxed text-muted md:mt-6 md:text-lg">
					Tutorials, workflows, tool recommendations, templates, and weekly calls. Everything you need to actually use AI in your work, your side projects, and your life. Not theory. The actual how.
				</p>

				<div class="{mounted ? 'reveal visible' : 'opacity-0'} mt-8 flex flex-wrap items-center gap-4">
					<a href="#founding" class="neo-btn w-full justify-center rounded-xl bg-cyan px-7 py-3.5 text-base text-ink sm:w-auto">
						Claim your founding spot &rarr;
					</a>
				</div>
				<span class="{mounted ? 'reveal visible' : 'opacity-0'} mt-3 inline-block font-mono text-xs text-muted sm:text-sm">50 spots &middot; $29/mo locked forever &middot; Price goes to $49 after</span>
			</div>

			<!-- Visual anchor -->
			<div class="{mounted ? 'reveal visible' : 'opacity-0'} relative hidden md:block">
				<div class="relative mx-auto w-full max-w-sm">
					<div class="absolute top-6 left-6 right-0 h-64 rounded-2xl border-4 border-ink bg-yellow-light"></div>
					<div class="absolute top-3 left-3 right-3 h-64 rounded-2xl border-4 border-ink bg-pink-light"></div>
					<div class="relative rounded-2xl border-4 border-ink bg-surface p-6 shadow-[8px_8px_0_#000]">
						<div class="flex items-center gap-3 border-b-2 border-ink/10 pb-4">
							<div class="flex h-10 w-10 items-center justify-center rounded-lg border-3 border-ink bg-cyan-light font-display text-lg font-bold">B</div>
							<div>
								<div class="font-display text-sm font-bold">BuildsByBen Library</div>
								<div class="font-mono text-xs text-muted">Updated today</div>
							</div>
						</div>
						<div class="mt-4 space-y-3">
							<div class="flex items-center gap-2">
								<div class="h-2.5 w-2.5 rounded-full border-2 border-ink bg-cyan"></div>
								<span class="text-sm font-medium">Tutorial: Automate your content pipeline</span>
							</div>
							<div class="flex items-center gap-2">
								<div class="h-2.5 w-2.5 rounded-full border-2 border-ink bg-yellow"></div>
								<span class="text-sm font-medium">Starter kit: AI-powered side project</span>
							</div>
							<div class="flex items-center gap-2">
								<div class="h-2.5 w-2.5 rounded-full border-2 border-ink bg-pink"></div>
								<span class="text-sm font-medium">Guide: The AI tools actually worth paying for</span>
							</div>
							<div class="flex items-center gap-2">
								<div class="h-2.5 w-2.5 rounded-full border-2 border-ink bg-green"></div>
								<span class="text-sm font-medium">Template: Client proposal workflow</span>
							</div>
						</div>
						<div class="mt-4 flex items-center gap-2 rounded-lg border-2 border-ink/10 bg-bg-alt px-3 py-2">
							<span class="font-mono text-xs text-muted">+8 new resources this week</span>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</section>

<!-- Stats row -->
<div class="border-y-4 border-ink bg-surface py-6 md:py-8">
	<div class="mx-auto grid max-w-4xl grid-cols-2 gap-4 px-6 md:grid-cols-4 md:gap-8">
		{#each [
			{ num: '12+', label: 'Tutorials', color: 'text-cyan' },
			{ num: '50+', label: 'Resources', color: 'text-yellow' },
			{ num: 'Weekly', label: 'Live Calls', color: 'text-pink' },
			{ num: '50', label: 'Founding Spots', color: 'text-green' }
		] as stat}
			<div class="reveal text-center">
				<div class="font-display text-3xl font-black {stat.color} md:text-4xl">{stat.num}</div>
				<div class="mt-1 font-mono text-xs font-bold uppercase tracking-wider text-muted">{stat.label}</div>
			</div>
		{/each}
	</div>
</div>

<!-- Scrolling marquee -->
<div class="overflow-hidden border-b-4 border-ink bg-ink py-3.5">
	<div class="animate-marquee flex w-max gap-10 whitespace-nowrap">
		{#each Array(3) as _}
			<span class="font-display text-base font-bold uppercase tracking-wide text-bg">Step-by-Step Tutorials</span>
			<span class="text-cyan">&bull;</span>
			<span class="font-display text-base font-bold uppercase tracking-wide text-bg">Workflow Templates</span>
			<span class="text-cyan">&bull;</span>
			<span class="font-display text-base font-bold uppercase tracking-wide text-bg">Honest Tool Reviews</span>
			<span class="text-cyan">&bull;</span>
			<span class="font-display text-base font-bold uppercase tracking-wide text-bg">Exclusive Deals</span>
			<span class="text-cyan">&bull;</span>
			<span class="font-display text-base font-bold uppercase tracking-wide text-bg">Weekly Live Calls</span>
			<span class="text-cyan">&bull;</span>
			<span class="font-display text-base font-bold uppercase tracking-wide text-bg">Starter Kits</span>
			<span class="text-cyan">&bull;</span>
		{/each}
	</div>
</div>

<!-- ============================================ -->
<!-- PROBLEM / SOLUTION (side by side) -->
<!-- ============================================ -->
<section class="py-14 md:py-28">
	<div class="mx-auto max-w-5xl px-6">
		<div class="reveal">
			<div class="inline-block -rotate-1 rounded-lg border-4 border-ink bg-pink-light px-4 py-1.5 font-mono text-xs font-bold uppercase tracking-wider text-ink shadow-[4px_4px_0_#000]">
				Sound familiar?
			</div>
			<h2 class="mt-6 font-display text-3xl font-bold leading-tight text-ink md:text-5xl">
				You know AI can change your life. You just don't know where to start.
			</h2>
		</div>

		<div class="mt-10 space-y-3 md:mt-12 md:space-y-4">
			{#each [
				{
					problem: '1,000 AI tools. No idea which ones are worth paying for.',
					pain: 'You signed up for 3 different things last month. Used one of them twice. The rest are charging your card for nothing.',
					solution: 'Honest monthly breakdowns of which tools are actually worth it, what they cost, and why. No affiliate links. Plus member-only deals designed to save you more than $29/mo.'
				},
				{
					problem: 'You see what AI can do but can\'t replicate it.',
					pain: 'You watched someone on Twitter automate their entire content pipeline. The thread was 12 tweets of hype and zero details.',
					solution: 'Step-by-step tutorials: "Open this tool. Paste this prompt. Click here." Written for non-technical people. Zero fluff.'
				},
				{
					problem: 'ChatGPT gives you generic, robotic outputs.',
					pain: 'You know the tool is powerful but you\'re clearly not using it right.',
					solution: 'Copy-paste prompt packs for specific tasks: proposals, content, analysis, even family stuff. Each one tells you which model to use and shows example output.'
				},
				{
					problem: 'You get stuck and have nobody to ask.',
					pain: 'Google gives you 2023 answers. Reddit threads end in arguments.',
					solution: 'A private community with dedicated channels for questions, troubleshooting, and sharing wins. Plus weekly calls where topics get covered live.'
				},
				{
					problem: 'No time to figure this out yourself.',
					pain: 'Full-time job. Maybe kids. 45 minutes before you\'re exhausted.',
					solution: 'Prompts you can use in 30 seconds. Tutorials you can finish in one sitting. Skip the research, go straight to results.'
				}
			] as row, i}
				<div class="reveal grid gap-0 md:grid-cols-2" style="transition-delay: {i * 60}ms;">
					<!-- Problem side -->
					<div class="neo-card rounded-t-xl md:rounded-l-xl md:rounded-tr-none border-b-[2px] md:border-b-4 md:border-r-0 bg-surface p-4 md:p-6">
						<div class="mb-1.5 inline-block rounded-md border-2 border-ink/20 bg-pink-light px-2 py-0.5 font-mono text-[0.6rem] font-bold uppercase tracking-wider text-ink/60">Problem</div>
						<p class="text-sm font-semibold text-ink">{row.problem}</p>
						<p class="mt-1 hidden text-sm text-muted md:block">{row.pain}</p>
					</div>
					<!-- Solution side -->
					<div class="neo-card rounded-b-xl md:rounded-r-xl md:rounded-bl-none border-t-0 md:border-t-4 bg-cyan-bg p-4 md:p-6">
						<div class="mb-1.5 inline-block rounded-md border-2 border-ink bg-cyan px-2 py-0.5 font-mono text-[0.6rem] font-bold uppercase tracking-wider">Solution</div>
						<p class="text-sm font-medium leading-relaxed text-ink">{row.solution}</p>
					</div>
				</div>
			{/each}
		</div>

		<div class="reveal mt-10 rounded-2xl border-4 border-ink bg-yellow-bg p-6 text-center shadow-[8px_8px_0_theme(--color-yellow)] md:p-8">
			<p class="font-display text-xl font-bold text-ink md:text-2xl">
				The gap isn't knowledge. It's knowing what to actually do.
			</p>
			<p class="mt-2 text-muted">
				You don't need another YouTube video. You need prompts that work, tools that are worth it, tutorials you can follow, and people to ask when you're stuck.
			</p>
			<a href="#founding" class="neo-btn mt-6 inline-flex rounded-xl bg-cyan px-7 py-3 text-sm text-ink">
				Claim your founding spot &rarr;
			</a>
		</div>
	</div>
</section>

<!-- ============================================ -->
<!-- WHO THIS IS FOR (Audience Segments) -->
<!-- ============================================ -->
<section class="py-14 md:py-28">
	<div class="mx-auto max-w-5xl px-6">
		<div class="reveal">
			<div class="inline-block rotate-1 rounded-lg border-4 border-ink bg-cyan-light px-4 py-1.5 font-mono text-xs font-bold uppercase tracking-wider text-ink shadow-[4px_4px_0_#000]">
				Who this is for
			</div>
			<h2 class="mt-6 font-display text-3xl font-bold leading-tight text-ink md:text-5xl">
				Running a business. Building on the side. AI should help with both.
			</h2>
		</div>

		<div class="mt-12 grid gap-5 md:grid-cols-2">
			{#each [
				{
					who: 'Business Owners',
					badge: 'bg-cyan-light',
					shadow: 'neo-card-cyan',
					lines: [
						'You know AI can save you time and money but don\'t know where to start',
						'You\'re tired of hype and want to see what actually works',
						'You need results this week, not a 12-week course',
						'You want honest tool recommendations with no affiliate links or agenda'
					]
				},
				{
					who: 'Side Hustlers',
					badge: 'bg-yellow-light',
					shadow: 'neo-card-yellow',
					lines: [
						'You have a full-time job and something you\'re building on the side',
						'You have limited time and need to move fast without a team',
						'You want proven workflows from people actually doing it solo',
						'You need the shortcut to "what tools do I use and how"'
					]
				}
			] as segment, i}
				<div class="reveal neo-card {segment.shadow} rounded-2xl p-5 md:p-7" style="transition-delay: {i * 80}ms;">
					<span class="inline-block -rotate-1 rounded-lg border-3 border-ink {segment.badge} px-3 py-1 font-mono text-xs font-bold uppercase tracking-wider">{segment.who}</span>
					<ul class="mt-5 space-y-3">
						{#each segment.lines as line}
							<li class="flex gap-2.5 text-sm leading-relaxed">
								<span class="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-md border-2 border-ink bg-surface text-xs font-bold">&#10003;</span>
								{line}
							</li>
						{/each}
					</ul>
				</div>
			{/each}
		</div>
	</div>
</section>

<!-- ============================================ -->
<!-- WHAT YOU GET (Tangible Outputs) -->
<!-- ============================================ -->
<section class="border-y-4 border-ink bg-bg-alt py-14 md:py-28">
	<div class="mx-auto max-w-5xl px-6">
		<div class="reveal">
			<div class="inline-block -rotate-1 rounded-lg border-4 border-ink bg-yellow-light px-4 py-1.5 font-mono text-xs font-bold uppercase tracking-wider text-ink shadow-[4px_4px_0_#000]">
				What's inside
			</div>
			<h2 class="mt-6 font-display text-3xl font-bold text-ink md:text-5xl">
				Not theory. Not courses. Things you can use today.
			</h2>
		</div>

		<div class="mt-12 space-y-5">
			{#each [
				{
					num: '01',
					title: 'Step-by-Step Tutorials',
					desc: 'Full walkthroughs that take you from zero to a working result. Written for non-technical people. Each one covers a real use case you can apply the same day.',
					examples: 'Automate your content pipeline (no code). Write client proposals in 10 minutes. Set up your first AI workflow. Build a custom tool for your family.',
					badge: 'bg-cyan-light',
					shadow: 'neo-card-cyan'
				},
				{
					num: '02',
					title: 'Templates, Workflows & Starter Kits',
					desc: 'Ready-to-use templates for common tasks. Automation workflows you can import and run. Starter kits that give you a head start on projects instead of starting from scratch.',
					examples: 'Content pipeline templates. Client onboarding workflows. AI-powered email sequences. Side project starter kits. Prompt libraries organized by use case.',
					badge: 'bg-yellow-light',
					shadow: 'neo-card-yellow'
				},
				{
					num: '03',
					title: 'Honest Tool Breakdowns',
					desc: 'Monthly roundups of which AI tools are actually worth paying for, what they cost, and honest verdicts. No affiliate links. No sponsorships. Just what works and what doesn\'t, tested across real work and real projects.',
					examples: 'The AI tools actually worth paying for (and the monthly damage). Best free tools for small business. When to use Claude vs ChatGPT vs Gemini. Tool deals that offset your membership.',
					badge: 'bg-pink-light',
					shadow: 'neo-card-pink'
				},
				{
					num: '04',
					title: 'Weekly Calls + Private Community',
					desc: 'Weekly community calls covering specific AI topics, live walkthroughs, and Q&amp;A. Dedicated channels for questions, wins, and troubleshooting. New resources added every week.',
					examples: 'Weekly topic-based calls (recorded). Help channel for questions. Wins channel to share what you built. All session recordings archived.',
					badge: 'bg-cyan-light',
					shadow: 'neo-card-cyan'
				},
				{
					num: '05',
					title: 'Exclusive Tool Deals',
					desc: 'Discounts negotiated with AI tool companies, exclusively for members. The goal: the deals alone save you more than the $29/mo membership. Everything else is free upside.',
					examples: 'Discounts on recommended tools. Lifetime deal alerts before they go public. Partner pricing on AI platforms.',
					badge: 'bg-yellow-light',
					shadow: 'neo-card-yellow'
				},
				{
					num: '06',
					title: 'The Full Stack (For Builders)',
					desc: 'For members who want to go deeper: the tech, the content strategy, and the launch playbook. How to go from idea to live product using AI as your unfair advantage.',
					examples: 'Automation workflow templates. Technical deep-dives. Content and social media strategies. Launch checklists. Code walkthroughs from real products.',
					badge: 'bg-pink-light',
					shadow: 'neo-card-pink'
				}
			] as feature, i}
				<div class="reveal neo-card {feature.shadow} rounded-2xl p-5 md:p-8" style="transition-delay: {i * 40}ms;">
					<div class="flex flex-col gap-4 md:flex-row md:items-start md:gap-6">
						<span class="inline-flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border-4 border-ink {feature.badge} font-mono text-sm font-black">{feature.num}</span>
						<div class="flex-1">
							<h3 class="font-display text-xl font-bold text-ink">{feature.title}</h3>
							<p class="mt-2 text-[0.95rem] leading-relaxed text-muted">{feature.desc}</p>
							<p class="mt-3 rounded-lg border-2 border-ink/10 bg-bg-alt px-4 py-3 font-mono text-xs leading-relaxed text-muted">
								<span class="font-bold text-ink">Examples:</span> {feature.examples}
							</p>
						</div>
					</div>
				</div>
			{/each}
		</div>
	</div>
</section>

<!-- Mid-page CTA 2 -->
<div class="border-b-4 border-ink bg-cyan-bg py-10 text-center">
	<div class="reveal mx-auto max-w-2xl px-6">
		<p class="font-display text-xl font-bold text-ink md:text-2xl">Everything above. $29/mo. Cancel anytime.</p>
		<a href="#founding" class="neo-btn mt-5 inline-flex rounded-xl bg-yellow px-7 py-3 text-sm text-ink">
			Lock in founding pricing &rarr;
		</a>
	</div>
</div>

<!-- ============================================ -->
<!-- BUILT FROM REAL WORK -->
<!-- ============================================ -->
<section class="relative overflow-hidden py-14 md:py-28">
	<!-- Floating shapes -->
	<div class="geo-shape hidden h-10 w-10 rotate-12 rounded-md bg-pink-light md:block" style="top: 80px; right: 8%;"></div>
	<div class="geo-shape hidden h-8 w-8 -rotate-6 bg-cyan-light md:block" style="bottom: 100px; left: 6%;"></div>

	<div class="relative z-10 mx-auto max-w-4xl px-6">
		<div class="reveal">
			<div class="inline-block rotate-1 rounded-lg border-4 border-ink bg-green-light px-4 py-1.5 font-mono text-xs font-bold uppercase tracking-wider text-ink shadow-[4px_4px_0_#000]">
				Built by
			</div>
			<h2 class="mt-6 font-display text-3xl font-bold text-ink md:text-5xl">
				Built from real work, not theory.
			</h2>
		</div>

		<div class="reveal mt-10 rounded-2xl border-4 border-ink bg-surface p-6 shadow-[8px_8px_0_theme(--color-cyan)] md:p-12">
			<p class="text-base leading-relaxed text-ink md:text-xl">
				Everything in this community comes from hands-on experience. AI automation for enterprise clients. Consumer products used by thousands. Side projects built on nights and weekends. Even a bedtime story generator for the kids.
			</p>
			<p class="mt-4 font-display text-xl font-bold text-ink md:mt-6 md:text-3xl">The resources reflect that range.</p>
			<p class="mt-4 text-muted leading-relaxed">
				From business operations to content creation to family life. The tutorials, prompts, and tool recommendations cover AI use cases most communities don't touch because they only focus on one niche.
			</p>
		</div>

		<div class="mt-6 grid grid-cols-2 gap-4 md:grid-cols-4 md:gap-5">
			{#each [
				{ label: 'Work', text: 'AI for proposals, client delivery, meeting notes, competitive analysis, and saving hours every week.', color: 'bg-cyan-light', shadow: 'neo-card-cyan' },
				{ label: 'Building', text: 'Tutorials on shipping products, automating workflows, and using AI as a solo builder.', color: 'bg-yellow-light', shadow: 'neo-card-yellow' },
				{ label: 'Life', text: 'Prompts for family stuff, meal planning, learning tools, creative projects. AI beyond work.', color: 'bg-pink-light', shadow: 'neo-card-pink' },
				{ label: 'Tools', text: 'Honest breakdowns of what to pay for, what to skip, and deals that save you money.', color: 'bg-green-light', shadow: 'neo-card' }
			] as card, i}
				<div class="reveal neo-card {card.shadow} rounded-xl p-5" style="transition-delay: {i * 60}ms;">
					<span class="inline-block -rotate-2 rounded-md border-2 border-ink {card.color} px-2.5 py-0.5 font-mono text-[0.65rem] font-bold uppercase tracking-wider">{card.label}</span>
					<p class="mt-3 text-sm leading-relaxed text-muted">{card.text}</p>
				</div>
			{/each}
		</div>

		<p class="reveal mt-8 text-center text-muted">
			Not "AI for marketing" or "AI for devs." <span class="font-semibold text-ink">AI for your whole life.</span> That range is what makes this different.
		</p>
	</div>
</section>


<!-- ============================================ -->
<!-- FOUNDING MEMBERS -->
<!-- ============================================ -->
<section id="founding" class="relative overflow-hidden border-b-4 border-ink bg-ink py-14 md:py-28">
	<!-- Floating shapes on dark bg -->
	<div class="geo-shape hidden h-12 w-12 rotate-12 rounded-lg border-bg/30 bg-cyan/20 md:block" style="top: 100px; left: 5%;"></div>
	<div class="geo-shape hidden h-8 w-8 -rotate-6 border-bg/30 bg-yellow/20 md:block" style="bottom: 120px; right: 8%;"></div>

	<div class="relative z-10 mx-auto max-w-4xl px-6">
		<div class="reveal text-center">
			<div class="mx-auto inline-block -rotate-1 rounded-lg border-4 border-bg bg-yellow px-4 py-1.5 font-mono text-xs font-bold uppercase tracking-wider text-ink shadow-[4px_4px_0_theme(--color-cyan)]">
				Limited availability
			</div>
			<h2 class="mt-6 font-display text-3xl font-bold text-bg md:text-5xl">
				50 founding spots. $29/mo. Locked forever.
			</h2>
			<p class="mt-4 text-base text-bg/60 md:text-lg">
				The first 50 members lock in $29/mo permanently. After that, the price goes to $49/mo and never comes back down.
			</p>
		</div>

		<div class="mt-12 grid items-start gap-8 md:grid-cols-2">
			<!-- Pricing card -->
			<div class="reveal">
				<div class="rounded-2xl border-4 border-bg bg-surface shadow-[8px_8px_0_theme(--color-cyan)]">
					<div class="border-b-4 border-ink bg-cyan px-6 py-5 rounded-t-[12px] md:px-8 md:py-6">
						<span class="font-mono text-sm font-bold uppercase tracking-widest text-ink">Founding Member</span>
						<div class="mt-3 flex items-baseline justify-center gap-1">
							<span class="font-display text-5xl font-black text-ink md:text-6xl">$29</span>
							<span class="text-xl text-ink/60">/mo</span>
						</div>
						<p class="mt-1 text-sm text-ink/60">Standard price: <span class="line-through">$49/mo</span></p>
					</div>

					<div class="px-6 py-6 md:px-8 md:py-8">
						<ul class="space-y-3 text-left text-sm">
							{#each [
								'Full library: tutorials, templates, workflows, tool guides',
								'Permanent price lock at $29/mo',
								'Weekly community calls + private channels',
								'Starter kits and automation templates',
								'Exclusive tool deals and partner discounts',
								'Founding member badge + input on what gets built',
								'Early access to all future products'
							] as perk}
								<li class="flex gap-3">
									<span class="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-md border-2 border-ink bg-cyan-light text-xs font-bold">&#10003;</span>
									{perk}
								</li>
							{/each}
						</ul>

						<a
							href="#founding"
							class="neo-btn mt-8 w-full justify-center rounded-xl bg-yellow px-6 py-4 text-base text-ink"
						>
							Claim your founding spot &rarr;
						</a>
						<p class="mt-4 text-center text-xs text-muted">Cancel anytime. No contracts.</p>
					</div>
				</div>
			</div>

			<!-- Why now -->
			<div class="reveal space-y-5" style="transition-delay: 100ms;">
				<div class="neo-card neo-card-cyan rounded-xl p-6">
					<h4 class="font-display text-lg font-bold text-ink">Price lock is permanent</h4>
					<p class="mt-2 text-sm text-muted">The $29/mo rate is locked as long as you stay subscribed. If you cancel and come back later, you pay whatever the current price is. There's no way to get the founding rate back.</p>
				</div>
				<div class="neo-card neo-card-yellow rounded-xl p-6">
					<h4 class="font-display text-lg font-bold text-ink">The library only gets bigger</h4>
					<p class="mt-2 text-sm text-muted">New tutorials, prompts, and tool guides are added every week. The value compounds. Your price stays the same.</p>
				</div>
				<div class="neo-card neo-card-pink rounded-xl p-6">
					<h4 class="font-display text-lg font-bold text-ink">Tool deals offset the cost</h4>
					<p class="mt-2 text-sm text-muted">Exclusive discounts negotiated with AI tool companies. The goal is for the deals alone to save you more than $29/mo. Everything else is free upside.</p>
				</div>
			</div>
		</div>
	</div>
</section>

<!-- ============================================ -->
<!-- FAQ -->
<!-- ============================================ -->
<section class="py-14 md:py-28">
	<div class="mx-auto max-w-2xl px-6">
		<div class="reveal">
			<h2 class="font-display text-3xl font-bold text-ink md:text-4xl">Questions</h2>
		</div>

		<div class="mt-10 space-y-3">
			{#each faqs as faq, i}
				<div class="reveal" style="transition-delay: {i * 50}ms;">
					<button
						onclick={() => toggleFaq(i)}
						class="neo-card w-full rounded-xl px-6 py-5 text-left {openFaq === i ? 'bg-cyan-light' : ''}"
					>
						<div class="flex items-center justify-between">
							<span class="font-semibold text-ink">{faq.q}</span>
							<span class="ml-4 flex h-7 w-7 shrink-0 items-center justify-center rounded-md border-2 border-ink text-sm font-bold transition-all {openFaq === i ? 'rotate-45 bg-cyan' : 'bg-surface'}">+</span>
						</div>
					</button>
					<div class="faq-content {openFaq === i ? 'open' : ''}">
						<div>
							<p class="px-6 pt-3 pb-5 text-sm leading-relaxed text-muted">{faq.a}</p>
						</div>
					</div>
				</div>
			{/each}
		</div>
	</div>
</section>

<!-- ============================================ -->
<!-- FINAL CTA -->
<!-- ============================================ -->
<section class="border-t-4 border-ink bg-cyan-bg py-14 md:py-28">
	<div class="mx-auto max-w-3xl px-6 text-center">
		<div class="reveal">
			<h2 class="font-display text-3xl font-bold text-ink md:text-5xl">
				Learn AI. Use it everywhere.
			</h2>
			<p class="mt-4 text-base text-muted md:text-lg">
				50 founding spots. Tutorials, templates, tool deals, weekly calls, and a private community. $29/mo locked forever.
			</p>
			<a
				href="#founding"
				class="neo-btn mt-10 inline-flex rounded-xl bg-cyan px-8 py-4 text-base text-ink"
			>
				Claim your founding spot &rarr;
			</a>
			<p class="mt-4 font-mono text-xs text-muted">Cancel anytime. No contracts. Price goes to $49/mo after 50 members.</p>
		</div>
	</div>
</section>

<!-- Footer -->
<footer class="border-t-4 border-ink py-8">
	<div class="mx-auto flex max-w-6xl flex-col items-center gap-4 px-6 text-sm text-muted md:flex-row md:justify-between">
		<span class="font-bold text-ink">BuildsByBen &copy; {new Date().getFullYear()}</span>
		<div class="flex gap-6">
			<a href="https://x.com/xBenJamminx" target="_blank" rel="noopener" class="font-medium transition-colors hover:text-ink">X / Twitter</a>
			<a href="https://buildsbyben.com" target="_blank" rel="noopener" class="font-medium transition-colors hover:text-ink">Portfolio</a>
			<a href="https://github.com/xBenJamminx" target="_blank" rel="noopener" class="font-medium transition-colors hover:text-ink">GitHub</a>
		</div>
	</div>
</footer>
