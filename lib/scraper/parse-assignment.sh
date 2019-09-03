for problem in $1/*; do
    echo $problem
    python html_parser.py $problem
done
