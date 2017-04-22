class Output
  def initialize(output)
    @output = output
    @output_type = output['output_type']
  end

  def rendered
    if @output_type == 'stream'
      text = @output['text'].join.delete("\n")
      "<div class='output output-text'> #{text} </div>"
    else
      as_img_html_or_text(@output['data'])
    end
  end

  private

  def as_img_html_or_text(data)
    key = (['image/png', 'text/html', 'text/plain'] & @output['data'].keys).first
    case key
    when 'image/png' then
      png = data['image/png'].strip
      "<div class='output output-image'>
      <img src='data:image/png;base64,#{png}'>
      </div>"
    else
      text = data[key].join.delete("\n")
      "<div class='output output-data'> #{text} </div>"
    end
  end
end

