for problem in $1/*; do
    echo $problem
    python ../../lib/html_parser.py $problem
done
