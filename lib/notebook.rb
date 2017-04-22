require 'json'
require 'pygments'
require 'redcarpet'

require_relative 'output'
require_relative 'cell'

class Notebook
  def initialize(path)
    raw = File.read(path)
    @json = JSON.parse(raw)
    @cells = (@json['cells'] if @json) || []
  rescue JSON::ParserError
  end

  def rendered
    return unless @cells
    @cells.map { |cell| Cell.new(cell).rendered }.join("\n")
  end
end
