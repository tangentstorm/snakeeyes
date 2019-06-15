#!/bin/sh

# Old-school continuous test suite runner for snakeeyes.
# Re-runs tests continuously, showing green bar if they pass.
# Stops and shows red bar with errors if the tests fail.

export ansi_plain="\e[0m"
export ansi_fg_yellow="\e[01;33m"
export ansi_fg_white="\e[01;37m"
export ansi_bg_red="\e[41m"
export ansi_bg_green="\e[42m"
export ansi_cls="\e[2J" # clear whole screen
export ansi_cls="\e[2J\e[;H"  # clear screen, go to top
export ansi_eol="\e[K"  # clear to end of line

cd code/snakeeyes
while [ 1 ];  do
    echo -e ${ansi_cls}
    export PAUSE=0
    python tests/__init__.py  || export PAUSE=1
    if [ "$PAUSE" = "1" ]; then
    	echo
        echo -e "${ansi_bg_red}${ansi_fg_yellow}`date` [ FAILED. ]${ansi_eol}"
        echo -e "Hit enter to continue.${ansi_eol}"
        echo -e $ansi_plain
        read
    else
        echo -e "${ansi_fg_white}${ansi_bg_green}`date` [ PASSED. ]${ansi_eol}"
        echo -e $ansi_plain
        sleep 2;
    fi
done
