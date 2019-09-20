cd ../../lib
for problem in $1/*; do
    if [ ! -d "problem" ]; then
        echo $problem
        python parse.py $problem
    fi
done
