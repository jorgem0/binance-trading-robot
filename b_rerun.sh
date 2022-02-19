while :
do
	if ps aux | grep '[p]ython binance_bot.py'; then

		echo $(date)
		echo "Script is still running"

	else 
	
		echo $(date)
		echo "Script stopped running, time to rerun"
		python binance_bot.py &> b_output.txt &

	fi

	sleep 30m 
done
