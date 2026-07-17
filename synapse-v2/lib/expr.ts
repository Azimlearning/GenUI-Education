/**
 * A restricted expression evaluator.
 *
 * Tier B lets the model write the *formula* driving a screen — the specific
 * physics equation, a reaction-rate function — without shipping generated code
 * to the host page. This is what makes Tier B more than plain UI-as-data.
 *
 * The rules that make that safe:
 *   - Recursive-descent parser. No eval, no new Function, ever.
 *   - Whitelisted maths only. No property access, no calls into anything but
 *     the function table below, no DOM, no I/O, no globals.
 *   - No loops in the grammar at all, so there is no unbounded work to bound.
 *   - Hard caps on input length and AST node count.
 *
 * Grammar (lowest precedence first):
 *   expr    := ternary
 *   ternary := or ( "?" expr ":" expr )?
 *   or      := and ( "||" and )*
 *   and     := cmp ( "&&" cmp )*
 *   cmp     := sum ( ("=="|"!="|"<="|">="|"<"|">") sum )?
 *   sum     := product ( ("+"|"-") product )*
 *   product := power ( ("*"|"/"|"%") power )*
 *   power   := unary ( "^" power )?            right associative
 *   unary   := ("-"|"!")? primary
 *   primary := number | ident | ident "(" args ")" | "(" expr ")"
 */

const MAX_SOURCE = 500;
const MAX_NODES = 200;
/**
 * Nesting cap. The node cap does not bound this: each "(" costs ~10 stack
 * frames but only one node, so a formula of nothing but parentheses could
 * recurse deep enough to overflow while still counting as small.
 */
const MAX_DEPTH = 24;

const FUNCTIONS: Record<string, (...a: number[]) => number> = {
  abs: Math.abs,
  min: Math.min,
  max: Math.max,
  sqrt: Math.sqrt,
  cbrt: Math.cbrt,
  pow: Math.pow,
  exp: Math.exp,
  ln: Math.log,
  log: Math.log10,
  log2: Math.log2,
  sin: Math.sin,
  cos: Math.cos,
  tan: Math.tan,
  asin: Math.asin,
  acos: Math.acos,
  atan: Math.atan,
  atan2: Math.atan2,
  sinh: Math.sinh,
  cosh: Math.cosh,
  tanh: Math.tanh,
  round: Math.round,
  floor: Math.floor,
  ceil: Math.ceil,
  sign: Math.sign,
  hypot: Math.hypot,
  rad: (d) => (d * Math.PI) / 180,
  deg: (r) => (r * 180) / Math.PI,
  clamp: (v, lo, hi) => Math.min(Math.max(v, lo), hi),
};

const CONSTANTS: Record<string, number> = {
  pi: Math.PI,
  e: Math.E,
  // Physical constants a science formula might reasonably reach for.
  g: 9.81,
  c: 299_792_458,
  NA: 6.02214076e23,
};

type Token =
  | { kind: "num"; value: number }
  | { kind: "ident"; value: string }
  | { kind: "op"; value: string };

function tokenize(src: string): Token[] {
  const tokens: Token[] = [];
  let i = 0;

  while (i < src.length) {
    const ch = src[i];

    if (ch === " " || ch === "\t" || ch === "\n" || ch === "\r") {
      i++;
      continue;
    }

    if (ch >= "0" && ch <= "9") {
      let j = i;
      while (j < src.length && /[0-9._]/.test(src[j])) j++;
      // Exponent notation: 1.5e-3
      if (src[j] === "e" || src[j] === "E") {
        const k = src[j + 1] === "+" || src[j + 1] === "-" ? j + 2 : j + 1;
        if (/[0-9]/.test(src[k] ?? "")) {
          j = k;
          while (j < src.length && /[0-9]/.test(src[j])) j++;
        }
      }
      const value = Number(src.slice(i, j).replace(/_/g, ""));
      if (!Number.isFinite(value)) throw new Error(`bad number at ${i}`);
      tokens.push({ kind: "num", value });
      i = j;
      continue;
    }

    if (/[A-Za-z_]/.test(ch)) {
      let j = i;
      while (j < src.length && /[A-Za-z0-9_]/.test(src[j])) j++;
      tokens.push({ kind: "ident", value: src.slice(i, j) });
      i = j;
      continue;
    }

    const two = src.slice(i, i + 2);
    if (["==", "!=", "<=", ">=", "&&", "||"].includes(two)) {
      tokens.push({ kind: "op", value: two });
      i += 2;
      continue;
    }

    if ("+-*/%^()<>?:,!".includes(ch)) {
      tokens.push({ kind: "op", value: ch });
      i++;
      continue;
    }

    throw new Error(`unexpected character "${ch}" at ${i}`);
  }

  return tokens;
}

/**
 * Parse and evaluate in one pass. The scope is a flat map of numbers — the
 * current values of the screen's inputs. Anything not in scope, CONSTANTS, or
 * FUNCTIONS is an error, so an expression cannot reach outside itself.
 */
class Parser {
  private pos = 0;
  private nodes = 0;
  private depth = 0;

  constructor(
    private readonly tokens: Token[],
    private readonly scope: Record<string, number>,
  ) {}

  private peek(): Token | undefined {
    return this.tokens[this.pos];
  }

