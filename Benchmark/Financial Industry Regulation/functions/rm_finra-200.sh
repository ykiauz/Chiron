funcs=("marketdata" "lastpx" "side" "trddate" "volume")
for ((i=0;i<5;i++))
do
    faas-cli remove -f ${funcs[$i]}-200.yml
done

faas-cli deploy -f yfinance.yml