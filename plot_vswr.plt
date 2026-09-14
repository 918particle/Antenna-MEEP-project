set terminal pdf
set output "Sept4_plot1.pdf"

set xlabel "Frequency [GHz]" font "Courier,20"
set ylabel "VSWR" font "Courier,20"

set xtics 0,2.0,20 font "Courier,20"
set ytics 0,2.0,20 font "Courier,20"

set xrange [0:18]
set yrange [0:18]

set key top right font "Courier,18" box on width 1.5 height 0.5

plot "vswr.dat" using 1:3 w l lc -1 lw 2 title "MEEP Sim", \
     "vswr_data/vswr_wide_cable_ensemble.dat" using 1:2 w l lc "#AAAAAA" lw 2 title "Lab Data"