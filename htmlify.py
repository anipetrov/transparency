import pygments
from pygments import lexers, formatters
import json
import markdown

class Htmlify():
    def __init__(self, path):
        self.path = path
        
    def template(self):
        return """
<!DOCTYPE html>
<html>
<head>
<style>
{style}

  .highlight  {{ 
      padding: 12px; 
      margin: 12px;
      background: #f5f5f5;
      font-size: 16px;
  }}
</style>
  <title></title>
</head>
<body>
    {body}
</body>
</html>
"""

    def write_html(self):
        opts = {}
        with open(self.path, 'r') as f:
            body = json.loads(f.read())
        cells = body['cells']

        body = ''
        for cell in cells:
            body += self.parse_lines(cell)

        opts['style'] = self.style()
        opts['body'] = body
        with open('index.html', 'w') as f:
            f.write(self.template().format(**opts))

    def style(self):
        return formatters.HtmlFormatter().get_style_defs('.highlight')

    def format_as_frontmatter(self, lines):
        # make github handles links
        # format
        pass

    def format_as_code(self, lines):
        return pygments.highlight(lines, lexers.PythonLexer(), pygments.formatters.HtmlFormatter())

    def format_as_markdown(self, lines):
        return markdown.markdown(lines)

    def format_as_image(self, display):
        data = display['data']['image/png']
        return "<img src='data:image/png;base64,%s'>" % data.strip()

    def find_display_outputs(self, cell):
        if 'outputs' not in cell:
            return
        outputs = cell['outputs']
        types = enumerate(map(lambda c: c['output_type'], outputs))
        indices = map(lambda x: x[0], filter(lambda tup: tup[1] == 'display_data', types))
        return [outputs[i] for i in indices]

    def parse_lines(self, cell):
        parsed = []
        cell_type = cell['cell_type']
        outputs = cell['outputs'] if 'outputs' in cell else []
        lines = ''.join(cell['source'])
        if lines[:5] == "#hide":
            return ''
        if cell_type == 'code':
            parsed.append(self.format_as_code(lines))
        elif cell_type == 'markdown':
            parsed.append(self.format_as_markdown(lines))

        displays = self.find_display_outputs(cell)
        if displays:
            for display in displays:
                parsed.append(self.format_as_image(display))

        return "\n".join(parsed)
