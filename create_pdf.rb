#!/usr/bin/env ruby

def create_tex(src_dir)
  jpegs = Dir["#{src_dir}/*.jpg"].sort_by { |f| File.stat(f).mtime }
  # jpegs = Dir["#{src_dir}/*.jpg"].sort
  if jpegs.size == 0
    STDERR.puts "no jpegs found in #{src_dir}"
    exit
  end
  STDERR.puts(jpegs)
  cwd = File.basename(Dir.pwd)
  File.open("#{cwd}.tex", "w") do |tex|
    tex.write(<<~END_OF_TEX_HEADER)
    \\documentclass{article}
    \\usepackage{pdfpages}
    \\begin{document}
    END_OF_TEX_HEADER
    jpegs.each do |page|
      page = 
        tex.write("\\includepdf{\"#{page[0,page.size-4]}\".jpg\}\n")
    end
    tex.write(<<~END_OF_TEX_FOOTER)
    \\end{document}
    END_OF_TEX_FOOTER
  end
  "#{cwd}.tex"
end

def create_pdf(tex_file)
  STDERR.puts "output=#{tex_file}"
  exit_code = %x( pdflatex -interaction=batchmode #{tex_file} 2>&1 )
  STDERR.puts "exit code #{exit_code}"
end

def clean_up(work_dir)
  STDERR.puts "cleanup #{work_dir}"
  Dir.chdir work_dir
  Dir['*.log'].each {|f| File.delete f}
  Dir['*.aux'].each {|f| File.delete f}
  Dir['*.tex'].each {|f| File.delete f}
end

work_dir = Dir.pwd
tex = create_tex(work_dir)
pdf = create_pdf(tex)
clean_up(work_dir)

