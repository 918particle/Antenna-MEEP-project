set terminal pdf
set output "beam_1_and_2.pdf"
set bmargin 3.5
set rmargin 3.5
set lmargin 8
set xlabel "Phase Shift [deg]" font "Courier,20"
set ylabel "Beam Angle [deg]" font "Courier,20" offset -1,0
set xtics 0,20,120 font "Courier,20"
set ytics 0,10,60 font "Courier,20"
set xrange [0:120]
set yrange [0:65]
set key at 45,63 box on font "Courier,14" height 0.4 width 0.125 samplen 0.33
set pointsize 0.75
plot "beam_1.dat" index 0 using ($2*180/3.14):($3*180/3.14) w p pt 4 lc -1 lw 1.5 title "Beam 1, 1.20 GHz", \
"beam_1.dat" index 0 using ($2*180/3.14):($5*180/3.14) w l lc -1 lw 1.5 notitle, \
"beam_1.dat" index 1 using ($2*180/3.14):($3*180/3.14) w p pt 5 lc -1 lw 1.5 title "Beam 1, 3.60 GHz", \
"beam_1.dat" index 1 using ($2*180/3.14):($5*180/3.14) w l lc -1 lw 1.5 notitle, \
"beam_1.dat" index 2 using ($2*180/3.14):($3*180/3.14) w p pt 6 lc -1 lw 1.5 title "Beam 1, 7.20 GHz", \
"beam_1.dat" index 2 using ($2*180/3.14):($5*180/3.14) w l lc -1 lw 1.5 notitle, \
"beam_1.dat" index 3 using ($2*180/3.14):($3*180/3.14) w p pt 7 lc -1 lw 1.5 title "Beam 1, 10.8 GHz", \
"beam_1.dat" index 3 using ($2*180/3.14):($5*180/3.14) w l lc -1 lw 1.5 notitle, \
"beam_2.dat" index 0 using ($2*180/3.14):($3*180/3.14) w p pt 8 lc -1 lw 1.5 title "Beam 2, 7.20 GHz", \
"beam_2.dat" index 0 using ($2*180/3.14):($5*180/3.14+31.5) w l lc -1 lw 1.5 notitle, \
"beam_2.dat" index 1 using ($2*180/3.14):($3*180/3.14) w p pt 9 lc -1 lw 1.5 title "Beam 2, 10.8 GHz", \
"beam_2.dat" index 1 using ($2*180/3.14):($5*180/3.14+20.5) w l lc -1 lw 1.5 notitle