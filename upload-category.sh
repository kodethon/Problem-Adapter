category=$1

if [ ! -e "$category" ]; then
    echo "$category does not exist!"
    exit
fi

# Export ENV variables
export $(sed -e 's/:[^:\/\/]/=/g;s/$//g;s/ *=/=/g' config/credentials.yml)

for problem in $category/*; do
    problem_name=$(basename -- "$problem")
    cd "output/$problem_name" && zip -r cases.zip cases > /dev/null; cd ../..
    python lib/upload.py "output/$problem_name"
done
