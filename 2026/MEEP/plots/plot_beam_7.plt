set terminal pdf
set output "beam_7.pdf"
set bmargin 3.5
set rmargin 3.5
set lmargin 8
set xlabel "Phase Shift [deg]" font "Courier,20"
set ylabel "Beam Angle [deg]" font "Courier,20" offset -1,0
set xtics 0,20,120 font "Courier,20"
set ytics -120,20,0 font "Courier,20"
set xrange [0:120]
set yrange [-120:0]
unset key
set pointsize 0.7
plot "beam_7.dat" index 0 using ($2*180/3.14):($3*180/3.14) w p pt 7 lc -1 lw 1.5, \
"beam_7.dat" index 0 using ($2*180/3.14):(3*$5*180/3.14-87) w l lc -1 lw 1.5