set terminal pdf
set output "August24_plot1.pdf"
set xlabel "Frequency [GHz]" font "Courier,20"
set ylabel "VSWR" font "Courier,20"
set xtics 0,2,20 font "Courier,20"
set ytics 0,2,10 font "Courier,20"
set xrange [0:20]
set yrange [0:10]
set pointsize 0.5
plot "vswr.dat" using ($1*4):2 w l lc -1 lw 2 title "MEEP sim", "vswr_lab.dat" using 1:2 w p pt 6 lc -1 title "lab data"
