# -*- coding: utf-8 -*-

import re, os
import pygments
from pygments import lexers, formatters
from jinja2 import Template
import json
import markdown

class Notebook():
    def __init__(self, path):
        print path
        self.path = path
        self.template_path = 'web/shared/template.html'
        self.web_path = 'web/' + re.match('.*/(.*).ipynb', self.path).groups()[0] + '.html'
        
    def delete(self):
        os.system('rm %s' % self.web_path)

    def save(self):
        with open(self.path, 'r') as f:
            print self.path, '  yo'
            cells = json.loads(f.read())['cells']
        body = '\n'.join(map(self.parse_lines, cells))
        with open(self.template_path, 'r') as f:
            template = Template(f.read())
        with open(self.web_path, 'w') as f:
            notebook = "<div class='notebook'>%s</div>" % body
            f.write(template.render(body=notebook).encode('utf-8'))

    def format_as_frontmatter(self, lines):
        author_re = re.compile(r"@([a-z]*)", re.MULTILINE)
        authors = author_re.findall(lines)
        authors = ''.join(map(lambda s: "<a class='frontmatter-author'>@%s</a>" % s, authors))

        keywords_re = re.compile(r"keyword\(s\): (.*)")
        keywords = keywords_re.findall(lines)[0].split(', ')
        keywords = ''.join(map(lambda s: "<a class='frontmatter-keyword'>%s</a>" % s, keywords))
        # make github handles links
        # format
        return """
            <div class='frontmatter'>
                <div class='frontmatter-authors'>
                    {authors}
                </div>
                <div class='frontmatter-keywords'>
                    {keywords}
                </div>
                <a href='#'> link to code (coming soon) </a>
            </div>
        """.format(authors=authors, keywords=keywords)

    def format_as_code(self, lines):
        return pygments.highlight(lines, lexers.PythonLexer(), pygments.formatters.HtmlFormatter())

    def format_as_markdown(self, lines):
        return markdown.markdown(lines)

    def format_as_image(self, output):
        data = output['data']['image/png']
        return "<img src='data:image/png;base64,%s'>" % data.strip()

    def format_as_data(self, output):
        data = output['data']
        if 'text/html' in data:
            key = 'text/html'
        else:
            key = 'text/plain'
        data = ''.join(data[key]).replace('\n', '').replace(u'×', 'x')
        return "<div class='output-data'>%s</div>" % data

    def format_as_text(self, output):
        data = ''.join(output['text']).replace('\n', '')
        return "<div class='output-text'>%s</div>" % data

    def format_output(self, output):
        output_type = output['output_type']
        if output_type == 'display_data':
            return self.format_as_image(output)
        elif output_type == 'stream':
            return self.format_as_text(output)
        elif output_type == 'execute_result':
            return self.format_as_data(output)

    def hide(self, lines, agg = []):
        if '#hide\n' in lines:
            if '#show\n' not in lines:
                b = lines.index('#hide\n')
                return lines[:b] + agg
            elif lines.index('#show\n'):
                a = lines.index('#hide\n')+1
                b = lines.index('#show\n')
                return self.hide(lines[b+1:], lines[a:b])
        return agg + lines

    def parse_lines(self, cell):
        parsed = []
        cell_type = cell['cell_type']
        outputs = cell['outputs'] if 'outputs' in cell else []
        source = cell['source']
        lines = ''.join(source)

        if lines[:3] == '---':
            return self.format_as_frontmatter(lines)

        if "#hide" in lines:
            source = self.hide(source)
            lines = ''.join(source)
            if lines == '':
                return''
            
        if cell_type == 'code':
            parsed.append(self.format_as_code(lines))
        elif cell_type == 'markdown':
            parsed.append(self.format_as_markdown(lines))

        if 'outputs' in cell:
            outputs = map(self.format_output, cell['outputs'])
            for output in outputs:
                parsed.append(output)

        return "<div class='cell'>" + "\n".join(parsed) + "</div>"
