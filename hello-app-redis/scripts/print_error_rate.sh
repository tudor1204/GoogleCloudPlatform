#!/bin/bash

TOTAL=$(cat output | wc -l);
SUCCESS=$(grep "200" output |  wc -l);
ERROR1=$(grep "000" output |  wc -l)
ERROR2=$(grep "503" output |  wc -l)
ERROR3=$(grep "500" output |  wc -l)
SUCCESS_RATE=$(($SUCCESS * 100 / TOTAL))
ERROR_RATE=$(($ERROR1 * 100 / TOTAL))
ERROR_RATE_2=$(($ERROR2 * 100 / TOTAL))
ERROR_RATE_3=$(($ERROR3 * 100 / TOTAL))
echo "Success rate: $SUCCESS/$TOTAL (${SUCCESS_RATE}%)"
echo "App network Error rate: $ERROR1/$TOTAL (${ERROR_RATE}%)"
echo "Resource Error rate: $ERROR2/$TOTAL (${ERROR_RATE_2}%)"
echo "Redis Error rate: $ERROR3/$TOTAL (${ERROR_RATE_3}%)"
