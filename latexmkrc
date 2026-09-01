$pdf_mode = 4;
$lualatex = 'lualatex -interaction=nonstopmode -file-line-error -synctex=1 %O %S';
$bibtex_use = 2;
$max_repeat = 5;
@default_files = ('main.tex');
@generated_exts = (@generated_exts, 'synctex.gz');
