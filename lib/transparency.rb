require 'filewatcher'
require_relative 'notebook'

directory = '/users/wg/artsy/minotaur/analysis'

FileWatcher.new("#{directory}/**/*.ipynb").watch do |filename, event|
  puts "File #{event}: #{filename}"

  blog_filename = filename.split('/').last.chomp('.ipynb')
  full_blog_path = "source/articles/#{blog_filename}.html.markdown"

  if event == 'delete'
    File.delete(full_blog_path)
  elsif File.exist?(filename)
    File.open(full_blog_path, 'w') do |f|
      f << Notebook.new(filename).rendered
    end
  end
end
