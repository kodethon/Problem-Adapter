cd ../../lib
for problem in $1/*; do
    if [ ! -d "problem" ]; then
        echo $problem
        python html_parser.py $problem
    fi
done
