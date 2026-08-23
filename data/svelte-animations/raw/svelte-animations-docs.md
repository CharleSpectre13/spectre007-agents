<!--
Source: Svelte MCP server (get-documentation), fetched 2026-08-23
Sections (in order): svelte/transition, svelte/in-and-out, svelte/animate,
  svelte/svelte-transition, svelte/svelte-animate, svelte/svelte-motion,
  svelte/svelte-easing, svelte/key, svelte/scoped-styles, svelte/global-styles,
  svelte/@attach, svelte/$effect
-->

## transition:

A _transition_ is triggered by an element entering or leaving the DOM as a result of a state change.

When a block (such as an `{#if ...}` block) is transitioning out, all elements inside it, including those that do not have their own transitions, are kept in the DOM until every transition in the block has been completed.

The `transition:` directive indicates a _bidirectional_ transition, which means it can be smoothly reversed while the transition is in progress.

```svelte
<script>
	+++import { fade } from 'svelte/transition';+++

	let visible = $state(false);
</script>

<button onclick={() => visible = !visible}>toggle</button>

{#if visible}
	<div +++transition:fade+++>fades in and out</div>
{/if}
```

## Local vs global

Transitions are local by default. Local transitions only play when the block they belong to is created or destroyed, _not_ when parent blocks are created or destroyed.

```svelte
{#if x}
	{#if y}
		<p transition:fade>fades in and out only when y changes</p>

		<p transition:fade|global>fades in and out when x or y change</p>
	{/if}
{/if}
```

## Built-in transitions

A selection of built-in transitions can be imported from the [`svelte/transition`](svelte-transition) module.

## Transition parameters

Transitions can have parameters.

