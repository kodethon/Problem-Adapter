category=$1
for subcategory in $category/*; do
    sh assignment.sh $subcategory
done
