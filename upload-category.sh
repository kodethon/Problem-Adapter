category=$1

if [ -e "$category" ]; then
    echo "$category does not exist!"
    exit
fi

# Export ENV variables
export $(sed -e 's/:[^:\/\/]/=/g;s/$//g;s/ *=/=/g' credentials.yml)

for problem in $category/*; do
    problem_name=$(basename -- "$problem")
    python lib/upload.py output/$problem_name
done
