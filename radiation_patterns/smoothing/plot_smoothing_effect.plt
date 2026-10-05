set terminal pdf
set key top right box on font "Courier,16" spacing 1.25
set grid
set datafile separator ","
set pointsize 1.5
set linestyle 1 pt 6 lw 1 lc -1
set linestyle 2 pt 3 lw 1 lc -1
set xrange [5:19]
set yrange [-90:-50]
set xtics font "Courier,20"
set ytics font "Courier,20"
set xlabel "Frequency [GHz]" font "Courier,20"
set ylabel "S21 [dB]" font "Courier,20" offset -2,0
set bmargin 3.5
set lmargin 9
set output "October_5th.pdf"
plot "HORN4_before_after_filing_S21.csv" using 1:2 w lp ls 1 title "Before filing", \
"HORN4_before_after_filing_S21.csv" using 1:3 w lp ls 2 title "After filing"