(The double `{{curlies}}` aren't a special syntax; this is an object literal inside an expression tag.)

```svelte
{#if visible}
	<div transition:fade={{ duration: 2000 }}>fades in and out over two seconds</div>
{/if}
```

## Accessibility

Transitions are driven by the [Web Animations API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Animations_API) rather than by CSS. A global `@media (prefers-reduced-motion: reduce)` rule that zeroes `transition-duration` and `animation-duration` therefore has no effect on them.

Use [`prefersReducedMotion`](svelte-motion#prefersReducedMotion) to adjust (or completely disable) the transition accordingly for devices who request reduced motion.

## Custom transition functions

```js
/// copy: false
// @noErrors
transition = (node: HTMLElement, params: any, options: { direction: 'in' | 'out' | 'both' }) => {
	delay?: number,
	duration?: number,
	easing?: (t: number) => number,
	css?: (t: number, u: number) => string,
	tick?: (t: number, u: number) => void
}
```

Transitions can use custom functions. If the returned object has a `css` function, Svelte will generate keyframes for a [web animation](https://developer.mozilla.org/en-US/docs/Web/API/Web_Animations_API).

The `t` argument passed to `css` is a value between `0` and `1` after the `easing` function has been applied. _In_ transitions run from `0` to `1`, _out_ transitions run from `1` to `0` — in other words, `1` is the element's natural state, as though no transition had been applied. The `u` argument is equal to `1 - t`.

The function is called repeatedly _before_ the transition begins, with different `t` and `u` arguments.

```svelte
<!--- file: App.svelte --->
<script>
	import { elasticOut } from 'svelte/easing';

	/** @type {boolean} */
	export let visible;

	/**
	 * @param {HTMLElement} node
	 * @param {{ delay?: number, duration?: number, easing?: (t: number) => number }} params
	 */
	function whoosh(node, params) {
		const existingTransform = getComputedStyle(node).transform.replace('none', '');

		return {
			delay: params.delay || 0,
			duration: params.duration || 400,
			easing: params.easing || elasticOut,
			css: (t, u) => `transform: ${existingTransform} scale(${t})`
		};
	}
</script>

{#if visible}
	<div in:whoosh>whooshes in</div>
{/if}
```

A custom transition function can also return a `tick` function, which is called _during_ the transition with the same `t` and `u` arguments.

> [!NOTE] If it's possible to use `css` instead of `tick`, do so — web animations can run off the main thread, preventing jank on slower devices.

```svelte
<!--- file: App.svelte --->
<script>
	export let visible = false;

	/**
	 * @param {HTMLElement} node
	 * @param {{ speed?: number }} params
	 */
	function typewriter(node, { speed = 1 }) {
		const valid = node.childNodes.length === 1 && node.childNodes[0].nodeType === Node.TEXT_NODE;

		if (!valid) {
			throw new Error(`This transition only works on elements with a single text node child`);
		}

		const text = node.textContent;
		const duration = text.length / (speed * 0.01);

		return {
			duration,
			tick: (t) => {
				const i = ~~(text.length * t);
				node.textContent = text.slice(0, i);
			}
		};
	}
</script>

{#if visible}
	<p in:typewriter={{ speed: 1 }}>The quick brown fox jumps over the lazy dog</p>
{/if}
```

If a transition returns a function instead of a transition object, the function will be called in the next microtask. This allows multiple transitions to coordinate, making [crossfade effects](/tutorial/deferred-transitions) possible.

Transition functions also receive a third argument, `options`, which contains information about the transition.

Available values in the `options` object are:

- `direction` - one of `in`, `out`, or `both` depending on the type of transition

## Transition events

An element with transitions will dispatch the following events in addition to any standard DOM events:

- `introstart`
- `introend`
- `outrostart`
- `outroend`

```svelte
{#if visible}
	<p
		transition:fly={{ y: 200, duration: 2000 }}
		onintrostart={() => (status = 'intro started')}
		onoutrostart={() => (status = 'outro started')}
		onintroend={() => (status = 'intro ended')}
		onoutroend={() => (status = 'outro ended')}
	>
		Flies in and out
	</p>
{/if}
```

---

## in: and out:

The `in:` and `out:` directives are identical to [`transition:`](transition), except that the resulting transitions are not bidirectional — an `in` transition will continue to 'play' alongside the `out` transition, rather than reversing, if the block is outroed while the transition is in progress. If an out transition is aborted, transitions will restart from scratch.

```svelte
<script>
  import { fade, fly } from 'svelte/transition';

  let visible = $state(false);
</script>

<label>
  <input type="checkbox" bind:checked={visible}>
  visible
</label>

{#if visible}
	<div in:fly={{ y: 200 }} out:fade>flies in, fades out</div>
{/if}
```

---

## animate:

An animation is triggered when the contents of a [keyed each block](each#Keyed-each-blocks) are re-ordered. Animations do not run when an element is added or removed, only when the index of an existing data item within the each block changes. Animate directives must be on an element that is an _immediate_ child of a keyed each block.

Animations can be used with Svelte's [built-in animation functions](svelte-animate) or [custom animation functions](#Custom-animation-functions).

```svelte
<!-- When `list` is reordered the animation will run -->
{#each list as item, index (item)}
	<li animate:flip>{item}</li>
{/each}
```

## Animation Parameters

As with actions and transitions, animations can have parameters.

(The double `{{curlies}}` aren't a special syntax; this is an object literal inside an expression tag.)

```svelte
{#each list as item, index (item)}
	<li animate:flip={{ delay: 500 }}>{item}</li>
{/each}
```

## Custom animation functions

```js
/// copy: false
// @noErrors
animation = (node: HTMLElement, { from: DOMRect, to: DOMRect } , params: any) => {
	delay?: number,
	duration?: number,
	easing?: (t: number) => number,
	css?: (t: number, u: number) => string,
	tick?: (t: number, u: number) => void
}
```

Animations can use custom functions that provide the `node`, an `animation` object and any `parameters` as arguments. The `animation` parameter is an object containing `from` and `to` properties each containing a [DOMRect](https://developer.mozilla.org/en-US/docs/Web/API/DOMRect#Properties) describing the geometry of the element in its `start` and `end` positions. The `from` property is the DOMRect of the element in its starting position, and the `to` property is the DOMRect of the element in its final position after the list has been reordered and the DOM updated.

If the returned object has a `css` method, Svelte will create a [web animation](https://developer.mozilla.org/en-US/docs/Web/API/Web_Animations_API) that plays on the element.

The `t` argument passed to `css` is a value that goes from `0` and `1` after the `easing` function has been applied. The `u` argument is equal to `1 - t`.

The function is called repeatedly _before_ the animation begins, with different `t` and `u` arguments.

<!-- TODO: Types -->

```svelte
<!--- file: App.svelte --->
<script>
	import { cubicOut } from 'svelte/easing';

	/**
	 * @param {HTMLElement} node
	 * @param {{ from: DOMRect; to: DOMRect }} states
	 * @param {any} params
	 */
	function whizz(node, { from, to }, params) {
		const dx = from.left - to.left;
		const dy = from.top - to.top;

		const d = Math.sqrt(dx * dx + dy * dy);

		return {
			delay: 0,
			duration: Math.sqrt(d) * 120,
			easing: cubicOut,
			css: (t, u) => `transform: translate(${u * dx}px, ${u * dy}px) rotate(${t * 360}deg);`
		};
	}
</script>

{#each list as item, index (item)}
	<div animate:whizz>{item}</div>
{/each}
```

A custom animation function can also return a `tick` function, which is called _during_ the animation with the same `t` and `u` arguments.

> [!NOTE] If it's possible to use `css` instead of `tick`, do so — web animations can run off the main thread, preventing jank on slower devices.

```svelte
<!--- file: App.svelte --->
<script>
	import { cubicOut } from 'svelte/easing';

	/**
	 * @param {HTMLElement} node
	 * @param {{ from: DOMRect; to: DOMRect }} states
	 * @param {any} params
	 */
	function whizz(node, { from, to }, params) {
		const dx = from.left - to.left;
		const dy = from.top - to.top;

		const d = Math.sqrt(dx * dx + dy * dy);

		return {
			delay: 0,
			duration: Math.sqrt(d) * 120,
			easing: cubicOut,
			tick: (t, u) => Object.assign(node.style, { color: t > 0.5 ? 'Pink' : 'Blue' })
		};
	}
</script>

{#each list as item, index (item)}
	<div animate:whizz>{item}</div>
{/each}
```

---

## svelte/transition

```js
// @noErrors
import {
	blur,
	crossfade,
	draw,
	fade,
	fly,
	scale,
	slide
} from 'svelte/transition';
```

## blur

Animates a `blur` filter alongside an element's opacity.

<div class="ts-block">

```dts
function blur(
	node: Element,
	{
		delay,
		duration,
		easing,
		amount,
		opacity
	}?: BlurParams | undefined
): TransitionConfig;
```

</div>



## crossfade

The `crossfade` function creates a pair of [transitions](/docs/svelte/transition) called `send` and `receive`. When an element is 'sent', it looks for a corresponding element being 'received', and generates a transition that transforms the element to its counterpart's position and fades it out. When an element is 'received', the reverse happens. If there is no counterpart, the `fallback` transition is used.

<div class="ts-block">

```dts
function crossfade({
	fallback,
	...defaults
}: CrossfadeParams & {
	fallback?: (
		node: Element,
		params: CrossfadeParams,
		intro: boolean
	) => TransitionConfig;
}): [
	(
		node: any,
		params: CrossfadeParams & {
			key: any;
		}
	) => () => TransitionConfig,
	(
		node: any,
		params: CrossfadeParams & {
			key: any;
		}
	) => () => TransitionConfig
];
```

</div>



## draw

Animates the stroke of an SVG element, like a snake in a tube. `in` transitions begin with the path invisible and draw the path to the screen over time. `out` transitions start in a visible state and gradually erase the path. `draw` only works with elements that have a `getTotalLength` method, like `<path>` and `<polyline>`.

<div class="ts-block">

```dts
function draw(
	node: SVGElement & {
		getTotalLength(): number;
	},
	{
		delay,
		speed,
		duration,
		easing
	}?: DrawParams | undefined
): TransitionConfig;
```

</div>



## fade

Animates the opacity of an element from 0 to the current opacity for `in` transitions and from the current opacity to 0 for `out` transitions.

<div class="ts-block">

```dts
function fade(
	node: Element,
	{ delay, duration, easing }?: FadeParams | undefined
): TransitionConfig;
```

</div>



## fly

Animates the x and y positions and the opacity of an element. `in` transitions animate from the provided values, passed as parameters to the element's default values. `out` transitions animate from the element's default values to the provided values.

<div class="ts-block">

```dts
function fly(
	node: Element,
	{
		delay,
		duration,
		easing,
		x,
		y,
		opacity
	}?: FlyParams | undefined
): TransitionConfig;
```

</div>



## scale

Animates the opacity and scale of an element. `in` transitions animate from the provided values, passed as parameters, to an element's current (default) values. `out` transitions animate from an element's default values to the provided values.

<div class="ts-block">

```dts
function scale(
	node: Element,
	{
		delay,
		duration,
		easing,
		start,
		opacity
	}?: ScaleParams | undefined
): TransitionConfig;
```

</div>



## slide

Slides an element in and out.

<div class="ts-block">

```dts
function slide(
	node: Element,
	{
		delay,
		duration,
		easing,
		axis
	}?: SlideParams | undefined
): TransitionConfig;
```

</div>



## BlurParams

<div class="ts-block">

```dts
interface BlurParams {/*…*/}
```

<div class="ts-block-property">

```dts
delay?: number;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
duration?: number;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
easing?: EasingFunction;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
amount?: number | string;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
opacity?: number;
```

<div class="ts-block-property-details"></div>
</div></div>

## CrossfadeParams

<div class="ts-block">

```dts
interface CrossfadeParams {/*…*/}
```

<div class="ts-block-property">

```dts
delay?: number;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
duration?: number | ((len: number) => number);
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
easing?: EasingFunction;
```

<div class="ts-block-property-details"></div>
</div></div>

## DrawParams

<div class="ts-block">

```dts
interface DrawParams {/*…*/}
```

<div class="ts-block-property">

```dts
delay?: number;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
speed?: number;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
duration?: number | ((len: number) => number);
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
easing?: EasingFunction;
```

<div class="ts-block-property-details"></div>
</div></div>

## EasingFunction

<div class="ts-block">

```dts
type EasingFunction = (t: number) => number;
```

</div>

## FadeParams

<div class="ts-block">

```dts
interface FadeParams {/*…*/}
```

<div class="ts-block-property">

```dts
delay?: number;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
duration?: number;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
easing?: EasingFunction;
```

<div class="ts-block-property-details"></div>
</div></div>

## FlyParams

<div class="ts-block">

```dts
interface FlyParams {/*…*/}
```

<div class="ts-block-property">

```dts
delay?: number;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
duration?: number;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
easing?: EasingFunction;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
x?: number | string;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
y?: number | string;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
opacity?: number;
```

<div class="ts-block-property-details"></div>
</div></div>

## ScaleParams

<div class="ts-block">

```dts
interface ScaleParams {/*…*/}
```

<div class="ts-block-property">

```dts
delay?: number;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
duration?: number;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
easing?: EasingFunction;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
start?: number;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
opacity?: number;
```

<div class="ts-block-property-details"></div>
</div></div>

## SlideParams

<div class="ts-block">

```dts
interface SlideParams {/*…*/}
```

<div class="ts-block-property">

```dts
delay?: number;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
duration?: number;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
easing?: EasingFunction;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
axis?: 'x' | 'y';
```

<div class="ts-block-property-details"></div>
</div></div>

## TransitionConfig

<div class="ts-block">

```dts
interface TransitionConfig {/*…*/}
```

<div class="ts-block-property">

```dts
delay?: number;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
duration?: number;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
easing?: EasingFunction;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
css?: (t: number, u: number) => string;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
tick?: (t: number, u: number) => void;
```

<div class="ts-block-property-details"></div>
</div></div>

---

## svelte/animate

```js
// @noErrors
import { flip } from 'svelte/animate';
```

## flip

The flip function calculates the start and end position of an element and animates between them, translating the x and y values.
`flip` stands for [First, Last, Invert, Play](https://aerotwist.com/blog/flip-your-animations/).

<div class="ts-block">

```dts
function flip(
	node: Element,
	{
		from,
		to
	}: {
		from: DOMRect;
		to: DOMRect;
	},
	params?: FlipParams
): AnimationConfig;
```

</div>



## AnimationConfig

<div class="ts-block">

```dts
interface AnimationConfig {/*…*/}
```

<div class="ts-block-property">

```dts
delay?: number;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
duration?: number;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
easing?: (t: number) => number;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
css?: (t: number, u: number) => string;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
tick?: (t: number, u: number) => void;
```

<div class="ts-block-property-details"></div>
</div></div>

## FlipParams

<div class="ts-block">

```dts
interface FlipParams {/*…*/}
```

<div class="ts-block-property">

```dts
delay?: number;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
duration?: number | ((len: number) => number);
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
easing?: (t: number) => number;
```

<div class="ts-block-property-details"></div>
</div></div>

---

## svelte/motion

```js
// @noErrors
import {
	Spring,
	Tween,
	prefersReducedMotion,
	spring,
	tweened
} from 'svelte/motion';
```

## Spring

<blockquote class="since note">

Available since 5.8.0

</blockquote>

A wrapper for a value that behaves in a spring-like fashion. Changes to `spring.target` will cause `spring.current` to
move towards it over time, taking account of the `spring.stiffness` and `spring.damping` parameters.

```svelte
<script>
	import { Spring } from 'svelte/motion';

	const spring = new Spring(0);
</script>

<input type="range" bind:value={spring.target} />
<input type="range" bind:value={spring.current} disabled />
```

<div class="ts-block">

```dts
class Spring<T> {/*…*/}
```

<div class="ts-block-property">

```dts
constructor(value: T, options?: SpringOptions);
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
static of<U>(fn: () => U, options?: SpringOptions): Spring<U>;
```

<div class="ts-block-property-details">

Create a spring whose value is bound to the return value of `fn`. This must be called
inside an effect root (for example, during component initialisation).

```svelte
<script>
	import { Spring } from 'svelte/motion';

	let { number } = $props();

	const spring = Spring.of(() => number);
</script>
```

</div>
</div>

<div class="ts-block-property">

```dts
set(value: T, options?: SpringUpdateOptions): Promise<void>;
```

<div class="ts-block-property-details">

Sets `spring.target` to `value` and returns a `Promise` that resolves if and when `spring.current` catches up to it.

If `options.instant` is `true`, `spring.current` immediately matches `spring.target`.

If `options.preserveMomentum` is provided, the spring will continue on its current trajectory for
the specified number of milliseconds. This is useful for things like 'fling' gestures.

</div>
</div>

<div class="ts-block-property">

```dts
damping: number;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
precision: number;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
stiffness: number;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
target: T;
```

<div class="ts-block-property-details">

The end value of the spring.
This property only exists on the `Spring` class, not the legacy `spring` store.

</div>
</div>

<div class="ts-block-property">

```dts
get current(): T;
```

<div class="ts-block-property-details">

The current value of the spring.
This property only exists on the `Spring` class, not the legacy `spring` store.

</div>
</div></div>



## Tween

<blockquote class="since note">

Available since 5.8.0

</blockquote>

A wrapper for a value that tweens smoothly to its target value. Changes to `tween.target` will cause `tween.current` to
move towards it over time, taking account of the `delay`, `duration` and `easing` options.

```svelte
<script>
	import { Tween } from 'svelte/motion';

	const tween = new Tween(0);
</script>

<input type="range" bind:value={tween.target} />
<input type="range" bind:value={tween.current} disabled />
```

<div class="ts-block">

```dts
class Tween<T> {/*…*/}
```

<div class="ts-block-property">

```dts
static of<U>(fn: () => U, options?: TweenOptions<U> | undefined): Tween<U>;
```

<div class="ts-block-property-details">

Create a tween whose value is bound to the return value of `fn`. This must be called
inside an effect root (for example, during component initialisation).

```svelte
<script>
	import { Tween } from 'svelte/motion';

	let { number } = $props();

	const tween = Tween.of(() => number);
</script>
```

</div>
</div>

<div class="ts-block-property">

```dts
constructor(value: T, options?: TweenOptions<T>);
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
set(value: T, options?: TweenOptions<T> | undefined): Promise<void>;
```

<div class="ts-block-property-details">

Sets `tween.target` to `value` and returns a `Promise` that resolves if and when `tween.current` catches up to it.

If `options` are provided, they will override the tween's defaults.

</div>
</div>

<div class="ts-block-property">

```dts
get current(): T;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
set target(v: T);
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
get target(): T;
```

<div class="ts-block-property-details"></div>
</div></div>



## prefersReducedMotion

<blockquote class="since note">

Available since 5.7.0

</blockquote>

A [media query](/docs/svelte/svelte-reactivity#MediaQuery) that matches if the user [prefers reduced motion](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion).

```svelte
<script>
	import { prefersReducedMotion } from 'svelte/motion';
	import { fly } from 'svelte/transition';

	let visible = $state(false);
</script>

<button onclick={() => visible = !visible}>
	toggle
</button>

{#if visible}
	<p transition:fly={{ y: prefersReducedMotion.current ? 0 : 200 }}>
		flies in, unless the user prefers reduced motion
	</p>
{/if}
```

<div class="ts-block">

```dts
const prefersReducedMotion: MediaQuery;
```

</div>



## spring

<blockquote class="tag deprecated note">

Use [`Spring`](/docs/svelte/svelte-motion#Spring) instead

</blockquote>

The spring function in Svelte creates a store whose value is animated, with a motion that simulates the behavior of a spring. This means when the value changes, instead of transitioning at a steady rate, it "bounces" like a spring would, depending on the physics parameters provided. This adds a level of realism to the transitions and can enhance the user experience.

<div class="ts-block">

```dts
function spring<T = any>(
	value?: T | undefined,
	opts?: SpringOptions | undefined
): Spring<T>;
```

</div>



## tweened

<blockquote class="tag deprecated note">

Use [`Tween`](/docs/svelte/svelte-motion#Tween) instead

</blockquote>

A tweened store in Svelte is a special type of store that provides smooth transitions between state values over time.

<div class="ts-block">

```dts
function tweened<T>(
	value?: T | undefined,
	defaults?: TweenOptions<T> | undefined
): Tweened<T>;
```

</div>



## Spring

<div class="ts-block">

```dts
interface Spring<T> extends Readable<T> {/*…*/}
```

<div class="ts-block-property">

```dts
set(new_value: T, opts?: SpringUpdateOptions): Promise<void>;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
update: (fn: Updater<T>, opts?: SpringUpdateOptions) => Promise<void>;
```

<div class="ts-block-property-details">

<div class="ts-block-property-bullets">

- <span class="tag deprecated">deprecated</span> Only exists on the legacy `spring` store, not the `Spring` class

</div>

</div>
</div>

<div class="ts-block-property">

```dts
subscribe(fn: (value: T) => void): Unsubscriber;
```

<div class="ts-block-property-details">

<div class="ts-block-property-bullets">

- <span class="tag deprecated">deprecated</span> Only exists on the legacy `spring` store, not the `Spring` class

</div>

</div>
</div>

<div class="ts-block-property">

```dts
precision: number;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
damping: number;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
stiffness: number;
```

<div class="ts-block-property-details"></div>
</div></div>

## SpringOptions

<div class="ts-block">

```dts
interface SpringOptions {/*…*/}
```

<div class="ts-block-property">

```dts
stiffness?: number;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
damping?: number;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
precision?: number;
```

<div class="ts-block-property-details"></div>
</div></div>

## SpringUpdateOptions

<div class="ts-block">

```dts
interface SpringUpdateOptions {/*…*/}
```

<div class="ts-block-property">

```dts
hard?: any;
```

<div class="ts-block-property-details">

<div class="ts-block-property-bullets">

- <span class="tag deprecated">deprecated</span> Only use this for the spring store; does nothing when set on the Spring class

</div>

</div>
</div>

<div class="ts-block-property">

```dts
soft?: string | number | boolean;
```

<div class="ts-block-property-details">

<div class="ts-block-property-bullets">

- <span class="tag deprecated">deprecated</span> Only use this for the spring store; does nothing when set on the Spring class

</div>

</div>
</div>

<div class="ts-block-property">

```dts
instant?: boolean;
```

<div class="ts-block-property-details">

Only use this for the Spring class; does nothing when set on the spring store

</div>
</div>

<div class="ts-block-property">

```dts
preserveMomentum?: number;
```

<div class="ts-block-property-details">

Only use this for the Spring class; does nothing when set on the spring store

</div>
</div></div>

## TweenOptions

<div class="ts-block">

```dts
interface TweenOptions<T> {/*…*/}
```

<div class="ts-block-property">

```dts
delay?: number;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
duration?: number | ((from: T, to: T) => number);
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
easing?: (t: number) => number;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
interpolate?: (a: T, b: T) => (t: number) => T;
```

<div class="ts-block-property-details"></div>
</div></div>

## Tweened

<div class="ts-block">

```dts
interface Tweened<T> extends Readable<T> {/*…*/}
```

<div class="ts-block-property">

```dts
set(value: T, opts?: TweenOptions<T>): Promise<void>;
```

<div class="ts-block-property-details"></div>
</div>

<div class="ts-block-property">

```dts
update(updater: Updater<T>, opts?: TweenOptions<T>): Promise<void>;
```

<div class="ts-block-property-details"></div>
</div></div>

## Updater

<div class="ts-block">

```dts
type Updater<T> = (target_value: T, value: T) => T;
```

</div>

---

## svelte/easing

```js
// @noErrors
import {
	backIn,
	backInOut,
	backOut,
	bounceIn,
	bounceInOut,
	bounceOut,
	circIn,
	circInOut,
	circOut,
	cubicIn,
	cubicInOut,
	cubicOut,
	elasticIn,
	elasticInOut,
	elasticOut,
	expoIn,
	expoInOut,
	expoOut,
	linear,
	quadIn,
	quadInOut,
	quadOut,
	quartIn,
	quartInOut,
	quartOut,
	quintIn,
	quintInOut,
	quintOut,
	sineIn,
	sineInOut,
	sineOut
} from 'svelte/easing';
```

## backIn

<div class="ts-block">

```dts
function backIn(t: number): number;
```

</div>



## backInOut

<div class="ts-block">

```dts
function backInOut(t: number): number;
```

</div>



## backOut

<div class="ts-block">

```dts
function backOut(t: number): number;
```

</div>



## bounceIn

<div class="ts-block">

```dts
function bounceIn(t: number): number;
```

</div>



## bounceInOut

<div class="ts-block">

```dts
function bounceInOut(t: number): number;
```

</div>



## bounceOut

<div class="ts-block">

```dts
function bounceOut(t: number): number;
```

</div>



## circIn

<div class="ts-block">

```dts
function circIn(t: number): number;
```

</div>



## circInOut

<div class="ts-block">

```dts
function circInOut(t: number): number;
```

</div>



## circOut

<div class="ts-block">

```dts
function circOut(t: number): number;
```

</div>



## cubicIn

<div class="ts-block">

```dts
function cubicIn(t: number): number;
```

</div>



## cubicInOut

<div class="ts-block">

```dts
function cubicInOut(t: number): number;
```

</div>



## cubicOut

<div class="ts-block">

```dts
function cubicOut(t: number): number;
```

</div>



## elasticIn

<div class="ts-block">

```dts
function elasticIn(t: number): number;
```

</div>



## elasticInOut

<div class="ts-block">

```dts
function elasticInOut(t: number): number;
```

</div>



## elasticOut

<div class="ts-block">

```dts
function elasticOut(t: number): number;
```

</div>



## expoIn

<div class="ts-block">

```dts
function expoIn(t: number): number;
```

</div>



## expoInOut

<div class="ts-block">

```dts
function expoInOut(t: number): number;
```

</div>



## expoOut

<div class="ts-block">

```dts
function expoOut(t: number): number;
```

</div>



## linear

<div class="ts-block">

```dts
function linear(t: number): number;
```

</div>



## quadIn

<div class="ts-block">

```dts
function quadIn(t: number): number;
```

</div>



## quadInOut

<div class="ts-block">

```dts
function quadInOut(t: number): number;
```

</div>



## quadOut

<div class="ts-block">

```dts
function quadOut(t: number): number;
```

</div>



## quartIn

<div class="ts-block">

```dts
function quartIn(t: number): number;
```

</div>



## quartInOut

<div class="ts-block">

```dts
function quartInOut(t: number): number;
```

</div>



## quartOut

<div class="ts-block">

```dts
function quartOut(t: number): number;
```

</div>



## quintIn

<div class="ts-block">

```dts
function quintIn(t: number): number;
```

</div>



## quintInOut

<div class="ts-block">

```dts
function quintInOut(t: number): number;
```

</div>



## quintOut

<div class="ts-block">

```dts
function quintOut(t: number): number;
```

</div>



## sineIn

<div class="ts-block">

```dts
function sineIn(t: number): number;
```

</div>



## sineInOut

<div class="ts-block">

```dts
function sineInOut(t: number): number;
```

</div>



## sineOut

<div class="ts-block">

```dts
function sineOut(t: number): number;
```

</div>

---

## {#key ...}

```svelte
<!--- copy: false  --->
{#key expression}...{/key}
```

Key blocks destroy and recreate their contents when the value of an expression changes. When used around components, this will cause them to be reinstantiated and reinitialised:

```svelte
{#key value}
	<Component />
{/key}
```

It's also useful if you want a transition to play whenever a value changes:

```svelte
{#key value}
	<div transition:fade>{value}</div>
{/key}
```

---

## Scoped styles

Svelte components can include a `<style>` element containing CSS that belongs to the component. This CSS is _scoped_ by default, meaning that styles will not apply to any elements on the page outside the component in question.

This works by adding a class to affected elements, which is based on a hash of the component styles (e.g. `svelte-123xyz`).

```svelte
<style>
	p {
		/* this will only affect <p> elements in this component */
		color: burlywood;
	}
</style>
```

## Specificity

Each scoped selector receives a [specificity](https://developer.mozilla.org/en-US/docs/Web/CSS/Specificity) increase of 0-1-0, as a result of the scoping class (e.g. `.svelte-123xyz`) being added to the selector. This means that (for example) a `p` selector defined in a component will take precedence over a `p` selector defined in a global stylesheet, even if the global stylesheet is loaded later.

In some cases, the scoping class must be added to a selector multiple times, but after the first occurrence it is added with `:where(.svelte-xyz123)` in order to not increase specificity further.

## Scoped keyframes

If a component defines `@keyframes`, the name is scoped to the component using the same hashing approach. Any `animation` rules in the component will be similarly adjusted:

```svelte
<style>
	.bouncy {
		animation: bounce 10s;
	}

	/* these keyframes are only accessible inside this component */
	@keyframes bounce {
		/* ... */
	}
</style>
```

---

## Global styles

## :global(...)

To apply styles to a single selector globally, use the `:global(...)` modifier:

```svelte
<style>
	:global(body) {
		/* applies to <body> */
		margin: 0;
	}

	div :global(strong) {
		/* applies to all <strong> elements, in any component,
		   that are inside <div> elements belonging
		   to this component */
		color: goldenrod;
	}

	p:global(.big.red) {
		/* applies to all <p> elements belonging to this component
		   with `class="big red"`, even if it is applied
		   programmatically (for example by a library) */
	}
</style>
```

If you want to make @keyframes that are accessible globally, you need to prepend your keyframe names with `-global-`.

The `-global-` part will be removed when compiled, and the keyframe will then be referenced using just `my-animation-name` elsewhere in your code.

```svelte
<style>
	@keyframes -global-my-animation-name {
		/* code goes here */
	}
</style>
```

## :global

To apply styles to a group of selectors globally, create a `:global {...}` block:

```svelte
<style>
	:global {
		/* applies to every <div> in your application */
		div { ... }

		/* applies to every <p> in your application */
		p { ... }
	}

	.a :global {
		/* applies to every `.b .c .d` element, in any component,
		   that is inside an `.a` element in this component */
		.b .c .d {...}
	}
</style>
```

> [!NOTE] The second example above could also be written as an equivalent `.a :global .b .c .d` selector, where everything after the `:global` is unscoped, though the nested form is preferred.

---

## {@attach ...}

Attachments are functions that run in an [effect]($effect) when an element is mounted to the DOM or when [state]($state) read inside the function updates.

Optionally, they can return a function that is called before the attachment re-runs, or after the element is later removed from the DOM.

> [!NOTE]
> Attachments are available in Svelte 5.29 and newer.

```svelte
<!--- file: App.svelte --->
<script>
	/** @type {import('svelte/attachments').Attachment} */
	function myAttachment(element) {
		console.log(element.nodeName); // 'DIV'

		return () => {
			console.log('cleaning up');
		};
	}
</script>

<div {@attach myAttachment}>...</div>
```

An element can have any number of attachments.

## Attachment factories

A useful pattern is for a function, such as `tooltip` in this example, to _return_ an attachment (demo:

```svelte
<!--- file: App.svelte --->
<script>
	import tippy from 'tippy.js';

	let content = $state('Hello!');

	/**
	 * @param {string} content
	 * @returns {import('svelte/attachments').Attachment}
	 */
	function tooltip(content) {
		return (element) => {
			const tooltip = tippy(element, { content });
			return tooltip.destroy;
		};
	}
</script>

<input bind:value={content} />

<button {@attach tooltip(content)}>
	Hover me
</button>
```

Since the `tooltip(content)` expression runs inside an [effect]($effect), the attachment will be destroyed and recreated whenever `content` changes. The same thing would happen for any state read _inside_ the attachment function when it first runs. (If this isn't what you want, see [Controlling when attachments re-run](#Controlling-when-attachments-re-run).)

## Inline attachments

Attachments can also be created inline (demo:

```svelte
<!--- file: App.svelte --->
<canvas
	width={32}
	height={32}
	{@attach (canvas) => {
		const context = canvas.getContext('2d');

		$effect(() => {
			context.fillStyle = color;
			context.fillRect(0, 0, canvas.width, canvas.height);
		});
	}}
></canvas>
```

> [!NOTE]
> The nested effect runs whenever `color` changes, while the outer effect (where `canvas.getContext(...)` is called) only runs once, since it doesn't read any reactive state.

## Conditional attachments

Falsy values like `false` or `undefined` are treated as no attachment, enabling conditional usage:

```svelte
<div {@attach enabled && myAttachment}>...</div>
```

## Passing attachments to components

When used on a component, `{@attach ...}` will create a prop whose key is a [`Symbol`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Symbol). If the component then [spreads](/tutorial/svelte/spread-props) props onto an element, the element will receive those attachments.

This allows you to create _wrapper components_ that augment elements (demo:

```svelte
<!--- file: Button.svelte --->
<script>
	/** @type {import('svelte/elements').HTMLButtonAttributes} */
	let { children, ...props } = $props();
</script>

<!-- `props` includes attachments -->
<button {...props}>
	{@render children?.()}
</button>
```

```svelte
<!--- file: App.svelte --->
<script>
	import tippy from 'tippy.js';
	import Button from './Button.svelte';

	let content = $state('Hello!');

	/**
	 * @param {string} content
	 * @returns {import('svelte/attachments').Attachment}
	 */
	function tooltip(content) {
		return (element) => {
			const tooltip = tippy(element, { content });
			return tooltip.destroy;
		};
	}
</script>

<input bind:value={content} />

<Button {@attach tooltip(content)}>
	Hover me
</Button>
```

## Controlling when attachments re-run

Attachments, unlike [actions](use), are fully reactive: `{@attach foo(bar)}` will re-run on changes to `foo` _or_ `bar` (or any state read inside `foo`):

```js
// @errors: 7006 2304 2552
function foo(bar) {
	return (node) => {
		veryExpensiveSetupWork(node);
		update(node, bar);
	};
}
```

In the rare case that this is a problem (for example, if `foo` does expensive and unavoidable setup work) consider passing the data inside a function and reading it in a child effect:

```js
// @errors: 7006 2304 2552
function foo(+++getBar+++) {
	return (node) => {
		veryExpensiveSetupWork(node);

+++		$effect(() => {
			update(node, getBar());
		});+++
	}
}
```

## Creating attachments programmatically

To add attachments to an object that will be spread onto a component or element, use [`createAttachmentKey`](svelte-attachments#createAttachmentKey).

## Converting actions to attachments

If you're using a library that only provides actions, you can convert them to attachments with [`fromAction`](svelte-attachments#fromAction), allowing you to (for example) use them with components.

---

## $effect

Effects are functions that run when state updates, and can be used for things like calling third-party libraries, drawing on `<canvas>` elements, or making network requests. They only run in the browser, not during server-side rendering.

Generally speaking, you should _not_ update state inside effects, as it will make code more convoluted and will often lead to never-ending update cycles. If you find yourself doing so, see [when not to use `$effect`](#When-not-to-use-$effect) to learn about alternative approaches.

You can create an effect with the `$effect` rune (demo:

```svelte
<script>
	let size = $state(50);
	let color = $state('#ff3e00');

	let canvas;

	$effect(() => {
		const context = canvas.getContext('2d');
		context.clearRect(0, 0, canvas.width, canvas.height);

		// this will re-run whenever `color` or `size` change
		context.fillStyle = color;
		context.fillRect(0, 0, size, size);
	});
</script>

<canvas bind:this={canvas} width="100" height="100"></canvas>
```

When Svelte runs an effect function, it tracks which pieces of state (and derived state) are accessed (unless accessed inside [`untrack`](svelte#untrack)), and re-runs the function when that state later changes.

> [!NOTE] If you're having difficulty understanding why your `$effect` is rerunning or is not running see [understanding dependencies](#Understanding-dependencies). Effects are triggered differently than the `$:` blocks you may be used to if coming from Svelte 4.

### Understanding lifecycle

Your effects run after the component has been mounted to the DOM, and in a [microtask](https://developer.mozilla.org/en-US/docs/Web/API/HTML_DOM_API/Microtask_guide) after state changes. Re-runs are batched (i.e. changing `color` and `size` in the same moment won't cause two separate runs), and happen after any DOM updates have been applied.

You can use `$effect` anywhere, not just at the top level of a component, as long as it is called while a parent effect is running.

> [!NOTE] Svelte uses effects internally to represent logic and expressions in your template — this is how `<h1>hello {name}!</h1>` updates when `name` changes.

An effect can return a _teardown function_ which will run immediately before the effect re-runs:

<!-- codeblock:start {"title":"Effect teardown"} -->
```svelte
<!--- file: App.svelte --->
<script>
	let count = $state(0);
	let milliseconds = $state(1000);

	$effect(() => {
		// This will be recreated whenever `milliseconds` changes
		const interval = setInterval(() => {
			count += 1;
		}, milliseconds);

		return () => {
			// if a teardown function is provided, it will run
			// a) immediately before the effect re-runs
			// b) when the component is destroyed
			clearInterval(interval);
		};
	});
</script>

<h1>{count}</h1>

<button onclick={() => (milliseconds *= 2)}>slower</button>
<button onclick={() => (milliseconds /= 2)}>faster</button>
```
<!-- codeblock:end -->

Teardown functions also run when the effect is destroyed, which happens when its parent is destroyed (for example, a component is unmounted) or the parent effect re-runs.

### Understanding dependencies

`$effect` automatically picks up any reactive values (`$state`, `$derived`, `$props`) that are _synchronously_ read inside its function body (including indirectly, via function calls) and registers them as dependencies. When those dependencies change, the `$effect` schedules a re-run.

If `$state` and `$derived` are used directly inside the `$effect` (for example, during creation of a [reactive class](https://svelte.dev/docs/svelte/$state#Classes)), those values will _not_ be treated as dependencies.

Values that are read _asynchronously_ — after an `await` or inside a `setTimeout`, for example — will not be tracked. Here, the canvas will be repainted when `color` changes, but not when `size` changes (demo:

```ts
// @filename: index.ts
declare let canvas: {
	width: number;
	height: number;
	getContext(type: '2d', options?: CanvasRenderingContext2DSettings): CanvasRenderingContext2D;
};
declare let color: string;
declare let size: number;

// ---cut---
$effect(() => {
	const context = canvas.getContext('2d');
	context.clearRect(0, 0, canvas.width, canvas.height);

	// this will re-run whenever `color` changes...
	context.fillStyle = color;

	setTimeout(() => {
		// ...but not when `size` changes
		context.fillRect(0, 0, size, size);
	}, 0);
});
```

An effect only reruns when the object it reads changes, not when a property inside it changes. (If you want to observe changes _inside_ an object at dev time, you can use [`$inspect`]($inspect).)

```svelte
<script>
	let state = $state({ value: 0 });
	let derived = $derived({ value: state.value * 2 });

	// this will run once, because `state` is never reassigned (only mutated)
	$effect(() => {
		state;
	});

	// this will run whenever `state.value` changes...
	$effect(() => {
		state.value;
	});

	// ...and so will this, because `derived` is a new object each time
	$effect(() => {
		derived;
	});
</script>

<button onclick={() => (state.value += 1)}>
	{state.value}
</button>

<p>{state.value} doubled is {derived.value}</p>
```

An effect only depends on the values that it read the last time it ran. This has interesting implications for effects that have conditional code.

For instance, if `condition` is `true` in the code snippet below, the code inside the `if` block will run and `color` will be evaluated. This means that changes to either `condition` or `color` will cause the effect to re-run.

Conversely, if `condition` is `false`, `color` will not be evaluated, and the effect will _only_ re-run again when `condition` changes.

```ts
// @filename: ambient.d.ts
declare module 'canvas-confetti' {
	interface ConfettiOptions {
		colors: string[];
	}

	function confetti(opts?: ConfettiOptions): void;
	export default confetti;
}

// @filename: index.js
// ---cut---
import confetti from 'canvas-confetti';

let condition = $state(true);
let color = $state('#ff3e00');

$effect(() => {
	if (condition) {
		confetti({ colors: [color] });
	} else {
		confetti();
	}
});
```

## `$effect.pre`

In rare cases, you may need to run code _before_ the DOM updates. For this we can use the `$effect.pre` rune:

```svelte
<script>
	import { tick } from 'svelte';

	let div = $state();
	let messages = $state([]);

	// ...

	$effect.pre(() => {
		if (!div) return; // not yet mounted

		// reference `messages` array length so that this code re-runs whenever it changes
		messages.length;

		// autoscroll when new messages are added
		if (div.offsetHeight + div.scrollTop > div.scrollHeight - 20) {
			tick().then(() => {
				div.scrollTo(0, div.scrollHeight);
			});
		}
	});
</script>

<div bind:this={div}>
	{#each messages as message}
		<p>{message}</p>
	{/each}
</div>
```

Apart from the timing, `$effect.pre` works exactly like `$effect`.

## `$effect.tracking`

The `$effect.tracking` rune is an advanced feature that tells you whether or not the code is running inside a tracking context, such as an effect or inside your template:

<!-- codeblock:start {"title":"$effect.tracking()"} -->
```svelte
<!--- file: App.svelte --->
<script>
	console.log('in component setup:', $effect.tracking()); // false

	$effect(() => {
		console.log('in effect:', $effect.tracking()); // true
	});
</script>

<p>in template: {$effect.tracking()}</p> <!-- true -->
```
<!-- codeblock:end -->

It is used to implement abstractions like [`createSubscriber`](/docs/svelte/svelte-reactivity#createSubscriber), which will create listeners to update reactive values but _only_ if those values are being tracked (rather than, for example, read inside an event handler).

## `$effect.pending`

When using [`await`](await-expressions) in components, the `$effect.pending()` rune tells you how many promises are pending in the current [boundary](svelte-boundary), not including child boundaries:

<!-- codeblock:start {"title":"$effect.pending"} -->
```svelte
<!--- file: App.svelte --->
<script>
	let a = $state(1);
	let b = $state(2);

	async function add(a, b) {
		await new Promise((f) => setTimeout(f, 500)); // artificial delay
		return a + b;
	}
</script>

<button onclick={() => a++}>a++</button>
<button onclick={() => b++}>b++</button>

<p>{a} + {b} = {await add(a, b)}</p>

{#if $effect.pending()}
	<p>pending promises: {$effect.pending()}</p>
{/if}
```
<!-- codeblock:end -->

## `$effect.root`

The `$effect.root` rune is an advanced feature that creates a non-tracked scope that doesn't auto-cleanup. This is useful for nested effects that you want to manually control. This rune also allows for the creation of effects outside of the component initialisation phase.

```js
const destroy = $effect.root(() => {
	$effect(() => {
		// setup
	});

	return () => {
		// cleanup
	};
});

// later...
destroy();
```

## When not to use `$effect`

In general, `$effect` is best considered something of an escape hatch — useful for things like analytics and direct DOM manipulation — rather than a tool you should use frequently. In particular, avoid using it to synchronise state. Instead of this...

```svelte
<script>
	let count = $state(0);
	let doubled = $state();

	// don't do this!
	$effect(() => {
		doubled = count * 2;
	});
</script>
```

...do this:

```svelte
<script>
	let count = $state(0);
	let doubled = $derived(count * 2);
</script>
```

> [!NOTE] For things that are more complicated than a simple expression like `count * 2`, you can also use `$derived.by`.

If you're using an effect because you want to be able to reassign the derived value (to build an optimistic UI, for example) note that [deriveds can be directly overridden]($derived#Overriding-derived-values) as of Svelte 5.25.

You might be tempted to do something convoluted with effects to link one value to another. The following example shows two inputs for "money spent" and "money left" that are connected to each other. If you update one, the other should update accordingly. Instead of using effects for this...

<!-- codeblock:start {"title":"Setting state in effects (don't do this!)"} -->
```svelte
<!--- file: App.svelte --->
<script>
	const total = 100;
	let spent = $state(0);
	let left = $state(total);

	$effect(() => {
		left = total - spent;
	});

	$effect(() => {
		spent = total - left;
	});
</script>

<label>
	<input type="range" bind:value={spent} max={total} />
	{spent}/{total} spent
</label>

<label>
	<input type="range" bind:value={left} max={total} />
	{left}/{total} left
</label>

<style>
	label {
		display: flex;
		gap: 0.5em;
	}
</style>
```
<!-- codeblock:end -->

...use `oninput` callbacks or — better still — [function bindings](bind#Function-bindings) where possible:

<!-- codeblock:start {"title":"Setting state with function bindings"} -->
```svelte
<!--- file: App.svelte --->
<script>
	const total = 100;
	let spent = $state(0);
	let left = $derived(total - spent);

+++	function updateLeft(left) {
		spent = total - left;
	}+++
</script>

<label>
	<input type="range" bind:value={spent} max={total} />
	{spent}/{total} spent
</label>

<label>
	<input type="range" +++bind:value={() => left, updateLeft}+++ max={total} />
	{left}/{total} left
</label>

<style>
	label {
		display: flex;
		gap: 0.5em;
	}
</style>
```
<!-- codeblock:end -->

If you absolutely have to update `$state` within an effect and run into an infinite loop because you read and write to the same `$state`, use [untrack](svelte#untrack).