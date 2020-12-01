#!/bin/sh

MSG_NO="Error: Please provide a"
RET_TRUE=0
RET_FALSE=1

for arg in "$@"
do
    if [ ! -f $arg ];
    then
        echo "\033[0;31m${MSG_NO} \033[0;33m${2}\033[0m"
        exit $RET_FALSE
    fi
done
exit $RET_TRUE
