"""Safe rich reading for standalone articles; daily archive renderer stays stable."""
import html
import re

from markdown_it import MarkdownIt
from mdit_py_plugins.dollarmath import dollarmath_plugin
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound


def inline_tex(state, silent):
    r"""Recognize GPT's \( ... \) before CommonMark consumes the escapes."""
    start=state.pos
    if not state.src.startswith('\\(', start): return False
    end=state.src.find('\\)', start+2)
    if end<0: return False
    if not silent:
        token=state.push('math_inline','math',0)
        token.content=state.src[start+2:end]
    state.pos=end+2
    return True


def block_tex(state, start, end, silent):
    line=state.src[state.bMarks[start]+state.tShift[start]:state.eMarks[start]]
    if not line.startswith('\\['): return False
    parts=[line[2:]];last=start
    while not parts[-1].rstrip().endswith('\\]'):
        last+=1
        if last>=end: return False
        parts.append(state.src[state.bMarks[last]+state.tShift[last]:state.eMarks[last]])
    if silent: return True
    parts[-1]=parts[-1].rstrip()[:-2]
    token=state.push('math_block','math',0)
    token.block=True;token.content='\n'.join(parts).strip();token.map=[start,last+1]
    state.line=last+1
    return True


def render_reading(body):
    """Return rendered Markdown and a unique, ordered heading outline."""
    md = MarkdownIt('commonmark', {'html': False, 'breaks': True}).enable('table')
    md.use(dollarmath_plugin, allow_space=False, allow_digits=False)
    md.inline.ruler.before('escape','inline_tex',inline_tex)
    md.block.ruler.before('paragraph','block_tex',block_tex,{'alt':['paragraph','reference','blockquote','list']})

    def fence(tokens, idx, options, env):
        token = tokens[idx]
        language = token.info.split()[0] if token.info.strip() else 'text'
        if language == 'mermaid':
            return '<pre class="mermaid">'+html.escape(token.content)+'</pre>\n'
        try:
            lexer = get_lexer_by_name(language)
        except ClassNotFound:
            lexer = get_lexer_by_name('text')
        return highlight(token.content, lexer, HtmlFormatter())

    md.renderer.rules['fence'] = fence
    # Keep TeX as text for KaTeX; no author-controlled HTML enters the DOM.
    md.renderer.rules['math_inline'] = lambda ts, i, o, e: '<span class="math inline">'+html.escape(ts[i].content)+'</span>'
    md.renderer.rules['math_block'] = lambda ts, i, o, e: '<div class="math block">'+html.escape(ts[i].content)+'</div>\n'
    tokens = md.parse(body)
    outline, used = [], {'main-content'}
    for idx, token in enumerate(tokens):
        if token.type == 'heading_open':
            inline = tokens[idx+1]
            title = ''.join(t.content for t in (inline.children or []) if t.type in ('text', 'code_inline', 'math_inline'))
            stem = re.sub(r'[^\w\-\u4e00-\u9fff]+', '-', title.casefold()).strip('-') or 'section'
            anchor, number = stem, 1
            while anchor in used:
                number += 1
                anchor = stem+'-'+str(number)
            used.add(anchor)
            token.attrSet('id', anchor)
            level = int(token.tag[1])
            if level == 1:
                token.tag = tokens[idx+2].tag = 'h2'
            outline.append((level, anchor, title))
        if token.children:
            for child in token.children:
                if child.type == 'image':
                    child.attrSet('loading', 'lazy')
                    child.attrSet('decoding', 'async')
    return md.renderer.render(tokens, md.options, {}), outline


def render_toc(outline):
    if not outline:
        return ''
    links = ''.join('<li class="toc-level-'+str(min(level, 3))+'"><a href="#'+html.escape(anchor, quote=True)+'">'+html.escape(title)+'</a></li>' for level, anchor, title in outline)
    return '<details class="reading-toc" open><summary>文章目录</summary><nav aria-label="文章目录"><ol>'+links+'</ol></nav></details>'