  private eat(value: string): boolean {
    const t = this.peek();
    if (t?.kind === "op" && t.value === value) {
      this.pos++;
      return true;
    }
    return false;
  }

  private expect(value: string): void {
    if (!this.eat(value)) throw new Error(`expected "${value}"`);
  }

  private tick(): void {
    if (++this.nodes > MAX_NODES) throw new Error("expression too complex");
  }

  parse(): number {
    const value = this.expr();
    if (this.pos !== this.tokens.length) throw new Error("trailing tokens");
    return value;
  }

  /**
   * Every nesting level enters through here: a parenthesised group, a ternary
   * branch, a function argument. Counting depth at this one point bounds the
   * recursion of the whole grammar.
   */
  private expr(): number {
    if (++this.depth > MAX_DEPTH) throw new Error("expression nested too deeply");
    try {
      return this.ternary();
    } finally {
      this.depth--;
    }
  }

  private ternary(): number {
    const cond = this.or();
    if (this.eat("?")) {
      this.tick();
      // Both branches are parsed so the grammar stays well-formed, but only
      // the taken branch's value is returned.
      const whenTrue = this.expr();
      this.expect(":");
      const whenFalse = this.expr();
      return cond ? whenTrue : whenFalse;
    }
    return cond;
  }

  private or(): number {
    let left = this.and();
    while (this.eat("||")) {
      this.tick();
      const right = this.and();
      left = left || right ? 1 : 0;
    }
    return left;
  }

  private and(): number {
    let left = this.cmp();
    while (this.eat("&&")) {
      this.tick();
      const right = this.cmp();
      left = left && right ? 1 : 0;
    }
    return left;
  }

  private cmp(): number {
    const left = this.sum();
    for (const op of ["==", "!=", "<=", ">=", "<", ">"]) {
      if (this.eat(op)) {
        this.tick();
        const right = this.sum();
        switch (op) {
          case "==":
            return left === right ? 1 : 0;
          case "!=":
            return left !== right ? 1 : 0;
          case "<=":
            return left <= right ? 1 : 0;
          case ">=":
            return left >= right ? 1 : 0;
          case "<":
            return left < right ? 1 : 0;
          default:
            return left > right ? 1 : 0;
        }
      }
    }
    return left;
  }

  private sum(): number {
    let left = this.product();
    for (;;) {
      if (this.eat("+")) {
        this.tick();
        left += this.product();
      } else if (this.eat("-")) {
        this.tick();
        left -= this.product();
      } else return left;
    }
  }

  private product(): number {
    let left = this.power();
    for (;;) {
      if (this.eat("*")) {
        this.tick();
        left *= this.power();
      } else if (this.eat("/")) {
        this.tick();
        left /= this.power();
      } else if (this.eat("%")) {
        this.tick();
        left %= this.power();
      } else return left;
    }
  }

  private power(): number {
    const base = this.unary();
    if (this.eat("^")) {
      this.tick();
      return Math.pow(base, this.power());
    }
    return base;
  }

  private unary(): number {
    if (this.eat("-")) {
      this.tick();
      return -this.unary();
    }
    if (this.eat("!")) {
      this.tick();
      return this.unary() ? 0 : 1;
    }
    return this.primary();
  }

  private primary(): number {
    this.tick();
    const t = this.peek();
    if (!t) throw new Error("unexpected end of expression");

    if (t.kind === "num") {
      this.pos++;
      return t.value;
    }

    if (t.kind === "ident") {
      this.pos++;
      const name = t.value;

      if (this.eat("(")) {
        const fn = FUNCTIONS[name];
        if (!fn) throw new Error(`unknown function "${name}"`);
        const args: number[] = [];
        if (!this.eat(")")) {
          do {
            args.push(this.expr());
          } while (this.eat(","));
          this.expect(")");
        }
        return fn(...args);
      }

      if (name in this.scope) return this.scope[name];
      if (name in CONSTANTS) return CONSTANTS[name];
      throw new Error(`unknown name "${name}"`);
    }

    if (this.eat("(")) {
      const value = this.expr();
      this.expect(")");
      return value;
    }

    throw new Error(`unexpected token "${t.value}"`);
  }
}

/**
 * Evaluate a model-written formula against the screen's current input values.
 * Never throws: a bad expression yields an error string the renderer can show,
 * because a broken formula must degrade visibly rather than crash the page.
 */
export function evaluate(
  source: string,
  scope: Record<string, number>,
): { ok: true; value: number } | { ok: false; error: string } {
  try {
    if (typeof source !== "string") throw new Error("formula must be a string");
    if (source.length > MAX_SOURCE) throw new Error("formula too long");

    const value = new Parser(tokenize(source), scope).parse();
    if (!Number.isFinite(value)) throw new Error("result is not a finite number");
    return { ok: true, value };
  } catch (err) {
    return { ok: false, error: err instanceof Error ? err.message : "bad formula" };
  }
}

/** The vocabulary, documented for the model's system prompt. */
export const EXPR_DOCS = `Formulas are arithmetic over the screen's input ids.
Operators: + - * / % ^ (power), comparisons (== != < <= > >=), && || !, and ternary cond ? a : b.
Functions: ${Object.keys(FUNCTIONS).join(", ")}.
Constants: ${Object.keys(CONSTANTS).join(", ")} (g = 9.81 m/s^2).
Angles are radians — use rad(deg) to convert. No variables other than input ids and these constants.`;
