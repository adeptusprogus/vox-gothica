"""Lexer. Roman numerals and string interpolation resolved here (docs 01)."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from .heresiae import Profanatio

KEYWORDS = {
    "AVE", "OMNISSIAH", "CANTICUM", "FABRICA", "LITANIA", "FINIS",
    "DECLARO", "SANCTUM", "FIAT", "SCHEMA", "RITUS", "REDDO",
    "SI", "TUNC", "ALITER", "DUM", "PRO", "OMNI", "IN", "AGE", "RUMPO", "PERGO",
    "ET", "VEL", "NON", "VERUM", "FALSUM", "NIHIL",
    "NUMERUS", "FRACTIO", "SCRIPTUM", "VERITAS", "ORDO", "TABULA", "HERESIS", "RELATIO",
    "VOCIFERO", "SUSURRO", "AUSCULTO",
    "TEMPTA", "HERESIM", "PROCLAMO", "DENIQUE", "GENERIS",
    "INVOCO", "EX", "UT", "PALAM",
    "EXSTRUATUR", "FOEDUS", "POSTULO", "PROFITEOR", "SCRUTOR", "SEDES", "ARCANUM",
}
RESERVED = {"CHORUS", "CAPITULUM", "LEGATUS", "MUTATIO"}

_ROMAN_RE = re.compile(r"^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$")
_ROMAN_VAL = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def roman_to_int(s: str) -> int | None:
    if s == "N":
        return 0
    if not s or not _ROMAN_RE.match(s):
        return None
    total, prev = 0, 0
    for ch in reversed(s):
        v = _ROMAN_VAL[ch]
        total = total - v if v < prev else total + v
        prev = max(prev, v)
    return total


def int_to_roman(n: int) -> str:
    if n == 0:
        return "N"
    if not (0 <= n <= 3999):
        raise ValueError(n)
    vals = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"),
            (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"),
            (5, "V"), (4, "IV"), (1, "I")]
    out = []
    for v, sym in vals:
        while n >= v:
            out.append(sym)
            n -= v
    return "".join(out)


@dataclass
class Tok:
    kind: str          # KW, IDENT, INT, FLOAT, STRING, OP, NL, EOF
    value: object
    line: int
    col: int = 0

    def __repr__(self):
        return f"{self.kind}:{self.value!r}@{self.line}"


@dataclass
class StrPart:
    """('t', text) or ('e', source_of_expression, line)"""
    kind: str
    value: str
    line: int = 0


_OPS = ["->", "==", "!=", "<=", ">=", "++", "+", "-", "*", "/", "%",
        "(", ")", "[", "]", "{", "}", ",", ":", ".", "<", ">", "="]

_CONT_AFTER = {"+", "-", "*", "/", "%", "==", "!=", "<", "<=", ">", ">=",
               ",", "->", "="}
_CONT_KW = {"FIAT", "ET", "VEL", "TUNC_NEVER"}


class Lexer:
    def __init__(self, src: str, archivum: str = "<anon>"):
        self.src = src.replace("\r\n", "\n")
        self.i = 0
        self.line = 1
        self.archivum = archivum
        self.toks: list[Tok] = []

    def err(self, code, genus, msg):
        raise Profanatio(code, genus, msg, self.archivum, self.line)

    def tokens(self) -> list[Tok]:
        self._lex()
        return self._postprocess()

    # ---------- raw lexing ----------
    def _lex(self):
        s, n = self.src, len(self.src)
        while self.i < n:
            c = s[self.i]
            if c == "\n":
                self.toks.append(Tok("NL", None, self.line))
                self.i += 1
                self.line += 1
                continue
            if c in " \t":
                self.i += 1
                continue
            # comments
            if s.startswith("+++", self.i):
                self._block_comment()
                continue
            if s.startswith("++", self.i):
                j = s.find("\n", self.i)
                self.i = n if j < 0 else j
                continue
            if c == '"':
                self._string()
                continue
            if c.isdigit():
                self._number()
                continue
            if c.isalpha() or c == "_":
                self._word()
                continue
            for op in _OPS:
                if s.startswith(op, self.i):
                    if op == "++":
                        break  # handled above; unreachable
                    self.toks.append(Tok("OP", op, self.line))
                    self.i += len(op)
                    break
            else:
                self.err("P-XIV", "syntaxis_profana",
                         f"Unholy glyph '{c}' defiles the scroll.")
        self.toks.append(Tok("NL", None, self.line))
        self.toks.append(Tok("EOF", None, self.line))

    def _block_comment(self):
        # +++ ... +++ (identical delimiters — non-nesting)
        s, n = self.src, len(self.src)
        self.i += 3
        while self.i < n:
            if s.startswith("+++", self.i):
                self.i += 3
                return
            if s[self.i] == "\n":
                self.line += 1
            self.i += 1
        self.err("P-II", "commentarium_apertum", "Unterminated block comment.")

    def _number(self):
        s, n = self.src, len(self.src)
        j = self.i
        while j < n and (s[j].isdigit() or s[j] == "_"):
            j += 1
        if j < n and s[j] == "." and j + 1 < n and s[j + 1].isdigit():
            j += 1
            while j < n and (s[j].isdigit() or s[j] == "_"):
                j += 1
            if j < n and s[j] in "eE":
                j += 1
                if j < n and s[j] in "+-":
                    j += 1
                while j < n and s[j].isdigit():
                    j += 1
            self.toks.append(Tok("FLOAT", float(s[self.i:j].replace("_", "")), self.line))
        else:
            self.toks.append(Tok("INT", int(s[self.i:j].replace("_", "")), self.line))
        self.i = j

    def _word(self):
        s, n = self.src, len(self.src)
        j = self.i
        while j < n and (s[j].isalnum() or s[j] == "_"):
            j += 1
        w = s[self.i:j]
        self.i = j
        if w.isupper() or (w[0].isupper() and w.isalpha()):
            if w in RESERVED:
                self.err("P-IV", "verbum_reservatum",
                         f"'{w}' is reserved for a future age.")
            if w in KEYWORDS:
                self.toks.append(Tok("KW", w, self.line))
                return
            r = roman_to_int(w)
            if r is not None:
                self.toks.append(Tok("ROMAN", r, self.line))
                return
            if w.isupper() and all(ch in "IVXLCDMN" for ch in w):
                self.err("P-V", "numerus_barbarus",
                         f"'{w}' is not a canonical numeral. The Machine God abhors sloppiness.")
            self.err("P-XIV", "syntaxis_profana",
                     f"Uppercase word '{w}' is neither keyword nor numeral.")
        if not re.fullmatch(r"[a-z_][a-z0-9_]*", w):
            self.err("P-XIV", "syntaxis_profana", f"Profane identifier '{w}'.")
        if len(w) > 128:
            self.err("P-III", "nomen_nimium", "Identifier exceeds 128 bytes.")
        self.toks.append(Tok("IDENT", w, self.line))

    def _string(self):
        s, n = self.src, len(self.src)
        triple = s.startswith('"""', self.i)
        endq = '"""' if triple else '"'
        self.i += len(endq)
        start_line = self.line
        parts: list[StrPart] = []
        buf = []
        while True:
            if self.i >= n:
                self.err("P-XIV", "syntaxis_profana", "Unterminated string.")
            if s.startswith(endq, self.i):
                self.i += len(endq)
                break
            c = s[self.i]
            if c == "\n":
                if not triple:
                    self.err("P-XIV", "syntaxis_profana",
                             "Newline in single-line string.")
                self.line += 1
                buf.append(c)
                self.i += 1
                continue
            if c == "\\":
                self.i += 1
                if self.i >= n:
                    self.err("P-VI", "fuga_ignota", "Escape at end of file.")
                e = s[self.i]
                mapping = {"n": "\n", "t": "\t", "r": "\r", '"': '"',
                           "\\": "\\", "0": "\0"}
                if e in mapping:
                    buf.append(mapping[e])
                    self.i += 1
                elif e == "u" and s[self.i + 1: self.i + 2] == "{":
                    j = s.find("}", self.i)
                    if j < 0:
                        self.err("P-VI", "fuga_ignota", "Unclosed \\u{...}.")
                    buf.append(chr(int(s[self.i + 2:j], 16)))
                    self.i = j + 1
                else:
                    self.err("P-VI", "fuga_ignota", f"Unknown escape '\\{e}'.")
                continue
            if c == "{":
                if s.startswith("{{", self.i):
                    buf.append("{")
                    self.i += 2
                    continue
                # interpolation
                if buf:
                    parts.append(StrPart("t", "".join(buf)))
                    buf = []
                expr_src, ln = self._capture_interp()
                parts.append(StrPart("e", expr_src, ln))
                continue
            if c == "}":
                if s.startswith("}}", self.i):
                    buf.append("}")
                    self.i += 2
                    continue
                self.err("P-XIV", "syntaxis_profana",
                         "Lone '}' in string; write '}}'.")
            buf.append(c)
            self.i += 1
        if buf or not parts:
            parts.append(StrPart("t", "".join(buf)))
        if triple:
            parts = _dedent_parts(parts)
        self.toks.append(Tok("STRING", parts, start_line))

    def _capture_interp(self) -> tuple[str, int]:
        s, n = self.src, len(self.src)
        assert s[self.i] == "{"
        self.i += 1
        start = self.i
        ln = self.line
        depth = 1
        in_str = False
        while self.i < n:
            c = s[self.i]
            if in_str:
                if c == "\\":
                    self.i += 2
                    continue
                if c == '"':
                    in_str = False
            else:
                if c == '"':
                    in_str = True
                elif c == "{":
                    depth += 1
                elif c == "}":
                    depth -= 1
                    if depth == 0:
                        src = s[start:self.i]
                        self.i += 1
                        return src, ln
                elif c == "\n":
                    self.err("P-XIV", "syntaxis_profana",
                             "Newline inside interpolation.")
            self.i += 1
        self.err("P-XIV", "syntaxis_profana", "Unclosed interpolation '{'.")

    # ---------- postprocess: newline suppression ----------
    def _postprocess(self) -> list[Tok]:
        """Suppress NL inside brackets — except inside the body of an
        anonymous RITUS expression opened within brackets, where statements
        need their newlines back (docs 05-rites §3)."""
        toks = self.toks
        out: list[Tok] = []
        depth = 0
        rite_stack: list[list[int]] = []   # [paren_depth_at_open, open_count]

        def is_rite_def_start(i: int) -> bool:
            t = toks[i]
            if not (t.kind == "KW" and t.value == "RITUS"):
                return False
            nxt = toks[i + 1] if i + 1 < len(toks) else None
            nxt2 = toks[i + 2] if i + 2 < len(toks) else None
            if nxt and nxt.kind == "OP" and nxt.value == "(":
                return True                     # anonymous
            if (nxt and nxt.kind == "IDENT" and nxt2
                    and nxt2.kind == "OP" and nxt2.value == "("):
                return True                     # named
            return False

        for i, t in enumerate(toks):
            if t.kind == "OP" and t.value in "([{":
                depth += 1
            elif t.kind == "OP" and t.value in ")]}":
                depth = max(0, depth - 1)
            if is_rite_def_start(i):
                if rite_stack:
                    rite_stack[-1][1] += 1
                elif depth > 0:
                    rite_stack.append([depth, 1])
            if (t.kind == "KW" and t.value == "RITUS" and i > 0
                    and toks[i - 1].kind == "KW" and toks[i - 1].value == "FINIS"
                    and rite_stack):
                rite_stack[-1][1] -= 1
                if rite_stack[-1][1] == 0:
                    rite_stack.pop()
            if t.kind == "NL":
                threshold = rite_stack[-1][0] if rite_stack else 0
                if depth > threshold:
                    continue
                if not out or out[-1].kind == "NL":
                    continue
                prev = out[-1]
                if ((prev.kind == "OP" and prev.value in _CONT_AFTER)
                        or (prev.kind == "KW" and prev.value in
                            ("FIAT", "ET", "VEL"))):
                    continue
            out.append(t)
        return out


def _dedent_parts(parts: list[StrPart]) -> list[StrPart]:
    # crude dedent: strip common leading spaces of lines in text parts
    text = "".join(p.value if p.kind == "t" else "\0" for p in parts)
    lines = text.split("\n")
    indents = [len(l) - len(l.lstrip(" ")) for l in lines[1:] if l.strip()]
    pad = min(indents) if indents else 0
    if pad == 0:
        return parts
    out = []
    for p in parts:
        if p.kind == "t":
            ls = p.value.split("\n")
            ls = [ls[0]] + [l[pad:] if l[:pad].strip() == "" else l for l in ls[1:]]
            v = "\n".join(ls)
            if v.startswith("\n"):
                v = v[1:]
            out.append(StrPart("t", v))
        else:
            out.append(p)
    return out
