class Cell
  def initialize(cell)
    @cell = cell
    @cell_type = cell['cell_type']
    @source = cell['source']
    @outputs = cell['outputs'] || []

    @rendered_content = []
    @rendered_output = []

    remove_hidden!
    parse!
  end

  def rendered
    [@rendered_content, @rendered_output].join("\n")
  end

  def parse!
    if frontmatter?
      @rendered_content << as_frontmatter
      return
    end

    if @cell_type == 'code'
      @rendered_content << as_code
    elsif @cell_type == 'markdown'
      @rendered_content << as_markdown
    end

    return if @source.join.include?('#hide-outputs')
    
    @outputs.each do |output|
      @rendered_output << Output.new(output).rendered
    end
  end

  def frontmatter?
    return false unless @source.any?
    @source.first[0..2] == '---' && @source.last[0..2] == '---'
  end

  def remove_hidden!
    @source = hide(@source)
  end

  def as_frontmatter
    @source.join
  end

  def as_code
    content = Pygments.highlight(@source.join, lexer: 'python')
    "<div class='cell cell-content-code'> #{content} </div>" if @source.any?
  end

  def markdown_renderer
    @@markdown_renderer ||= begin
      renderer = Redcarpet::Render::HTML.new(render_options = {})
      Redcarpet::Markdown.new(renderer, extensions = {})
    end
  end

  def as_markdown
    content = markdown_renderer.render(@source.join("\n"))
    "<div class='cell cell-content-markdown'> #{content} </div>"
  end

  private

  def hide(lines)
    return lines unless lines.include?("#hide\n")
    a = lines.index("#hide\n")
    b = lines.index("#show\n") || -1
    lines -= lines[a..b]
    hide(lines)
  end
end
