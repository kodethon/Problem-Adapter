category=$1

if [ ! -e "$category" ]; then
    echo "$category does not exist!"
    exit
fi

# Export ENV variables
#export $(sed -e 's/:[^:\/\/]/=/g;s/$//g;s/ *=/=/g' config/credentials.yml)

for problem in $category/*; do
    problem_name=$(basename -- "$problem")
    sh upload-one.sh dist/$problem_name
done
