set terminal pdf
set output "beam_2.pdf"
set bmargin 3.5
set rmargin 3.5
set lmargin 8
set xlabel "Phase Shift [deg]" font "Courier,20"
set ylabel "Beam Angle [deg]" font "Courier,20" offset -1,0
set xtics 0,20,120 font "Courier,20"
set ytics 0,10,60 font "Courier,20"
set xrange [0:120]
set yrange [0:65]
unset key
set pointsize 0.7
plot "beam_2.dat" index 0 using ($2*180/3.14):($3*180/3.14) w p pt 7 lc -1 lw 1.5, \
"beam_2.dat" index 0 using ($2*180/3.14):($5*180/3.14+31.5) w l lc -1 lw 1.5, \
"beam_2.dat" index 1 using ($2*180/3.14):($3*180/3.14) w p pt 7 lc -1 lw 1.5, \
"beam_2.dat" index 1 using ($2*180/3.14):($5*180/3.14+20.5) w l lc -1 lw 1.5